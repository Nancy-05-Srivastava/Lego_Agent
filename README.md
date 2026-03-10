# 🧩 LEGO.AI — Repo Discovery Agent

Find semantically similar GitHub repositories using Azure OpenAI embeddings.

---

## 📁 Folder Structure

```
repo_discovery_agent/
├── app/
│   ├── agents/
│   │   └── repo_discovery_agent.py   # Orchestrates the discovery pipeline
│   ├── services/
│   │   ├── github_service.py         # Fetches README from GitHub API
│   │   ├── embedding_service.py      # Generates embeddings via Azure OpenAI
│   │   └── similarity_service.py     # Computes cosine similarity + ranking
│   ├── models/
│   │   └── schemas.py                # Pydantic request/response models
│   ├── api/
│   │   └── routes.py                 # FastAPI route definitions
│   └── core/
│       └── config.py                 # Environment config (Azure, GitHub keys)
├── scripts/
│   └── seed_repositories.py          # Pre-populate the repo store with embeddings
├── tests/
│   └── test_agent.py                 # Unit tests
├── .env.example                      # Environment variable template
├── requirements.txt
└── main.py                           # FastAPI app entry point
```

---

## ⚙️ Prerequisites

- Python 3.10+
- Azure OpenAI resource with a deployed `text-embedding-ada-002` model
- GitHub Personal Access Token (for higher API rate limits)

---

## 🚀 Setup & Run

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd repo_discovery_agent
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual keys
```

### 3. Seed the repository store

This pre-fetches READMEs and generates embeddings for a set of known repositories:

```bash
python scripts/seed_repositories.py
```

### 4. Start the API server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Test the endpoint

```bash
curl -X POST "http://localhost:8000/api/discover" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/tiangolo/fastapi"}'
```

Or open the interactive docs at: **http://localhost:8000/docs**

---

## 📡 API Reference

### `POST /api/discover`

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo"
}
```

**Response:**
```json
{
  "query_repo": "https://github.com/owner/repo",
  "similar_repositories": [
    {
      "url": "https://github.com/...",
      "name": "repo-name",
      "similarity_score": 0.94,
      "description": "..."
    }
  ]
}
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | e.g. `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | Embedding deployment name (e.g. `text-embedding-ada-002`) |
| `AZURE_OPENAI_API_VERSION` | e.g. `2024-02-01` |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
