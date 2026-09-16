"""
Workflow 1: Prompt Chaining
Chain: Ingest News → Preprocess → Classify → Extract → Summarize
Each step feeds its output directly into the next.
"""

from __future__ import annotations

import os
import json

import anthropic
from dotenv import load_dotenv

from tools.news_tool import fetch_news

load_dotenv()


def run_prompt_chain(ticker: str, lookback_days: int = 7) -> dict:
    """
    Run the full prompt chain for a ticker and return a structured result.

    Steps:
      1. Ingest  — fetch raw news articles
      2. Preprocess — clean and deduplicate titles
      3. Classify — label each article (earnings / macro / sentiment / other)
      4. Extract  — pull key facts from classified articles
      5. Summarize — write a final news summary
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # STEP 1 — INGEST

    print(f"[Chain] Step 1: Ingesting news for {ticker}...")
    articles = fetch_news(ticker, lookback_days=lookback_days)
    if not articles:
        return {"ticker": ticker, "error": "No news articles found."}

    
    # STEP 2 — PREPROCESS

    print(f"[Chain] Step 2: Preprocessing {len(articles)} articles...")
    seen = set()
    clean = []
    for a in articles:
        title = (a.get("title") or "").strip()
        if title and title not in seen:
            seen.add(title)
            clean.append({
                "title": title,
                "source": a.get("source"),
                "published_at": a.get("published_at"),
                "description": a.get("description") or "",
            })

    # STEP 3 — CLASSIFY
    
    print(f"[Chain] Step 3: Classifying {len(clean)} articles...")
    classify_prompt = (
        f"Classify each news headline about {ticker} into one of these categories:\n"
        f"  - earnings (revenue, profit, EPS, guidance)\n"
        f"  - macro (interest rates, economy, regulation)\n"
        f"  - sentiment (analyst ratings, upgrades, downgrades)\n"
        f"  - product (new products, partnerships, launches)\n"
        f"  - other\n\n"
        f"Headlines:\n"
        + "\n".join(f"{i+1}. {a['title']}" for i, a in enumerate(clean))
        + "\n\nReturn a JSON array where each item has: "
        f'{{\"index\": 1, \"category\": \"earnings\", \"title\": \"...\"}}. '
        f"Return ONLY the JSON array."
    )
    classify_resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": classify_prompt}],
    )
    try:
        classified = json.loads(classify_resp.content[0].text.strip())
    except json.JSONDecodeError:
        classified = [{"index": i+1, "category": "other", "title": a["title"]}
                      for i, a in enumerate(clean)]

    
    # STEP 4 — EXTRACT
    
    print(f"[Chain] Step 4: Extracting key facts...")
    extract_prompt = (
        f"You are a financial analyst. From these classified {ticker} news items, "
        f"extract the 3-5 most important facts an investor should know.\n\n"
        f"Classified articles:\n{json.dumps(classified, indent=2)}\n\n"
        f"Return a JSON array of fact strings. Return ONLY the JSON array."
    )
    extract_resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        messages=[{"role": "user", "content": extract_prompt}],
    )
    try:
        key_facts = json.loads(extract_resp.content[0].text.strip())
    except json.JSONDecodeError:
        key_facts = [extract_resp.content[0].text.strip()]

    
    # STEP 5 — SUMMARIZE
    print(f"[Chain] Step 5: Generating final summary...")
    summarize_prompt = (
        f"Write a 2-paragraph news summary for {ticker} based on these key facts:\n\n"
        + "\n".join(f"- {f}" for f in key_facts)
        + "\n\nParagraph 1: What happened. Paragraph 2: What it means for investors."
    )
    summarize_resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        messages=[{"role": "user", "content": summarize_prompt}],
    )
    summary = summarize_resp.content[0].text.strip()

    return {
        "ticker": ticker,
        "articles_ingested": len(articles),
        "articles_after_dedup": len(clean),
        "classified": classified,
        "key_facts": key_facts,
        "summary": summary,
    }
