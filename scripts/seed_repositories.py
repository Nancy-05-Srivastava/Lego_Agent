"""
Seed Script — Pre-populate the Repo Discovery Store
=====================================================
Fetches READMEs and generates embeddings for a curated set of repositories
so the agent has a meaningful index to search against.

Usage:
    python scripts/seed_repositories.py

Note: This script runs the FastAPI app in-process so that the seeded data
is available when the server starts. For a persistent store, swap the
in-memory store in similarity_service.py with a vector database.
"""

import asyncio
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agents.repo_discovery_agent import repo_discovery_agent
from app.services.similarity_service import store_size

# ── Curated seed list ──────────────────────────────────────────────────────
# Add any GitHub repos you want indexed here.
SEED_REPOSITORIES = [
    # Web frameworks
    "https://github.com/django/django",
    "https://github.com/pallets/flask",
    # AI / ML
    "https://github.com/huggingface/transformers",
    "https://github.com/openai/openai-python",
    "https://github.com/microsoft/autogen",
    "https://github.com/microsoft/semantic-kernel",
    "https://github.com/langchain-ai/langchain",
    # Dev tools
    "https://github.com/microsoft/vscode",
    "https://github.com/github/copilot-docs",
    # Infrastructure
    "https://github.com/kubernetes/kubernetes",
    "https://github.com/docker/compose",
]


async def seed():
    print(f"\n🧩 LEGO.AI — Seeding {len(SEED_REPOSITORIES)} repositories...\n")

    success, failed = 0, 0

    for url in SEED_REPOSITORIES:
        try:
            record = await repo_discovery_agent.index_repository(url)
            print(f"  ✅  {record.name:<40} | {url}")
            success += 1
        except Exception as e:
            print(f"  ❌  FAILED: {url}")
            print(f"       Reason: {e}")
            failed += 1

    print(f"\n{'─' * 60}")
    print(f"  Seeded:  {success} repositories")
    print(f"  Failed:  {failed} repositories")
    print(f"  Store size: {store_size()}")
    print(f"{'─' * 60}\n")

    if success == 0:
        print("⚠️  No repositories were seeded. Check your .env credentials.")
        sys.exit(1)

    print("✅  Seed complete. Start the server with: uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(seed())
