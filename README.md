# AAI-520 Final Project — Investment Research Agent

**Due: October 16, 2026** | USD Applied Artificial Intelligence Program

An agentic AI system that autonomously researches financial markets using multi-agent coordination and three core workflow patterns.

---

## Team Setup (first time only)

### 1. Clone the repo
```bash
git clone <repo-url>
cd Finalproject
```

### 2. Create your personal branch
```bash
git checkout -b your-name
git push -u origin your-name
```
**Never commit directly to `main`.** Open a Pull Request when your work is ready.

### 3. Set up your environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then fill in your API keys
```

### 4. Auto-activate .venv on `cd` (one-time setup)

Install direnv:
```bash
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
direnv allow .
```

After this, every time you `cd` into the project folder the `.venv` activates automatically.

---

## Repo Structure

```
Finalproject/
├── agents/              # Autonomous LLM agent modules
│   ├── research_agent.py     # Main orchestrator
│   ├── news_agent.py         # News specialist
│   ├── earnings_agent.py     # Earnings specialist
│   └── market_agent.py       # Market data specialist
├── workflows/           # Three required workflow patterns
│   ├── prompt_chaining.py    # Ingest→Preprocess→Classify→Extract→Summarize
│   ├── routing.py            # Route to the right specialist
│   └── evaluator_optimizer.py # Generate→Evaluate→Refine
├── tools/               # External API integrations
│   ├── yfinance_tool.py
│   ├── news_tool.py
│   └── memory_tool.py
├── notebooks/           # Final deliverable notebook
├── tests/               # Unit tests
├── data/                # Local datasets (gitignored)
├── private/             # Local-only reference files (gitignored)
├── .env                 # API keys — NEVER commit this
├── requirements.txt
├── plan.md              # Team project plan
└── CLAUDE.md            # AI assistant rules for this repo
```

---

## Grading Breakdown

| Component | Weight | Key Requirement |
|---|---|---|
| Agent Functions | 33.8% | Plan, tools, self-reflect, memory |
| Workflow Patterns | 33.8% | Prompt chaining, routing, evaluator-optimizer |
| Code | 32.4% | PEP 8, notebook as PDF/HTML, GitHub link included |

---

## Git Workflow

```
main
 └── develop          (integration branch)
      ├── member1     (personal work branch)
      ├── member2
      └── member3
```

1. Work on your personal branch.
2. Open a PR into `develop` when a piece is done.
3. After team review, merge `develop` → `main` before submission.

---

## APIs / Data Sources

- `yfinance` — stock prices, financials
- NewsAPI.org — financial news headlines
- FRED API — economic data (free)
- SEC EDGAR — company filings
- Alpha Vantage — alternative price/news data (free tier)
