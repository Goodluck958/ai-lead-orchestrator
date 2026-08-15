# ⚡ Autonomous Multi-Agent Business Intelligence Engine

A production-grade, asynchronous AI agent orchestration API built with **FastAPI**, **Pydantic**, and **LangChain**. Engineered around **Dependency Inversion** and **Contract-First API Design** to decouple control logic from third-party APIs, support deterministic testing, and enable seamless vendor pluggability.

---

## 🏗️ Architectural Principles

* **Dependency Inversion Principle (DIP):** Core orchestration relies exclusively on abstract interfaces (`BaseResearchService`, `BaseSynthesisService`). Concrete third-party tools are injected at the Composition Root (`main.py`) rather than hardcoded inside the agent logic.
* **Contract-First Schema Validation:** Strictly typed `AgentState` powered by **Pydantic** guarantees deterministic state transfer between workflow stages.
* **Asynchronous Execution:** Powered by Python's `asyncio` and **FastAPI** to handle high-concurrency request execution efficiently.
* **Environment-Aware Behavior:**
  * **Development / Testing:** Auto-fallback to mock engines for offline, zero-cost rapid iteration.
  * **Production Strategy:** Designed for explicit status reporting, retries, and circuit-breaker handling to prevent silent data corruption.

---

## 📐 System Flow

```text
                     [ Client Request ]
                             │
                             ▼
                 [ FastAPI Route: /run-agent ]
                             │
                             ▼
                   [ OrchestratorAgent ]
                    │                 │
                    ▼                 ▼
             [ Research Contract ] [ Synthesis Contract ]
                    │                 │
              (Mock / Tavily)   (Mock / OpenAI)
                    │                 │
                    └────────┬────────┘
                             ▼
                   [ Structured JSON ]
                   
