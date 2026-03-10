from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

# Agent imports
from app.agents.repo_discovery_agent import repo_discovery_agent
from app.agents.code_optimizer_agent import optimize_code
from app.agents.opportunity_agent import run as opportunity_agent

router = APIRouter(prefix="/api", tags=["LEGO Agents"])

# -----------------------------
# Request Models
# -----------------------------

class RepoRequest(BaseModel):
    repo_url: str

class CodeRequest(BaseModel):
    code: str

class IdeaRequest(BaseModel):
    idea: str

class LegoRequest(BaseModel):
    repo_url: str
    code: str
    idea: str

class CodeDiscoverRequest(BaseModel):
    user_input: str           # raw code snippet OR plain-English description
    language_hint: str = ""   # optional: "python", "javascript", etc.
    top_repos: int = 3        # how many similar repos to mine
    max_blocks: int = 8       # max code blocks to return


# -----------------------------
# Agent 1 — Repo Discovery
# -----------------------------

@router.post("/discover")
async def discover_repositories(request: RepoRequest):
    try:
        result = await repo_discovery_agent.run(request.repo_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Agent 1b — Code Block Discovery  ← NEW
# -----------------------------

@router.post("/discover/code")
async def discover_code_blocks(request: CodeDiscoverRequest):
    """
    User pastes code / describes an algorithm → returns ranked,
    copy-pasteable LEGO code blocks extracted from similar repositories.

    Example request:
        {
          "user_input": "def flood_fill(grid, row, col, color): ...",
          "language_hint": "python",
          "top_repos": 3,
          "max_blocks": 6
        }
    """
    try:
        result = await repo_discovery_agent.run_code_discovery(
            user_input=request.user_input,
            language_hint=request.language_hint,
            top_repos=request.top_repos,
            max_blocks=request.max_blocks,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Agent 3 — Code Optimizer
# -----------------------------

@router.post("/optimize-code")
async def optimize_user_code(request: CodeRequest):
    loop = asyncio.get_running_loop()
    suggestions, errors, optimized = await loop.run_in_executor(
        None,
        optimize_code,
        request.code
    )
    return {
        "suggestions": suggestions,
        "errors": errors,
        "optimized_code": optimized
    }


# -----------------------------
# Agent 2 — Opportunity Finder
# -----------------------------

@router.post("/find-opportunities")
async def find_opportunities(request: IdeaRequest):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        opportunity_agent,
        request.idea
    )
    return result


# -----------------------------
# Master LEGO Agent
# Runs all agents together
# -----------------------------

@router.post("/lego-agent")
async def run_lego_agents(request: LegoRequest):
    """
    Orchestrates all agents in parallel:
      - Repo Discovery   (similar repos by URL)
      - Code Discovery   (LEGO code blocks from the user's code) 
      - Code Optimizer
      - Opportunity Finder
    """
    try:
        loop = asyncio.get_running_loop()

        # Async tasks (native coroutines)
        repo_task         = asyncio.create_task(repo_discovery_agent.run(request.repo_url))
        code_blocks_task  = asyncio.create_task(                           
            repo_discovery_agent.run_code_discovery(
                user_input=request.code,
                max_blocks=5,
            )
        )

        # Sync agents wrapped in executor
        optimizer_task    = loop.run_in_executor(None, optimize_code, request.code)
        opportunity_task  = loop.run_in_executor(None, opportunity_agent, request.idea)

        # Await all concurrently
        repo_result, code_blocks_result, optimizer_result, opportunities = await asyncio.gather(
            repo_task,
            code_blocks_task,
            optimizer_task,
            opportunity_task,
        )

        suggestions, errors, optimized = optimizer_result

        return {
            "repo_discovery": repo_result,
            "code_blocks": code_blocks_result,         
            "code_optimization": {
                "suggestions": suggestions,
                "errors": errors,
                "optimized_code": optimized,
            },
            "opportunities": opportunities,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
