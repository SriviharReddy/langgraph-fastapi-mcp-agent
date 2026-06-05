# News & Weather Agent (FastAPI + LangGraph + FastMCP)

A production-grade, modular asynchronous web application that integrates a **LangGraph** conversational agent with custom external tools using the **Model Context Protocol (MCP)** via **FastMCP**. It is built on top of **FastAPI** and uses **PostgreSQL** for persistent conversational checkpoints (thread history).

---

## Architecture Overview

The system is split into two independent, lightweight services following a microservice-ish pattern:

```mermaid
graph TD
    Client[Client / test_client.py] -->|POST /chat| MainApp[Main Chat Server :8001]
    MainApp -->|Postgres Checkpointer| DB[(PostgreSQL :5442)]
    MainApp -->|Fetch & Call Tools via SSE| MCPServer[MCP Tool Server :8000]
    MCPServer -->|Weather API| AccuWeather[AccuWeather API]
    MCPServer -->|News API| NewsAPI[NewsAPI.org]
```

### Key Components:
1. **MCP Tool Server (`mcp_server/`)**: A FastMCP server exposing local Python functions as standardized MCP tools (weather fetching and news queries).
2. **Main Application (`main.py`)**: A FastAPI app hosting the LangGraph agent workflow. It connects to the database pool, connects to the MCP client, and serves the SSE streaming routes.
3. **Agent Graph (`agent/`)**: The LangGraph workflow. It utilizes `ChatDeepSeek` to route requests to MCP tools dynamically using a single-node cycle design.
4. **API Router (`api/`)**: Exposes a `POST /chat` streaming endpoint that returns a Server-Sent Events (SSE) token stream.
5. **Database Checkpointer**: Uses `AsyncPostgresSaver` backed by a production-ready `AsyncConnectionPool` to persist thread state dynamically.

---

## Project Structure

```text
├── agent/                  # LangGraph agent setup
│   ├── graph.py            # Graph construction and compilation
│   ├── nodes.py            # LLM node execution
│   └── tools.py            # MCP client setup (MultiServerMCPClient)
├── api/                    # FastAPI routes & schemas
│   ├── routes.py           # SSE stream routing (/chat)
│   └── schema.py           # Pydantic input models
├── integrations/           # Third-party integrations
│   ├── news_api.py         # NewsAPI Client
│   └── weather_api.py      # AccuWeather Client
├── mcp_server/             # FastMCP Server
│   ├── server.py           # FastAPI wrapper mounting FastMCP
│   └── tools.py            # Registered MCP tool definitions
├── config.py               # Settings (Pydantic BaseSettings)
├── docker-compose.yml      # PostgreSQL container setup
├── main.py                 # Main application entry point
├── pyproject.toml          # Project metadata and dependencies
├── test_client.py          # Real-time SSE stream test client
└── uv.lock                 # Lockfile (managed via uv)
```

---

## Setup Instructions

### 1. Prerequisites
* **Python 3.14+**
* **uv** (recommended for virtual env and package management)
* **Docker** (for Postgres)
* **API Keys**: AccuWeather API Key & NewsAPI.org API Key

### 2. Environment Configuration
Create a `.env` file in the root of the project:
```env
ACCUWEATHER_API_KEY="your_accuweather_api_key"
NEWS_API_KEY="your_news_api_key"
DEEPSEEK_API_KEY="your_deepseek_api_key"
DB_URL="postgresql://postgres:postgres@localhost:5442/postgres"
LOG_LEVEL="INFO"
```

### 3. Database Initialization
Start the PostgreSQL container:
```powershell
docker compose up -d
```
This spins up PostgreSQL on port `5442` (credentials matching the default `DB_URL` above).

### 4. Install Dependencies
Using `uv`, set up the virtual environment and install packages:
```powershell
uv sync
```

---

## How to Run

For local development, both services can be run simultaneously using python:

### 1. Start the MCP Server (Port 8000)
Exposes the weather and news tools at `http://127.0.0.1:8000/mcp/sse`.
```powershell
python mcp_server/server.py
```

### 2. Start the Main Chat Server (Port 8001)
Serves the FastAPI endpoint at `http://127.0.0.1:8001`.
```powershell
python main.py
```

---

## How to Test

### Method 1: Interactive Test Client (Recommended)
With both servers running, execute the pre-configured console streaming test:
```powershell
python test_client.py
```
This sends a request to the main server, calls the appropriate MCP tools, and streams the tokens live to your terminal.

### Method 2: Swagger UI Docs
FastAPI automatically publishes documentation. Open your browser and navigate to:
* **[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)**
* Run `POST /chat` with a request body structure:
  ```json
  {
    "message": "What is the weather in Seattle and latest tech news?",
    "thread_id": "optional-thread-uuid"
  }
  ```

### Method 3: Command-Line (cURL)
Test using raw cURL. The `-N` flag forces unbuffered output so you see the stream in real-time:
```bash
curl -N -X POST -H "Content-Type: application/json" -d '{"message": "What is the weather in London?"}' http://127.0.0.1:8001/chat
```
