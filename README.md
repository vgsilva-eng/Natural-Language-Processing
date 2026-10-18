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
├── notebooks/
│   ├── investment_research_agent.ipynb   # Final deliverable — run this
│   └── archive/                          # Individual agent demos (reference only)
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

---

## Agents

| Agent | Description |
|---|---|
| `ResearchAgent` | Orchestrator — plans research steps, fetches data, synthesizes a 3-paragraph investment report, and self-reflects on output quality |
| `MarketAgent` | Analyzes price trends, moving averages, and volume from Yahoo Finance — no LLM required |
| `NewsAgent` | Fetches recent news articles, classifies each by financial topic, and summarizes key themes using Claude |
| `EarningsAgent` | Pulls financial statements from Yahoo Finance and computes revenue, net income, margins, and valuation ratios |

---

## Workflow Patterns

| Workflow | Description |
|---|---|
| `Prompt Chaining` | 5-step news pipeline: ingest → preprocess → classify → extract facts → summarize |
| `Routing` | LLM classifier reads content and dispatches it to the correct specialist agent |
| `Evaluator-Optimizer` | Scores a draft, gives feedback, rewrites it — loops until quality passes a threshold |

---

## Final Deliverable

The complete project is demonstrated in:

**[`notebooks/investment_research_agent.ipynb`](notebooks/investment_research_agent.ipynb)**

This notebook runs all four agents and all three workflow patterns end-to-end, with live data, visualizations, and annotated outputs. It is the primary submission artifact and should be reviewed as a self-contained document.

---

## Setup

```bash
git clone https://github.com/vgsilva-eng/Natural-Language-Processing.git
cd Natural-Language-Processing
git checkout VivianaS
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY and NEWSAPI_KEY
```

Then open and run the notebook top-to-bottom with VPN disconnected:

```bash
jupyter notebook notebooks/investment_research_agent.ipynb
```

---

## Dependencies

```
anthropic
yfinance
pandas
python-dotenv
jupyter
```

---

## Team

- Viviana Garzon
- Obinna Edeh
- Dina Othman

---

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

Tests use fixed data and cover price history, missing metadata, invalid tickers, chart creation, news classification, and routing.
