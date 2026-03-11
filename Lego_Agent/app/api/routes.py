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

    try:

        loop = asyncio.get_running_loop()

        # Run Repo discovery (async)
        repo_task = asyncio.create_task(
            repo_discovery_agent.run(request.repo_url)
        )

        # Run optimizer
        optimizer_task = loop.run_in_executor(
            None,
            optimize_code,
            request.code
        )

        # Run opportunity agent
        opportunity_task = loop.run_in_executor(
            None,
            opportunity_agent,
            request.idea
        )

        repo_result = await repo_task
        suggestions, errors, optimized = await optimizer_task
        opportunities = await opportunity_task

        return {
            "repo_discovery": repo_result,
            "code_optimization": {
                "suggestions": suggestions,
                "errors": errors,
                "optimized_code": optimized
            },
            "opportunities": opportunities
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))