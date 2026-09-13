# Investment Research Agent
### AAI-520 · Agentic AI Systems · University of San Diego

An autonomous multi-agent system that researches financial markets end-to-end — planning research steps, routing content to specialist agents, self-reflecting on output quality, and retaining memory across runs.

---

## System Architecture

```
  Stock Ticker
       │
       ▼
┌─────────────────────────────────────┐
│           ResearchAgent             │◀── AgentMemory
│   Plan steps · Delegate · Reflect   │    (persists notes
└────────────────┬────────────────────┘     across runs)
                 │
                 ▼
    ┌────────────────────────┐
    │   Routing Workflow     │  ← classifies content type
    └──┬──────────┬──────────┘
       │          │          │
  ┌────▼───┐ ┌────▼────┐ ┌──▼────────┐
  │  News  │ │Earnings │ │  Market   │
  │ Agent  │ │  Agent  │ │  Agent    │
  │NewsAPI │ │yfinance │ │ yfinance  │
  └────┬───┘ └────┬────┘ └──┬────────┘
       └──────────┴──────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │    Prompt Chain Workflow    │
    │ Ingest → Classify →        │
    │   Extract → Summarize      │
    └─────────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │   Evaluator–Optimizer       │
    │ Generate → Evaluate         │
    │         → Refine (loop)    │
    └─────────────┬───────────────┘
                  │
                  ▼
          Research Report
```

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
