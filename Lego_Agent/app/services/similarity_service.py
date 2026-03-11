import numpy as np
from app.models.schemas import RepoRecord, SimilarRepository
from app.core.config import settings


# ---------------------------------------------------------------------------
# In-Memory Repository Vector Store
# In production, swap this with a vector DB (e.g. Azure AI Search, Qdrant).
# ---------------------------------------------------------------------------

_repo_store: list[RepoRecord] = []


def add_repo_to_store(record: RepoRecord) -> None:
    """Add or update a repository record in the in-memory store."""
    # Avoid duplicates: remove existing entry for same URL
    global _repo_store
    _repo_store = [r for r in _repo_store if r.url != record.url]
    _repo_store.append(record)


def get_store() -> list[RepoRecord]:
    return _repo_store


def store_size() -> int:
    return len(_repo_store)


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------

def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def find_similar_repositories(
    query_embedding: list[float],
    exclude_url: str | None = None,
) -> list[SimilarRepository]:
    """
    Compare the query embedding against all stored repositories and return
    the top-K most similar ones sorted by descending cosine similarity.

    Args:
        query_embedding: Embedding vector for the query repository.
        exclude_url:     URL to exclude from results (the query repo itself).

    Returns:
        List of SimilarRepository, sorted by similarity (highest first).
    """
    if not _repo_store:
        return []

    scored: list[tuple[float, RepoRecord]] = []

    for record in _repo_store:
        if exclude_url and record.url == exclude_url:
            continue

        score = _cosine_similarity(query_embedding, record.embedding)

        if score >= settings.min_similarity_threshold:
            scored.append((score, record))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)

    top_k = scored[: settings.top_k]

    return [
        SimilarRepository(
            url=record.url,
            name=record.name,
            similarity_score=round(score, 4),
            description=record.description,
            stars=record.stars,
        )
        for score, record in top_k
    ]