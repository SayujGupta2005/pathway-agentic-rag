# Agentic RAG — Intelligent API Automation via RAG-Powered Tool Retrieval

**Author Info:** Sayuj Gupta

Computer Science & Engineering

---

An intelligent **agentic Retrieval-Augmented Generation (RAG) AI assistant** that connects large language models to third-party APIs through **RAG-powered endpoint retrieval**. This project enables LLMs to handle complex, multi-step workflows by intelligently selecting and executing the right API endpoints based on natural language queries — powered by a **real-time vector store** with hybrid retrieval.

---

## System Design & Architecture

### Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) — High-performance async web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — Database ORM (SQLite)
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [Docker](https://www.docker.com/) — Containerized deployment

**RAG & Generative AI:**
- [DSPy](https://dspy-docs.vercel.app/) — Programming framework for LLM-based agents & signatures
- **Vector Store Pipeline** — Real-time document indexing with hybrid retrieval (KNN + BM25)
- [Gemini Embedder](https://ai.google.dev/) — Embedding generation via Google Gemini (`gemini-embedding-001`)
- [LiteLLM](https://github.com/BerriAI/litellm) — Unified LLM API layer (Groq, OpenAI, Cohere, Ollama support)
- [LangChain](https://www.langchain.com/) — Vector store client interface & document abstractions
- [Unstructured](https://unstructured.io/) — Document parsing & ingestion (PDFs, tables, images)
- [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) — Web search fallback

**Frontend:**
- [Next.js 14](https://nextjs.org/) — React framework (App Router)
- [Shadcn UI](https://ui.shadcn.com/) — Component library (Radix UI primitives)
- [Tailwind CSS](https://tailwindcss.com/) — Utility-first styling
- [Framer Motion](https://www.framer.com/motion/) — Animations & transitions

---

## How It Works

### RAG-Powered Tool Calling

Traditional tool calling approaches fail when dealing with large numbers of API endpoints. Modern APIs often have **100+ endpoints**, but LLMs can only reliably handle **30–40 tools** simultaneously. This project uses **Retrieval-Augmented Generation (RAG)** to intelligently select the most relevant endpoints before execution, powered by a real-time vector store with hybrid retrieval.

### Connecting a Platform

#### Method 1: OpenAPI Spec Available

When a platform provides OpenAPI documentation:

1. **Ingestion:** The OpenAPI spec is uploaded via the `/upload/upload_openapi` endpoint. The system parses the spec and extracts:
   - Endpoint URLs, descriptions, and HTTP methods
   - Request parameter schemas and body schemas
   - Response schemas (resolved from `$ref` references)

2. **Documentation Splitting:** Each endpoint's description is saved as an individual text file, organized by route path, enabling fine-grained retrieval.

3. **Vector Indexing:** The `DocumentStore` reads the documentation files, splits them using `TokenCountSplitter` (512 tokens), and indexes them using:
   - **KNN (Brute Force)** with Gemini embeddings
   - **BM25 (Tantivy)** for keyword-based retrieval
   - A **Hybrid Index** combining both for optimal retrieval accuracy

4. **Real-Time Updates:** The reactive pipeline automatically re-indexes when source documentation files change — no manual re-ingestion needed.

#### Method 2: No OpenAPI Spec Available

When OpenAPI documentation isn't available:

1. **Custom Wrapper:** Build a FastAPI wrapper around the platform's API
2. **Auto-Generated Spec:** FastAPI automatically generates OpenAPI documentation for the wrapper
3. **Standard Ingestion:** The generated spec follows the same ingestion process as Method 1

---

## Multi-Agent Query Execution Pipeline

The system orchestrates **7+ specialized DSPy agents**, each with a distinct role in the pipeline:

### Agent Architecture

| Agent | Role | DSPy Signature |
|-------|------|----------------|
| **Query Rephraser** | Normalizes user queries into succinct, API-documentation-friendly statements | `QueryRephraseSignature` |
| **Endpoint Filterer** | Selects the single most relevant endpoint from retrieved documentation | `ArrayAnswerSignature` |
| **Action Decider** | Determines if the query requires computation beyond simple data retrieval | `QueryActionSignature` |
| **Request Generator** | Extracts request parameters and body from the query based on endpoint schemas | `RequestSchemaGeneratorSignature` |
| **Code Generator** | Generates Python code for computational queries (aggregations, transformations) | `ComputeQuery` |
| **Response Generator** | Synthesizes API responses into natural language answers | `GenerateResponse` |
| **Follow-Up Generator** | Suggests 3 related actions the user might want to perform next | `FollowUpSignature` |

### Execution Flow

```
User Query
    │
    ▼
┌─────────────────────┐
│  Query Rephraser    │  ← Normalize slang, improve retrieval quality
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Vector            │  ← Similarity search (top-k=3) against
│  Store Retrieval    │    indexed API documentation
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Endpoint Filterer  │  ← LLM-based filtering to select optimal endpoint
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Request Generator  │  ← Generate request params/body from query + schema
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Action Decider     │  ← Does query need computation or just retrieval?
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
 Retrieval   Computation
    │           │
    │     ┌─────┴─────┐
    │     │ Code Gen  │  ← Generate & execute Python code
    │     └─────┬─────┘
    │           │
    ▼           ▼
┌─────────────────────┐
│  Response Generator │  ← Synthesize final natural language response
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Follow-Up Generator │  ← Suggest related next actions
└─────────────────────┘
```

### Approval Workflow

Certain endpoints (e.g., placing orders, posting reviews, modifying carts) are flagged for **user approval** before execution — preventing unintended state-changing actions.

---

## Design Choices & Differentiation

### Why RAG Over Traditional Tool Calling?

- **Scalability:** Traditional tool calling hits reliability limits around 30–40 tools. RAG enables connection to **hundreds of endpoints** by retrieving only the relevant ones.

- **Cost Efficiency:** Instead of passing all available tools to the LLM context, RAG retrieves only the **top-k most relevant endpoints**, dramatically reducing token consumption.

- **Reliability:** RAG-based selection is more reliable than asking LLMs to choose from hundreds of options simultaneously.

### Why a Hybrid Vector Store?

- **Real-Time Indexing:** The reactive pipeline **automatically re-indexes** when documentation changes — no manual re-ingestion needed.
- **Hybrid Retrieval:** Built-in support for combining **dense (KNN) + sparse (BM25)** retrieval strategies for superior accuracy.
- **Production-Ready:** A battle-tested `DocumentStoreServer` with built-in statistics, filtering, and metadata support.

### Advantages Over MCP (Model Context Protocol)

- **Token Efficiency:** MCP servers hosting hundreds of tools must pass all tools to the LLM context, causing massive token consumption. Our RAG approach reduces this by **10–100x**.

- **Loop Prevention:** MCPs frequently get stuck in infinite loops when dealing with complex tool selections. Our filtered, pipeline-based approach prevents this.

- **Cost Effectiveness:** Significantly lower operational costs due to reduced token usage and more efficient execution paths.

### DSPy-Powered Agent Design

Unlike raw prompt engineering, each agent uses **DSPy Signatures** with structured Pydantic input/output models. This provides:
- **Type-safe** agent communication
- **Reproducible** outputs via constrained generation
- **Pluggable LLM backends** (Groq Llama 3.3, Gemini, GPT-4o, Cohere, Ollama)
- **Built-in logging** with cost, token, and latency tracking per agent

---

## Evaluation Framework

The project includes a retrieval evaluation suite measuring:

| Metric | Description |
|--------|-------------|
| **Context Precision** | Fraction of retrieved endpoints that are correct |
| **Context Recall** | Fraction of correct endpoints that were retrieved |
| **F1 Score** | Harmonic mean of precision and recall |
| **Accuracy Score** | Exact-match accuracy across test queries |

Evaluations are run against a curated CSV dataset of queries with ground-truth endpoint mappings.

---

## Project Structure

```
Agentic-RAG/
├── agentic_rag/                    # Backend
│   ├── app.py                      # FastAPI application entry point
│   ├── constants.py                # Configuration & API keys
│   ├── retrieval_server.py         # Vector store server
│   ├── dspy_agents.py              # Agent definitions & logger
│   ├── models.py                   # SQLAlchemy models (User, Query)
│   ├── utils.py                    # Utility functions (Gemini, schema parsing)
│   ├── ytoj.py                     # YAML to JSON converter
│   ├── routes/
│   │   ├── query.py                # Query execution pipeline endpoints
│   │   └── uploads.py              # OpenAPI spec ingestion endpoints
│   ├── dspy_schemas/               # DSPy agent signatures
│   │   ├── rephraser_schema.py     # Query rephrasing
│   │   ├── endpoints_array_schema.py # Endpoint selection
│   │   ├── action_schema.py        # Action decision
│   │   ├── request_schema_agent.py # Request generation
│   │   ├── code_generator_schema.py # Code generation
│   │   ├── response_generator.py   # Response synthesis
│   │   ├── follow_up.py            # Follow-up suggestions
│   │   └── context_qa_schema.py    # Context-based QA
│   ├── extensions/
│   │   ├── pathway_client.py       # LangChain vector store client
│   │   ├── parser.py               # Document parsing (Unstructured)
│   │   ├── prompt.py               # Gemini prompt agent
│   │   ├── web.py                  # DuckDuckGo web search
│   │   └── tool_factory.py         # API endpoint tool factory
│   ├── evaluation/
│   │   └── eval.py                 # Retrieval evaluation metrics
│   ├── data/                       # Parsed schemas & data
│   ├── documentations/             # Indexed documentation files
│   ├── dockerfile                  # Docker configuration
│   └── requirements.txt            # Python dependencies
├── frontend/                       # Frontend
│   ├── app/
│   │   ├── page.tsx                # Landing page (animated)
│   │   ├── layout.tsx              # Root layout
│   │   └── app/
│   │       ├── page.tsx            # Main chat application
│   │       └── tools/              # Tools page
│   ├── components/
│   │   ├── chat/
│   │   │   ├── Chat.tsx            # Core chat interface
│   │   │   ├── MessageList.tsx     # Message rendering
│   │   │   ├── MessageInput.tsx    # User input component
│   │   │   ├── MetricsDialog.tsx   # Agent metrics display
│   │   │   └── APIDetailModal.tsx  # API details modal
│   │   ├── navbar.tsx              # Navigation bar
│   │   ├── LLMSelector.tsx         # LLM model selector
│   │   ├── openapi/                # OpenAPI viewer
│   │   ├── analytics/              # Analytics dashboard
│   │   └── ui/                     # Shadcn UI components (18 components)
│   ├── package.json
│   └── tailwind.config.ts
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop (recommended)
- API Keys:
  - Gemini API Key
  - (Optional) Groq / OpenAI / Cohere API Key

### Quick Setup (Docker — Recommended)

1. **Build the Docker Image:**

   ```bash
   cd agentic_rag
   docker build -t agentic-rag .
   ```

2. **Open in Dev Container:**
   - Install VS Code extensions: **Docker** and **Dev Containers**
   - Press `Ctrl+Shift+P` → `Dev Containers: Reopen in Container`

3. **Configure API Keys:**
   - Edit `constants.py` with your `GEMINI_API_KEY`
   - In `dspy_agents.py`, set your preferred LLM and its API key

4. **Start the Retrieval Server:**

   ```bash
   python retrieval_server.py
   ```

5. **Start the API Server** (new terminal):

   ```bash
   uvicorn app:app --reload --port 5000
   ```

6. **Access the API docs:**

   ```
   http://localhost:5000/docs
   ```

### Manual Setup (Without Docker)

1. **Clone and Install:**

   ```bash
   git clone <repository-url>
   cd agentic_rag
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   # or venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   pip install uvicorn
   ```

2. **Configure Environment:**
   - Edit `constants.py` with your API keys

3. **Start Services:**

   ```bash
   # Terminal 1: Retrieval Server
   python retrieval_server.py

   # Terminal 2: API Server
   uvicorn app:app --reload --port 5000
   ```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## API Usage

### Upload OpenAPI Spec

```bash
curl -X POST "http://localhost:5000/upload/upload_openapi" \
  -F "file=@openapi.json"
```

### Execute a Query

```bash
curl -X POST "http://localhost:5000/query/retrieve?API_BASE=http://127.0.0.1:8000&query=Show%20me%20my%20recent%20orders" \
  -H "Content-Type: application/json" \
  -d '{
    "Authorization": "Bearer your_token_here"
  }'
```

### View Query Metrics

```bash
curl "http://localhost:5000/query/metrics?index=0"
```

Response includes per-agent token usage, cost, latency, and retrieved endpoints.

### View API Documentation

```bash
curl "http://localhost:5000/api_docs"
```

---

## Social Impact

### Productivity Enhancement

According to ProcessMaker research, knowledge workers waste **1.5–4.6 hours per week** on manual copy-paste and ticketing tasks. By automating these mundane activities, we enable:

- **Productivity Gains:** Redirect focus toward high-value, creative, and strategic work
- **Job Satisfaction:** Reduce repetitive tasks that lead to burnout
- **Organizational Growth:** Enable teams to focus on innovation rather than manual processes
- **Efficiency Improvements:** Streamline workflows across multiple platforms and tools

### Automation Benefits

- **Error Reduction:** Eliminate human errors in repetitive tasks
- **Consistency:** Ensure standardized processes across teams
- **Scalability:** Handle increasing workloads without proportional staff increases
- **Integration:** Seamlessly connect disparate tools and platforms via a single natural language interface

---

