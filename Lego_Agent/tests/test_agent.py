"""
Unit tests for the Repo Discovery Agent.
Run with: pytest tests/
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.agents.repo_discovery_agent import RepoDiscoveryAgent
from app.models.schemas import RepoRecord, RepoNotFoundError
from app.services import similarity_service


# ── Fixtures ───────────────────────────────────────────────────────────────

FAKE_EMBEDDING_DIM = 8


def make_embedding(seed: float) -> list[float]:
    """Create a deterministic, normalised fake embedding."""
    import math
    base = [math.cos(seed + i) for i in range(FAKE_EMBEDDING_DIM)]
    norm = sum(x ** 2 for x in base) ** 0.5
    return [x / norm for x in base]


def make_record(i: int) -> RepoRecord:
    return RepoRecord(
        url=f"https://github.com/seed/repo{i}",
        name=f"repo{i}",
        description=f"Seed repo {i}",
        stars=i * 100,
        embedding=make_embedding(float(i)),
    )


@pytest.fixture(autouse=True)
def clear_store():
    similarity_service._repo_store.clear()
    yield
    similarity_service._repo_store.clear()


@pytest.fixture
def agent() -> RepoDiscoveryAgent:
    return RepoDiscoveryAgent()


# ── GitHub Service Tests ───────────────────────────────────────────────────

def test_parse_owner_repo_standard():
    from app.services.github_service import _parse_owner_repo
    owner, repo = _parse_owner_repo("https://github.com/tiangolo/fastapi")
    assert owner == "tiangolo"
    assert repo == "fastapi"


def test_parse_owner_repo_with_git_suffix():
    from app.services.github_service import _parse_owner_repo
    _, repo = _parse_owner_repo("https://github.com/owner/myrepo.git")
    assert repo == "myrepo"


def test_parse_owner_repo_invalid():
    from app.services.github_service import _parse_owner_repo
    with pytest.raises(ValueError, match="Cannot parse"):
        _parse_owner_repo("https://notgithub.com/owner/repo")


# ── Schema Tests ───────────────────────────────────────────────────────────

def test_repo_record_has_stars():
    r = make_record(5)
    assert r.stars == 500


def test_similar_repository_has_stars():
    from app.models.schemas import SimilarRepository
    s = SimilarRepository(
        url="https://github.com/x/y", name="y",
        similarity_score=0.9, description="desc", stars=42
    )
    assert s.stars == 42


# ── Similarity Service Tests ───────────────────────────────────────────────

def test_add_and_retrieve_repo():
    similarity_service.add_repo_to_store(make_record(1))
    assert similarity_service.store_size() == 1


def test_no_duplicate_urls():
    r = make_record(1)
    similarity_service.add_repo_to_store(r)
    similarity_service.add_repo_to_store(r)
    assert similarity_service.store_size() == 1


def test_cosine_similarity_identical():
    from app.services.similarity_service import _cosine_similarity
    vec = make_embedding(1.0)
    assert abs(_cosine_similarity(vec, vec) - 1.0) < 1e-5


def test_cosine_similarity_orthogonal():
    from app.services.similarity_service import _cosine_similarity
    a = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert abs(_cosine_similarity(a, b)) < 1e-5


def test_cosine_similarity_bounded():
    from app.services.similarity_service import _cosine_similarity
    for i in range(5):
        score = _cosine_similarity(make_embedding(float(i)), make_embedding(float(i + 1)))
        assert -1.0 <= score <= 1.0


def test_find_similar_returns_top_5():
    for i in range(10):
        similarity_service.add_repo_to_store(make_record(i))
    results = similarity_service.find_similar_repositories(make_embedding(0.05))
    assert len(results) <= 5


def test_find_similar_sorted_descending():
    for i in range(8):
        similarity_service.add_repo_to_store(make_record(i))
    results = similarity_service.find_similar_repositories(make_embedding(0.5))
    scores = [r.similarity_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_find_similar_excludes_query_url():
    url = "https://github.com/test/query-repo"
    similarity_service.add_repo_to_store(
        RepoRecord(url=url, name="q", description="", stars=0, embedding=make_embedding(0.0))
    )
    results = similarity_service.find_similar_repositories(make_embedding(0.0), exclude_url=url)
    assert all(r.url != url for r in results)


def test_find_similar_includes_stars():
    similarity_service.add_repo_to_store(make_record(7))  # stars=700
    results = similarity_service.find_similar_repositories(make_embedding(7.0))
    assert results[0].stars == 700


# ── Agent Integration Tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_returns_results(agent):
    for i in range(5):
        similarity_service.add_repo_to_store(make_record(i))

    with patch(
        "app.agents.repo_discovery_agent.github_service.fetch_readme",
        new_callable=AsyncMock,
        return_value="# FastAPI\nA modern web framework.",
    ), patch(
        "app.agents.repo_discovery_agent.embedding_service.generate_embedding",
        new_callable=AsyncMock,
        return_value=make_embedding(0.5),
    ):
        response = await agent.run("https://github.com/tiangolo/fastapi")

    assert response.query_repo == "https://github.com/tiangolo/fastapi"
    assert len(response.similar_repositories) <= 5
    scores = [r.similarity_score for r in response.similar_repositories]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_run_raises_repo_not_found(agent):
    """run() must propagate RepoNotFoundError — no silent fallback."""
    with patch(
        "app.agents.repo_discovery_agent.github_service.fetch_readme",
        new_callable=AsyncMock,
        side_effect=RepoNotFoundError("Repository not found: https://github.com/ghost/ghost"),
    ):
        with pytest.raises(RepoNotFoundError):
            await agent.run("https://github.com/ghost/ghost")


@pytest.mark.asyncio
async def test_run_raises_runtime_on_embedding_failure(agent):
    """run() wraps unexpected embedding errors in RuntimeError."""
    with patch(
        "app.agents.repo_discovery_agent.github_service.fetch_readme",
        new_callable=AsyncMock,
        return_value="Some readme content",
    ), patch(
        "app.agents.repo_discovery_agent.embedding_service.generate_embedding",
        new_callable=AsyncMock,
        side_effect=Exception("Azure quota exceeded"),
    ):
        with pytest.raises(RuntimeError, match="Embedding failed"):
            await agent.run("https://github.com/tiangolo/fastapi")


@pytest.mark.asyncio
async def test_index_repository_stores_stars(agent):
    with patch(
        "app.agents.repo_discovery_agent.github_service.fetch_readme",
        new_callable=AsyncMock,
        return_value="# Some readme",
    ), patch(
        "app.agents.repo_discovery_agent.github_service.fetch_repo_metadata",
        new_callable=AsyncMock,
        return_value={
            "name": "testrepo",
            "full_name": "owner/testrepo",
            "description": "A test repo",
            "stars": 9999,
        },
    ), patch(
        "app.agents.repo_discovery_agent.embedding_service.generate_embedding",
        new_callable=AsyncMock,
        return_value=make_embedding(1.0),
    ):
        record = await agent.index_repository("https://github.com/owner/testrepo")

    assert record.stars == 9999
    assert similarity_service.store_size() == 1
