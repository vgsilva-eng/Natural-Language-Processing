# Investment Research Agent
### AAI-520 · Agentic AI Systems · University of San Diego

An autonomous multi-agent system that researches financial markets end-to-end — planning research steps, routing content to specialist agents, self-reflecting on output quality, and retaining memory across runs.

---

## Agent Architecture

```
                        ResearchAgent (Orchestrator)
                               |
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
         NewsAgent       EarningsAgent     MarketAgent
     (news + sentiment)  (financials)   (price + signals)
              │                │                │
              └────────────────┴────────────────┘
                               │
                         AgentMemory
                    (persists notes across runs)
```

---

## Workflow Patterns

| Pattern | Flow |
|---|---|
| **Prompt Chaining** | Ingest News → Preprocess → Classify → Extract → Summarize |
| **Routing** | LLM classifier → EarningsAgent / NewsAgent / MarketAgent |
| **Evaluator–Optimizer** | Generate analysis → Evaluate quality → Refine (loop) |

---

## Grading Breakdown

| Component | Weight |
|---|---|
| Agent Functions | 33.8% |
| Workflow Patterns | 33.8% |
| Code | 32.4% |

---

## Repo Structure

```
Finalproject/
├── agents/
│   ├── research_agent.py      # Orchestrator — planning, reflection, memory
│   ├── news_agent.py          # News ingestion and sentiment
│   ├── earnings_agent.py      # Financial statements analysis
│   └── market_agent.py        # Price history and technical signals
├── workflows/
│   ├── prompt_chaining.py
│   ├── routing.py
│   └── evaluator_optimizer.py
├── tools/
│   ├── yfinance_tool.py
│   ├── news_tool.py
│   └── memory_tool.py
├── notebooks/                 # Final deliverable
├── tests/
├── .env.example               # API key template
└── requirements.txt
```

---

## Data Sources

| Source | Use |
|---|---|
| `yfinance` | Stock prices, financials |
| NewsAPI.org | Financial news headlines |
| FRED API | Economic indicators |
| SEC EDGAR | Company filings |
| Alpha Vantage | Alternative price and news data |

---

## Setup

```bash
git clone https://github.com/vgsilva-eng/Natural-Language-Processing.git
cd Natural-Language-Processing
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

---

## Dependencies

```
anthropic
langchain / langgraph
yfinance
pandas · numpy
python-dotenv
jupyter
```

---

## Team

- Viviana Garzon
- Obinna Edeh
- Dina Othman
