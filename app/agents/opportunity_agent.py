# app/agents/opportunity_agent.py
import os
import requests
from ddgs import DDGS

# Read Azure credentials (match what you put in .env)
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")  # e.g. https://lego-openai.services.ai.azure.com
AZURE_KEY = os.getenv("AZURE_KEY")


def extract_keywords(text: str):
    """
    Uses Azure Language key-phrase extraction.
    Falls through to a simple fallback if Azure fails.
    """
    if AZURE_ENDPOINT and AZURE_KEY:
        url = AZURE_ENDPOINT.rstrip("/") + "/language/:analyze-text?api-version=2023-04-01"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "kind": "KeyPhraseExtraction",
            "analysisInput": {"documents": [{"id": "1", "language": "en", "text": text}]},
        }
        try:
            r = requests.post(url, headers=headers, json=data, timeout=15)
            r.raise_for_status()
            result = r.json()
            return result["results"]["documents"][0]["keyPhrases"]
        except Exception:
            # fallback to simple split-based keywords if Azure not available
            pass

    # Simple fallback: pick top words (very naive)
    words = [w.lower() for w in text.split() if len(w) > 3]
    # return top unique words
    seen = set()
    out = []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
        if len(out) >= 6:
            break
    return out


def generate_queries(keywords):
    queries = []
    for keyword in keywords:
        queries.append(f"{keyword} hackathon")
        queries.append(f"{keyword} AI competition")
        queries.append(f"{keyword} coding challenge")
    return queries


def search_hackathons_online(queries, max_per_query: int = 3):
    results = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                search_results = ddgs.text(query, max_results=max_per_query)
            except Exception:
                continue
            for r in search_results:
                results.append({"query": query, "title": r.get("title"), "link": r.get("href")})
    return results


def run(idea: str):
    """
    Main entrypoint for the Opportunity Agent.
    Returns a dict with keywords and search results.
    """
    keywords = extract_keywords(idea)
    queries = generate_queries(keywords)
    results = search_hackathons_online(queries)
    return {"keywords": keywords, "queries": queries, "opportunities": results}