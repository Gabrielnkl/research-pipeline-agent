# 🔬 Research Pipeline Agent

A production-ready multi-agent research pipeline with **Human-in-the-Loop (HITL)** review. Submit a research question, watch specialist AI agents decompose it, search the web, fact-check findings, and pause for your approval before generating a final structured report.

Built with **LangGraph · FastAPI · Next.js · PostgreSQL · Redis**.

---

## ✨ Features

- **Multi-Agent Orchestration** — An orchestrator decomposes your question into subtasks and delegates to specialist agents (Web Search, Summarizer, Fact Checker, Report Writer)
- **Human-in-the-Loop** — The pipeline pauses at low-confidence results and waits for human approval or rejection before continuing
- **Stateful & Resumable** — Full graph state is persisted to PostgreSQL, so jobs survive restarts and can be resumed from any HTTP request
- **Live Agent Trace** — The frontend polls job status and shows each completed pipeline step in real time
- **Structured Reports** — Final output is a markdown report with Executive Summary, Findings by Subtask, Flagged Claims, and Sources

---

## 🏗️ Architecture

```
User (Next.js)
    │
    ▼
FastAPI REST API
    │
    ├── POST /research/start        → Starts a new research job
    ├── GET  /research/{id}/status  → Polls job state
    ├── POST /research/{id}/approve → Human approves/rejects a checkpoint
    └── GET  /research/{id}/report  → Returns final report
    │
    ▼
LangGraph State Machine
    │
    ├── [Node] Orchestrator         → Decomposes question into subtasks
    ├── [Node] Web Search Agent     → Searches for sources (Tavily)
    ├── [Node] Summarizer Agent     → Condenses findings per subtask
    ├── [Node] Fact Checker Agent   → Flags low-confidence claims
    ├── [Node] HITL Checkpoint      → Pauses, waits for human input
    └── [Node] Report Writer        → Synthesizes final structured report
    │
    ▼
PostgreSQL (job state + checkpointer) · Redis (task queue)
```

---

## 🗂️ Project Structure

```
research-pipeline-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── api/
│   │   │   └── routes.py            # REST endpoints
│   │   ├── agents/
│   │   │   ├── orchestrator.py      # Decomposes research question
│   │   │   ├── web_search.py        # Searches web, returns raw sources
│   │   │   ├── summarizer.py        # Summarizes per subtask
│   │   │   ├── fact_checker.py      # Scores confidence, flags claims
│   │   │   └── report_writer.py     # Final report synthesis
│   │   ├── graph/
│   │   │   ├── state.py             # LangGraph TypedDict state schema
│   │   │   ├── pipeline.py          # Graph definition + edge logic
│   │   │   └── checkpointer.py      # PostgreSQL-backed checkpointer
│   │   ├── db/
│   │   │   ├── postgres.py          # Async DB connection + queries
│   │   │   └── models.py            # SQLAlchemy models
│   │   ├── services/
│   │   │   └── job_service.py       # Business logic for job management
│   │   └── schemas/
│   │       └── research.py          # Pydantic request/response models
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Home — start a new research job
│   │   └── research/[id]/
│   │       ├── page.tsx             # Job status + live agent trace
│   │       └── review/page.tsx      # HITL review screen
│   ├── components/
│   │   ├── ResearchForm.tsx         # Input form
│   │   ├── AgentTrace.tsx           # Live step-by-step agent log
│   │   ├── HITLPanel.tsx            # Approve / reject checkpoint UI
│   │   ├── ReportViewer.tsx         # Final report display
│   │   └── StatusBadge.tsx          # Job status indicator
│   ├── lib/
│   │   └── api.ts                   # Typed API client
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Tavily API key](https://tavily.com) (free tier available)

### 1. Clone the repo

```bash
git clone https://github.com/Gabrielnkl/research-pipeline-agent.git
cd research-pipeline-agent
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=research_user
POSTGRES_PASSWORD=research_pass
POSTGRES_DB=research_db

REDIS_HOST=localhost
REDIS_PORT=6379

FRONTEND_URL=http://localhost:3000
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start all services

```bash
docker compose up --build
```

This starts the FastAPI backend, PostgreSQL, and Redis together.

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧠 How It Works

1. **Submit** — Enter a research question in the UI
2. **Orchestrate** — The orchestrator agent decomposes it into 3–5 subtasks
3. **Search** — The web search agent queries Tavily for each subtask
4. **Summarize** — The summarizer condenses findings with source citations
5. **Fact Check** — The fact checker scores confidence and flags uncertain claims
6. **HITL Review** — If confidence is low or claims are flagged, the pipeline pauses and prompts you to approve or reject with feedback
7. **Report** — The report writer synthesizes everything into a structured markdown report

---

## 🛠️ Tech Stack

| Layer         | Technology                              |
|---------------|-----------------------------------------|
| Agent orchestration | LangGraph                         |
| Backend API   | FastAPI + Uvicorn                       |
| Frontend      | Next.js 14 (App Router) + Tailwind CSS  |
| Database      | PostgreSQL (state + checkpointer)       |
| Task queue    | Redis                                   |
| AI model      | OpenAI GPT                              |
| Web search    | Tavily API                              |
| Containerization | Docker Compose                       |

---

## 🔑 Environment Variables

| Variable            | Description                          |
|---------------------|--------------------------------------|
| `OPENAI_API_KEY`    | OpenAI API key                       |
| `TAVILY_API_KEY`    | Tavily search API key                |
| `POSTGRES_HOST`     | PostgreSQL host                      |
| `POSTGRES_PORT`     | PostgreSQL port (default: `5432`)    |
| `POSTGRES_USER`     | PostgreSQL username                  |
| `POSTGRES_PASSWORD` | PostgreSQL password                  |
| `POSTGRES_DB`       | PostgreSQL database name             |
| `REDIS_HOST`        | Redis host                           |
| `REDIS_PORT`        | Redis port (default: `6379`)         |
| `FRONTEND_URL`      | Frontend URL for CORS                |

---

## 💡 Key Design Decisions

**Why LangGraph over a simple chain?**
LangGraph's stateful graph allows execution to be paused, serialized, and resumed — essential for HITL. A standard LangChain chain can't be interrupted mid-run and resumed from a different HTTP request.

**Why PostgreSQL as the checkpointer?**
In-memory checkpointers die when the process restarts. PostgreSQL ensures job state survives crashes and deploys, making the pipeline production-grade.

**Why the conditional edge on confidence score?**
Not every research job needs human review. Routing only uncertain results to HITL reduces friction for clear-cut questions while maintaining quality control on ambiguous ones.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a pull request

---

## 📄 License

This project is open source. See [LICENSE](LICENSE) for details.