
# 🧩 LEGO.AI — Multi-Agent Developer Assistant

**LEGO.AI** is a modular **multi-agent AI system** designed to help developers transform ideas into production-ready software faster.

Inspired by LEGO blocks, each AI agent performs a specialized task and can be combined with others to create a powerful developer workflow.

This project demonstrates how multiple AI agents can collaborate to assist developers with:

- 🔎 Discovering relevant GitHub repositories
- ⚡ Optimizing and improving code
- 🌍 Finding hackathons and opportunities to implement ideas

---

# 🚀 Features

## 🔎 Repo Discovery Agent
Finds **similar GitHub repositories** using semantic similarity of README files.

Capabilities:
- Extract README from a repository
- Generate embeddings
- Find semantically similar repositories
- Help developers discover reusable codebases

---

## ⚡ Code Optimization Agent
Analyzes user code and suggests improvements.

Capabilities:
- Detect inefficient coding patterns
- Perform AST-based static analysis
- Identify potential errors
- Auto-format code using PEP8 standards

---

## 🌍 Opportunity Finder Agent
Helps developers **discover hackathons and competitions** related to their ideas.

Capabilities:
- Extract keywords using Azure Language Service
- Generate relevant search queries
- Search the internet for hackathons and coding competitions

---

# 🧠 System Architecture

```

```
            User Input
                 │
                 ▼
          LEGO Agent API
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
```

Repo Discovery   Code Optimizer   Opportunity Finder
Agent             Agent            Agent
│                │               │
└────────────┬───────────────┘
▼
Combined AI Response

```

Each agent functions independently and can be extended or replaced without affecting the system — just like LEGO blocks.

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|--------|
| FastAPI | API framework |
| Azure Language Service | Keyword extraction |
| Sentence Transformers | Semantic embeddings |
| DuckDuckGo Search (DDGS) | Internet search for opportunities |
| Python AST | Static code analysis |
| Pyflakes & Autopep8 | Error detection and formatting |

---

# 📂 Project Structure

```

Lego_Agent
│
├── app
│   ├── agents
│   │   ├── repo_discovery_agent.py
│   │   ├── opportunity_agent.py
│   │   └── code_optimizer_agent.py
│   │
│   ├── api
│   │   └── routes.py
│   │
│   └── services
│
├── scripts
│   └── seed_repositories.py
│
├── main.py
├── requirements.txt
└── README.md

```

---

# ⚙️ Installation

Clone the repository

```

git clone [https://github.com/Nancy-05-Srivastava/Lego_Agent.git](https://github.com/Nancy-05-Srivastava/Lego_Agent.git)
cd Lego_Agent

```

Install dependencies

```

pip install -r requirements.txt

```

---

# ▶️ Running the Project

Start the FastAPI server:

```

uvicorn main:app --reload

```

Open the interactive API documentation:

```

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

```

---

# 📡 API Endpoints

| Endpoint | Description |
|--------|-------------|
| `/api/discover` | Discover similar GitHub repositories |
| `/api/optimize-code` | Analyze and optimize code |
| `/api/find-opportunities` | Find hackathons and competitions |
| `/api/lego-agent` | Run all agents together |

---

# 🧪 Example Request

```

POST /api/lego-agent

````

Example input:

```json
{
 "repo_url": "https://github.com/django/django",
 "code": "for i in range(len(arr)): print(arr[i])",
 "idea": "AI system for crop disease detection"
}
````

---

# 💡 Why LEGO.AI?

Developers often lose productive time due to:

* Searching for relevant codebases
* Understanding unfamiliar repositories
* Improving code quality
* Finding platforms to implement ideas

LEGO.AI reduces this friction by **automating discovery, optimization, and opportunity exploration through AI agents**.

---

# 🔮 Future Improvements

* Integrate Azure OpenAI for intelligent code suggestions
* Use Azure AI Search for scalable vector search
* Deploy agents as independent microservices
* Integrate with GitHub Copilot Extensions


