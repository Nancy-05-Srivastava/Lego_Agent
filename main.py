import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from scripts.seed_repositories import seed


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🧩 LEGO.AI — Repo Discovery Agent starting up")

    # Automatically seed repositories when server starts
    logger.info("Seeding repositories...")
    await seed()
    logger.info("Repository store ready.")

    yield

    logger.info("🧩 LEGO.AI — Repo Discovery Agent shutting down")


app = FastAPI(
    title="LEGO.AI — Repo Discovery Agent",
    description=(
        "A modular AI agent that finds semantically similar GitHub repositories "
        "using embeddings. Part of the LEGO.AI multi-agent platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ✅ ADD CORS HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allows React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "agent": "RepoDiscoveryAgent"}