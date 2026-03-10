"""
RepoDiscoveryAgent
===============================
Original pipeline:
  Step 1 — Fetch README from GitHub
  Step 2 — Generate embedding via Azure OpenAI
  Step 3 — Cosine similarity search
  Step 4 — Return top-5 similar repositories
  Step 5 — Fetch source files from top repos via GitHub API
  Step 6 — Parse & extract functions / classes (AST for Python, regex for others)
  Step 7 — Rank extracted blocks by relevance using Azure OpenAI
  Step 8 — Return ready-to-use LEGO code blocks with applications & research refs
"""

import ast
import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx
from openai import AsyncAzureOpenAI

from app.services import github_service, embedding_service, similarity_service
from app.models.schemas import (
    DiscoverResponse,
    RepoRecord,
    SimilarRepository,
    RepoNotFoundError,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# New response schemas for the code-block pipeline
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CodeBlock:
    """A single reusable LEGO code block extracted from a repository."""
    name: str                        # function / class name
    kind: str                        # "function" | "class" | "module"
    source_repo: str                 # GitHub repo URL
    source_file: str                 # path inside the repo  e.g. src/algo/flood.py
    source_url: str                  # direct GitHub link to the file
    code: str                        # full copy-pasteable source
    language: str                    # "python" | "javascript" | "java" | ...
    relevance_score: float = 0.0     # 0-1, set by ranker
    summary: str = ""                # one-line AI summary
    suggested_applications: list[str] = field(default_factory=list)
    related_papers: list[str] = field(default_factory=list)


@dataclass
class CodeDiscoverResponse:
    """Full response for the enhanced code-discovery pipeline."""
    query: str                                  # original user input
    similar_repositories: list[SimilarRepository] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    pipeline_time_seconds: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Language detection helper
# ─────────────────────────────────────────────────────────────────────────────

_EXT_TO_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".cpp": "cpp", ".c": "c", ".go": "go",
    ".rs": "rust", ".rb": "ruby", ".cs": "csharp", ".kt": "kotlin",
}

def _detect_language(filename: str) -> str:
    for ext, lang in _EXT_TO_LANG.items():
        if filename.endswith(ext):
            return lang
    return "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# AST-based Python parser
# ─────────────────────────────────────────────────────────────────────────────

def _extract_python_blocks(source: str, filepath: str, repo_url: str) -> list[dict]:
    """
    Use Python's AST to extract every top-level function and class
    with its full source text.
    """
    blocks = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return blocks

    lines = source.splitlines()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        # Only top-level or one level deep (methods inside classes excluded
        # to avoid duplicates — the whole class is already captured)
        if not isinstance(node, ast.ClassDef) and any(
            isinstance(p, ast.ClassDef)
            for p in ast.walk(tree)
            if hasattr(p, "body") and node in getattr(p, "body", [])
        ):
            continue

        start = node.lineno - 1
        end   = node.end_lineno  # Python 3.8+
        code  = "\n".join(lines[start:end])
        kind  = "class" if isinstance(node, ast.ClassDef) else "function"

        blocks.append({
            "name": node.name,
            "kind": kind,
            "code": code,
            "language": "python",
            "source_file": filepath,
            "source_repo": repo_url,
            "source_url": f"{repo_url}/blob/main/{filepath}",
        })

    return blocks


# ─────────────────────────────────────────────────────────────────────────────
# Regex-based parser for non-Python languages
# ─────────────────────────────────────────────────────────────────────────────

# Patterns: (language, kind, regex)
_GENERIC_PATTERNS = [
    # JavaScript / TypeScript functions
    ("js_ts", "function",
     re.compile(
         r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{",
         re.MULTILINE,
     )),
    # Arrow functions assigned to const
    ("js_ts", "function",
     re.compile(
         r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>",
         re.MULTILINE,
     )),
    # Java / C# / Kotlin methods
    ("java_like", "function",
     re.compile(
         r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{",
         re.MULTILINE,
     )),
    # C / C++ functions
    ("c_cpp", "function",
     re.compile(
         r"^[\w\s\*]+\s+(\w+)\s*\([^)]*\)\s*\{",
         re.MULTILINE,
     )),
    # Classes (generic)
    ("generic", "class",
     re.compile(
         r"(?:export\s+)?class\s+(\w+)",
         re.MULTILINE,
     )),
]

def _extract_generic_blocks(source: str, filepath: str,
                             repo_url: str, language: str) -> list[dict]:
    """
    Extract named functions/classes from non-Python files using regex.
    Grabs up to 60 lines after the signature as the body.
    """
    blocks = []
    lines  = source.splitlines()

    for _, kind, pattern in _GENERIC_PATTERNS:
        for m in pattern.finditer(source):
            name      = m.group(1)
            line_no   = source[:m.start()].count("\n")
            end_line  = min(line_no + 60, len(lines))
            code      = "\n".join(lines[line_no:end_line])
            blocks.append({
                "name": name,
                "kind": kind,
                "code": code,
                "language": language,
                "source_file": filepath,
                "source_repo": repo_url,
                "source_url": f"{repo_url}/blob/main/{filepath}",
            })

    # Deduplicate by name
    seen, unique = set(), []
    for b in blocks:
        if b["name"] not in seen:
            seen.add(b["name"])
            unique.append(b)
    return unique


# ─────────────────────────────────────────────────────────────────────────────
# GitHub file fetcher
# ─────────────────────────────────────────────────────────────────────────────

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", "vendor",
              "venv", ".venv", "test", "tests", "docs", "examples"}
_MAX_FILES_PER_REPO = 12     # keep API usage low
_MAX_FILE_BYTES     = 80_000 # skip huge files

async def _fetch_repo_source_files(
    repo_url: str,
    token: str,
    language_hint: str = "",
) -> list[tuple[str, str, str]]:
    """
    Walk the GitHub repo tree and download source files.
    Returns list of (filepath, content, language).
    """
    # Parse owner/repo from URL
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        # Get default branch
        meta_r = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}", headers=headers
        )
        meta_r.raise_for_status()
        default_branch = meta_r.json().get("default_branch", "main")

        # Get full file tree (recursive)
        tree_r = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/"
            f"{default_branch}?recursive=1",
            headers=headers,
        )
        tree_r.raise_for_status()
        tree = tree_r.json().get("tree", [])

        # Filter to source files only
        wanted_exts = set(_EXT_TO_LANG.keys())
        candidates = []
        for item in tree:
            if item.get("type") != "blob":
                continue
            path = item["path"]
            # Skip noise directories
            if any(skip in path.split("/") for skip in _SKIP_DIRS):
                continue
            ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
            if ext not in wanted_exts:
                continue
            # Prefer files matching language hint
            lang = _detect_language(path)
            priority = 0 if (language_hint and lang == language_hint) else 1
            candidates.append((priority, item.get("size", 0), path, lang))

        # Sort: language match first, then smallest files (faster to fetch)
        candidates.sort(key=lambda x: (x[0], x[1]))
        candidates = candidates[:_MAX_FILES_PER_REPO]

        # Fetch file contents in parallel
        async def fetch_file(path: str) -> tuple[str, str] | None:
            url = (f"https://raw.githubusercontent.com/{owner}/{repo}/"
                   f"{default_branch}/{path}")
            r = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            if r.status_code != 200 or len(r.content) > _MAX_FILE_BYTES:
                return None
            return path, r.text

        tasks   = [fetch_file(c[2]) for c in candidates]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        files = []
        for item, res in zip(candidates, results):
            if isinstance(res, tuple):
                path, content = res
                files.append((path, content, item[3]))  # (path, content, lang)

    return files


# ─────────────────────────────────────────────────────────────────────────────
# Main agent class
# ─────────────────────────────────────────────────────────────────────────────

class RepoDiscoveryAgent:
    """
    Modular LEGO.AI agent block for repository similarity discovery
    AND reusable code-block extraction.

    Public interface
    ----------------
    await agent.run(repo_url)                    → DiscoverResponse        (original)
    await agent.run_code_discovery(user_input)   → CodeDiscoverResponse    (NEW)
    await agent.index_repository(url)            → RepoRecord              (seed script)
    """

    def __init__(self, azure_client: AsyncAzureOpenAI, github_token: str,
                 deployment: str = "gpt-4o-mini"):
        self._llm      = azure_client
        self._gh_token = github_token
        self._deploy   = deployment

    async def run(self, repo_url: str) -> DiscoverResponse:
      """
        Given a GitHub repository URL, discover the top-5 most similar
        repositories using README embeddings and cosine similarity.
        Args:
            repo_url: Full GitHub URL, e.g. https://github.com/owner/repo
        Returns:
            DiscoverResponse with up to 5 repositories sorted by similarity score.
        Raises:
            RepoNotFoundError: If the repository or its README does not exist.
            RuntimeError: On unexpected failures during embedding or search.
        """
        t_start = time.perf_counter()
        logger.info(f"[RepoDiscoveryAgent] run() ▶  {repo_url}")

        readme_text     = await self._step_fetch_readme(repo_url)
        query_embedding = await self._step_generate_embedding(readme_text, repo_url)
        similar_repos   = self._step_search(query_embedding, exclude_url=repo_url)

        elapsed = time.perf_counter() - t_start
        logger.info(f"[Step 4] ✅ {len(similar_repos)} result(s) | {elapsed:.2f}s")

        return DiscoverResponse(
            query_repo=repo_url,
            similar_repositories=similar_repos,
        )

    async def index_repository(self, repo_url: str) -> RepoRecord:
        """
        Index a repository: fetch README + metadata, generate embedding,
        and persist to the similarity store.
        Args:
            repo_url: Full GitHub URL.
        Returns:
            The created RepoRecord (with stars included).
        Raises:
            RepoNotFoundError: If the repository does not exist on GitHub.
        """
        logger.info(f"[RepoDiscoveryAgent] Indexing: {repo_url}")
        readme_text = await self._step_fetch_readme(repo_url)
        meta        = await github_service.fetch_repo_metadata(repo_url)
        embedding   = await self._step_generate_embedding(readme_text, repo_url)

        record = RepoRecord(
            url=repo_url,
            name=meta["name"],
            description=meta["description"],
            stars=meta["stars"],
            embedding=embedding,
        )
        similarity_service.add_repo_to_store(record)
        logger.info(f"[RepoDiscoveryAgent] Indexed ✅  {meta['full_name']}  (⭐ {meta['stars']:,})")
        return record

    async def run_code_discovery(
        self,
        user_input: str,
        language_hint: str = "",
        top_repos: int = 3,
        max_blocks: int = 8,
    ) -> CodeDiscoverResponse:
        """
        Full pipeline: user pastes code / describes an algorithm / gives a repo URL
        → returns ready-to-use LEGO code blocks ranked by relevance.

        Args:
            user_input:    Raw code snippet, algorithm description, or GitHub URL.
            language_hint: e.g. "python", "javascript" — speeds up file filtering.
            top_repos:     How many similar repos to mine for code blocks (default 3).
            max_blocks:    Maximum code blocks to return (default 8).

        Returns:
            CodeDiscoverResponse
        """
        t_start = time.perf_counter()
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("[RepoDiscoveryAgent] run_code_discovery() ▶")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # ── Step 1-3: Semantic search (reuse existing pipeline) ───────────────
        similar_repos = await self._step_semantic_search(user_input)
        target_repos  = [r.url for r in similar_repos[:top_repos]]

        logger.info(f"[Step 5] Mining code from {len(target_repos)} repo(s)…")

        # ── Step 5: Fetch source files from top repos ─────────────────────────
        raw_blocks: list[dict] = []
        fetch_tasks = [
            _fetch_repo_source_files(url, self._gh_token, language_hint)
            for url in target_repos
        ]
        repo_file_lists = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for repo_url, file_list in zip(target_repos, repo_file_lists):
            if isinstance(file_list, Exception):
                logger.warning(f"[Step 5] ✖ Failed to fetch files from {repo_url}: {file_list}")
                continue
            for filepath, content, language in file_list:
                if language == "python":
                    blocks = _extract_python_blocks(content, filepath, repo_url)
                else:
                    blocks = _extract_generic_blocks(content, filepath, repo_url, language)
                raw_blocks.extend(blocks)

        logger.info(f"[Step 6] ✅ Extracted {len(raw_blocks)} raw code block(s)")

        # ── Step 7: Rank blocks with Azure OpenAI ─────────────────────────────
        ranked_blocks = await self._step_rank_blocks(user_input, raw_blocks, max_blocks)

        elapsed = time.perf_counter() - t_start
        logger.info(f"[Step 8] ✅ Returning {len(ranked_blocks)} ranked block(s) | {elapsed:.2f}s")

        return CodeDiscoverResponse(
            query=user_input,
            similar_repositories=similar_repos,
            code_blocks=ranked_blocks,
            pipeline_time_seconds=round(elapsed, 2),
        )

    # ── Step helpers ──────────────────────────────────────────────────────────

    async def _step_semantic_search(self, user_input: str) -> list[SimilarRepository]:
        """Steps 1-3 unified: embed the user input and search the vector store."""
        logger.info("[Step 1-3] Semantic search for similar repositories…")
        embedding = await self._step_generate_embedding(user_input, "user_input")
        return self._step_search(embedding)

    async def _step_rank_blocks(
        self,
        user_input: str,
        raw_blocks: list[dict],
        max_blocks: int,
    ) -> list[CodeBlock]:
        """
        Step 7 — Send block names + signatures to Azure OpenAI for relevance ranking.
        Then enrich the top-N with summaries, applications, and paper references.
        """
        if not raw_blocks:
            return []

        logger.info(f"[Step 7] Ranking {len(raw_blocks)} block(s) via LLM…")

        # Build a compact index: "idx | name | kind | language | first 3 lines"
        index_lines = []
        for i, b in enumerate(raw_blocks):
            preview = b["code"].splitlines()[0][:120]
            index_lines.append(f"{i:03d} | {b['name']} | {b['kind']} | {b['language']} | {preview}")
        index_text = "\n".join(index_lines)

        rank_prompt = f"""You are LEGO.AI's code relevance ranker.

User query / code:
\"\"\"
{user_input[:1500]}
\"\"\"

Below is an indexed list of extracted code blocks from similar repositories.
Format: idx | name | kind | language | first_line

{index_text}

Task:
1. Select the {max_blocks} most relevant and REUSABLE blocks for the user's use-case.
2. For each selected block, provide:
   - "idx": the 3-digit index number (string)
   - "score": relevance score 0.0-1.0
   - "summary": one-sentence plain-English description
   - "applications": list of 2-3 concrete application ideas (e.g. "Maze solver", "Game pathfinding")
   - "papers": list of 1-2 related research paper titles (real ones if known, otherwise omit)

Respond ONLY with a JSON array. No markdown fences. Example:
[{{"idx":"003","score":0.95,"summary":"BFS traversal...","applications":["..."],"papers":["..."]}}]
"""

        import json, re as _re

        try:
            resp = await self._llm.chat.completions.create(
                model=self._deploy,
                messages=[{"role": "user", "content": rank_prompt}],
                max_tokens=1200,
                temperature=0.1,
            )
            raw = resp.choices[0].message.content.strip()
            raw = _re.sub(r"```json|```", "", raw).strip()
            rankings: list[dict] = json.loads(raw)
        except Exception as exc:
            logger.error(f"[Step 7] ✖ LLM ranking failed: {exc}. Falling back to first {max_blocks}.")
            rankings = [{"idx": f"{i:03d}", "score": 0.5, "summary": "",
                         "applications": [], "papers": []}
                        for i in range(min(max_blocks, len(raw_blocks)))]

        # Build final CodeBlock objects
        result: list[CodeBlock] = []
        for r in rankings:
            try:
                idx = int(r["idx"])
                b   = raw_blocks[idx]
            except (KeyError, IndexError, ValueError):
                continue

            result.append(CodeBlock(
                name                  = b["name"],
                kind                  = b["kind"],
                source_repo           = b["source_repo"],
                source_file           = b["source_file"],
                source_url            = b["source_url"],
                code                  = b["code"],
                language              = b["language"],
                relevance_score       = float(r.get("score", 0.5)),
                summary               = r.get("summary", ""),
                suggested_applications= r.get("applications", []),
                related_papers        = r.get("papers", []),
            ))

        result.sort(key=lambda x: x.relevance_score, reverse=True)
        return result

    # ── Shared step implementations (original, unchanged) ─────────────────────

    async def _step_fetch_readme(self, repo_url: str) -> str:
        logger.info(f"[Step 1] Fetching README…  ({repo_url})")
        t = time.perf_counter()
        try:
            readme = await github_service.fetch_readme(repo_url)
        except RepoNotFoundError:
            logger.error(f"[Step 1] ✖ Not found: {repo_url}")
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch README for {repo_url}: {exc}") from exc
        logger.info(f"[Step 1] ✅ README fetched ({len(readme):,} chars | {time.perf_counter()-t:.2f}s)")
        return readme

    async def _step_generate_embedding(self, text: str, source_url: str) -> list[float]:
        logger.info("[Step 2] Generating embedding…")
        t = time.perf_counter()
        try:
            embedding = await embedding_service.generate_embedding(text)
        except Exception as exc:
            raise RuntimeError(f"Embedding failed for {source_url}: {exc}") from exc
        logger.info(f"[Step 2] ✅ dim={len(embedding)} | {time.perf_counter()-t:.2f}s")
        return embedding

    def _step_search(self, query_embedding: list[float],
                     exclude_url: str | None = None) -> list[SimilarRepository]:
        logger.info(f"[Step 3] Cosine search across {similarity_service.store_size()} repo(s)…")
        t = time.perf_counter()
        results = similarity_service.find_similar_repositories(
            query_embedding=query_embedding, exclude_url=exclude_url
        )
        logger.info(f"[Step 3] ✅ {len(results)} match(es) | {time.perf_counter()-t:.3f}s")
        if results:
            for i, r in enumerate(results, 1):
                logger.info(f"         {i}. {r.name:<35} score={r.similarity_score:.4f}  ⭐ {r.stars:,}")
        return results


# Singleton instance
repo_discovery_agent = RepoDiscoveryAgent(
    azure_client=AsyncAzureOpenAI(
        azure_endpoint=__import__("os").getenv("AZURE_OPENAI_ENDPOINT", ""),
        api_key=__import__("os").getenv("AZURE_OPENAI_API_KEY", ""),
        api_version=__import__("os").getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    ),
    github_token=__import__("os").getenv("GITHUB_TOKEN", ""),
    deployment=__import__("os").getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
)
