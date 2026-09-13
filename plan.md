# AAI-520 Final Project — Team Plan

**Project:** Autonomous Investment Research Agent
**Due:** October 16, 2026
**Team size:** 2–3 members

---

## Grading Breakdown

| Component | Weight | What It Covers |
|---|---|---|
| Agent Functions | 33.8% | Plan steps, dynamic tools, self-reflection, cross-run memory |
| Workflow Patterns | 33.8% | Prompt chaining, routing, evaluator-optimizer |
| Code | 32.4% | PEP 8, notebook (PDF/HTML), GitHub link, comments/report |

---

## Timeline (Sep 13 – Oct 16)

### Week 1 — Setup & Architecture (Sep 13–20)

**Goal:** Everyone can run the project locally; architecture is agreed on.

- [ ] Create GitHub repo and push initial structure
- [ ] Each member creates their personal branch (`git checkout -b your-name`)
- [ ] All members clone repo and set up `.venv`
- [ ] Agree on LLM provider (Anthropic Claude recommended) and API keys
- [ ] Confirm data sources: yfinance + one news source
- [ ] Sketch the agent architecture (which agent does what)
- [ ] Assign ownership: who owns agents, who owns workflows, who owns notebook

**Deliverable:** Repo live on GitHub with README, team all set up locally.

---

### Week 2 — Agent Functions (Sep 21–27)

**Goal:** Core autonomous agent working end-to-end for one ticker.

- [ ] `ResearchAgent` — planning logic (break ticker research into steps)
- [ ] `NewsAgent` — fetch and classify news articles
- [ ] `EarningsAgent` — pull and parse financial statements
- [ ] `MarketAgent` — price history and basic signals
- [ ] `AgentMemory` — save/load notes between runs (JSON file is fine)
- [ ] `ResearchAgent.reflect()` — self-critique of output quality

**Deliverable:** Running `ResearchAgent.run("AAPL")` produces a structured report.

---

### Week 3 — Workflow Patterns (Sep 28–Oct 4)

**Goal:** All three required workflow patterns implemented and demonstrable.

- [ ] **Prompt Chaining:** Ingest News → Preprocess → Classify → Extract → Summarize
  - Wire the `NewsAgent` steps into a sequential chain
- [ ] **Routing:** Given a piece of content, route to `EarningsAgent`, `NewsAgent`, or `MarketAgent`
  - Use an LLM classifier to decide the specialist
- [ ] **Evaluator–Optimizer:** Generate analysis → evaluate with criteria → refine
  - Loop until quality threshold met or max iterations reached

**Deliverable:** Each workflow runnable independently with a demo input.

---

### Week 4 — Integration & Testing (Oct 5–11)

**Goal:** Full system connected; notebook tells a clear story.

- [ ] Wire all workflows into the main `ResearchAgent.run()` loop
- [ ] Run end-to-end for 2–3 tickers (e.g., AAPL, NVDA, TSLA)
- [ ] Add notebook markdown cells explaining: Agent Design, Functions, Evaluation
- [ ] Write a brief Supplemental Report (optional but recommended for clarity)
- [ ] Team code review: PEP 8 pass on all files
- [ ] Confirm GitHub repo link is in notebook

**Deliverable:** Notebook runs clean top-to-bottom; GitHub has full commit history from all members.

---

### Week 5 — Polish & Submit (Oct 12–16)

**Goal:** Final submission ready by Oct 16.

- [ ] Export notebook as PDF (preferred) or HTML
- [ ] Final README review — GitHub link, setup instructions
- [ ] One team member submits to Canvas (PDF/HTML + optional report)
- [ ] Submit Peer Evaluation individually

**Deliverable:** Submitted to Canvas by Oct 16.

---

## Git Workflow

```
main            ← protected, merge via PR only
 └── develop    ← integration branch
      ├── [member1-name]
      ├── [member2-name]
      └── [member3-name]
```

### Commands each member runs (first time)

```bash
git clone <repo-url>
cd Finalproject
git checkout -b your-name
git push -u origin your-name
```

### Daily workflow

```bash
git pull origin your-name      # get latest from your own branch
# ... do work ...
git add agents/research_agent.py    # stage specific files only
git commit -m "feat: add planning logic to ResearchAgent"
git push origin your-name
```

### Submitting work for review (open a PR on GitHub)

`your-name` → `develop` → reviewed by team → `main`

---

## Ownership Split 

| Area | Files | Owner |
|---|---|---|
| Core agent + memory | `agents/research_agent.py`, `tools/memory_tool.py` | Member 1 |
| Specialist agents + tools | `agents/news_agent.py`, `agents/earnings_agent.py`, `agents/market_agent.py`, `tools/` | Member 2 |
| Workflow patterns + notebook | `workflows/`, `notebooks/` | Member 3 |

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Anthropic Claude (claude-opus-5 / claude-sonnet-5) |
| Agent framework | LangGraph or raw Anthropic SDK |
| Observability | LangSmith |
| Financial data | yfinance, Alpha Vantage |
| News | NewsAPI.org or yfinance news |
| Environment | Python 3.11+, `.venv`, python-dotenv |

---

## API Keys Needed

Create a `.env` file (gitignored — never commit):

```
ANTHROPIC_API_KEY=sk-ant-...
NEWSAPI_KEY=...
ALPHA_VANTAGE_KEY=...
FRED_API_KEY=...
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
```
