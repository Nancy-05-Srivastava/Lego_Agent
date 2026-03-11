"""
RepoDiscoveryAgent
==================
Orchestrates the four-step pipeline for finding similar repositories:

  Step 1 — Fetch README from GitHub
  Step 2 — Generate embedding via Azure OpenAI
  Step 3 — Compute cosine similarity against stored repo embeddings
  Step 4 — Return top-5 similar repositories sorted by score
"""

import logging
import time
from app.services import github_service, embedding_service, similarity_service
from app.models.schemas import DiscoverResponse, RepoRecord, SimilarRepository, RepoNotFoundError

logger = logging.getLogger(__name__)


class RepoDiscoveryAgent:
    """
    Modular LEGO.AI agent block for repository similarity discovery.

    Public interface
    ----------------
    await agent.run(repo_url)          → DiscoverResponse   (primary entry point)
    await agent.index_repository(url)  → RepoRecord         (used by seed script)
    """

    # ── Primary public entry point ────────────────────────────────────────

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
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"[RepoDiscoveryAgent] run() ▶  {repo_url}")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # ── Step 1: Fetch README ──────────────────────────────────────────
        readme_text = await self._step_fetch_readme(repo_url)

        # ── Step 2: Generate embedding ───────────────────────────────────
        query_embedding = await self._step_generate_embedding(readme_text, repo_url)

        # ── Step 3: Cosine similarity search ─────────────────────────────
        similar_repos = self._step_search(query_embedding, exclude_url=repo_url)

        # ── Step 4: Return top-5 sorted results ──────────────────────────
        elapsed = time.perf_counter() - t_start
        logger.info(
            f"[Step 4] ✅ Returning {len(similar_repos)} result(s) "
            f"| total time: {elapsed:.2f}s"
        )

        return DiscoverResponse(
            query_repo=repo_url,
            similar_repositories=similar_repos,
        )

    # ── Indexing (used by seed script) ────────────────────────────────────

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

        # Fetch README and metadata in parallel for efficiency
        readme_text = await self._step_fetch_readme(repo_url)
        meta = await github_service.fetch_repo_metadata(repo_url)
        embedding = await self._step_generate_embedding(readme_text, repo_url)

        record = RepoRecord(
            url=repo_url,
            name=meta["name"],
            description=meta["description"],
            stars=meta["stars"],
            embedding=embedding,
        )
        similarity_service.add_repo_to_store(record)
        logger.info(
            f"[RepoDiscoveryAgent] Indexed ✅  {meta['full_name']}  "
            f"(⭐ {meta['stars']:,})"
        )
        return record

    # ── Step implementations ──────────────────────────────────────────────

    async def _step_fetch_readme(self, repo_url: str) -> str:
        """
        Step 1 — Fetch README content from GitHub.
        Raises RepoNotFoundError if the repo or README is missing.
        """
        logger.info(f"[Step 1] Fetching README from GitHub…  ({repo_url})")
        t = time.perf_counter()

        try:
            readme = await github_service.fetch_readme(repo_url)
        except RepoNotFoundError:
            logger.error(f"[Step 1] ✖ Repository not found: {repo_url}")
            raise
        except Exception as exc:
            logger.error(f"[Step 1] ✖ Unexpected error fetching README: {exc}")
            raise RuntimeError(f"Failed to fetch README for {repo_url}: {exc}") from exc

        logger.info(
            f"[Step 1] ✅ README fetched  "
            f"({len(readme):,} chars | {time.perf_counter() - t:.2f}s)"
        )
        return readme

    async def _step_generate_embedding(self, text: str, source_url: str) -> list[float]:
        """
        Step 2 — Generate an embedding vector via Azure OpenAI.
        """
        logger.info("[Step 2] Generating embedding via Azure OpenAI…")
        t = time.perf_counter()

        try:
            embedding = await embedding_service.generate_embedding(text)
        except Exception as exc:
            logger.error(f"[Step 2] ✖ Embedding generation failed: {exc}")
            raise RuntimeError(f"Embedding failed for {source_url}: {exc}") from exc

        logger.info(
            f"[Step 2] ✅ Embedding generated  "
            f"(dim={len(embedding)} | {time.perf_counter() - t:.2f}s)"
        )
        return embedding

    def _step_search(
        self,
        query_embedding: list[float],
        exclude_url: str | None = None,
    ) -> list[SimilarRepository]:
        """
        Step 3 — Compute cosine similarity and return top-5 sorted results.
        """
        store_count = similarity_service.store_size()
        logger.info(
            f"[Step 3] Computing cosine similarity across "
            f"{store_count} indexed repo(s)…"
        )
        t = time.perf_counter()

        results = similarity_service.find_similar_repositories(
            query_embedding=query_embedding,
            exclude_url=exclude_url,
        )

        logger.info(
            f"[Step 3] ✅ Similarity search complete  "
            f"({len(results)} match(es) | {time.perf_counter() - t:.3f}s)"
        )

        if results:
            logger.info("[Step 3] Top results:")
            for i, r in enumerate(results, 1):
                logger.info(
                    f"         {i}. {r.name:<35} "
                    f"score={r.similarity_score:.4f}  ⭐ {r.stars:,}"
                )

        return results


# Singleton instance — shared across all requests
repo_discovery_agent = RepoDiscoveryAgent()
