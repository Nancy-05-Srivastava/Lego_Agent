from pydantic import BaseModel, field_validator


class DiscoverRequest(BaseModel):
    repo_url: str

    @field_validator("repo_url")
    @classmethod
    def must_be_github_url(cls, v: str) -> str:
        if "github.com" not in v:
            raise ValueError("Only GitHub repository URLs are supported.")
        return v.rstrip("/")


class SimilarRepository(BaseModel):
    url: str
    name: str
    similarity_score: float
    description: str
    stars: int


class DiscoverResponse(BaseModel):
    query_repo: str
    similar_repositories: list[SimilarRepository]


class RepoRecord(BaseModel):
    """Internal record stored in the in-memory repository store."""
    url: str
    name: str
    description: str
    stars: int = 0
    embedding: list[float]


class RepoNotFoundError(Exception):
    """Raised when a GitHub repository or its README cannot be located."""
