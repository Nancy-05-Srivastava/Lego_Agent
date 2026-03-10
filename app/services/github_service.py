import base64
import re
import httpx
from app.core.config import settings
from app.models.schemas import RepoNotFoundError
from app.core.config import settings
print("GitHub token:", settings.github_token)
GITHUB_API_BASE = "https://api.github.com"


def _parse_owner_repo(repo_url: str) -> tuple[str, str]:
    """Extract owner and repo name from a GitHub URL."""
    match = re.search(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?$", repo_url)

    if not match:
        raise ValueError(f"Cannot parse GitHub URL: {repo_url}")

    return match.group(1), match.group(2)


def _build_headers() -> dict:
    """
    Build GitHub API headers.
    Uses token authentication to avoid rate limits.
    """

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    # Add GitHub token if available
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    return headers


async def fetch_readme(repo_url: str) -> str:
    """
    Fetch and decode README content from GitHub.
    """

    owner, repo = _parse_owner_repo(repo_url)

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=_build_headers())

    if response.status_code == 404:
        raise RepoNotFoundError(
            f"Repository not found or has no README: {repo_url}"
        )

    if response.status_code == 403:
        raise Exception(
            "GitHub API rate limit exceeded. Check GITHUB_TOKEN."
        )

    response.raise_for_status()

    data = response.json()

    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")

    # Limit size to avoid embedding token overflow
    return content[:8000]


async def fetch_repo_metadata(repo_url: str) -> dict:
    """
    Fetch repository metadata.
    """

    owner, repo = _parse_owner_repo(repo_url)

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, headers=_build_headers())

    if response.status_code == 404:
        raise RepoNotFoundError(f"Repository not found: {repo_url}")

    if response.status_code == 403:
        raise Exception(
            "GitHub API rate limit exceeded. Check GITHUB_TOKEN."
        )

    response.raise_for_status()

    data = response.json()

    description = data.get("description") or ""
    topics = data.get("topics", [])

    if topics:
        description += f" Topics: {', '.join(topics)}"

    return {
        "name": data.get("name", repo),
        "full_name": data.get("full_name", f"{owner}/{repo}"),
        "description": description,
        "stars": data.get("stargazers_count", 0),
    }