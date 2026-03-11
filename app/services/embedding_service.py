"""
Local Embedding Service
Replaces Azure OpenAI embeddings with a local SentenceTransformer model.
"""

from sentence_transformers import SentenceTransformer
import asyncio

# Load the embedding model once
_model = SentenceTransformer("all-MiniLM-L6-v2")


async def generate_embedding(text: str) -> list[float]:
    """
    Generate a semantic embedding vector for the given text locally.

    Args:
        text: The input text (e.g., README content).

    Returns:
        A list of floats representing the embedding vector.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    loop = asyncio.get_event_loop()

    embedding = await loop.run_in_executor(
        None,
        lambda: _model.encode(text, normalize_embeddings=True).tolist()
    )

    return embedding


async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts locally.

    Args:
        texts: List of input strings.

    Returns:
        List of embedding vectors.
    """

    if not texts:
        return []

    loop = asyncio.get_event_loop()

    embeddings = await loop.run_in_executor(
        None,
        lambda: _model.encode(texts, normalize_embeddings=True).tolist()
    )

    return embeddings