"""
Workflow 3: Evaluator-Optimizer
Generate an analysis, evaluate its quality against criteria, then refine
using the feedback. Loops until quality passes or max iterations reached.
"""

from __future__ import annotations

import os
import json

import anthropic
from dotenv import load_dotenv
from tools.anthropic_tool import response_text

load_dotenv()


DEFAULT_CRITERIA = [
    "Factual accuracy and specificity (uses concrete numbers)",
    "Balanced view of risks and opportunities",
    "Clear investment takeaway",
    "No vague or filler statements",
]


def _evaluate(draft: str, criteria: list[str], client: anthropic.Anthropic) -> dict:
    """Score a draft against criteria. Returns {score, passed, feedback}."""
    prompt = (
        "You are a strict senior investment analyst evaluating a junior's draft.\n\n"
        f"Evaluation criteria:\n" + "\n".join(f"  - {c}" for c in criteria) + "\n\n"
        f"Draft to evaluate:\n{draft}\n\n"
        "Score the draft from 1-10 and give specific, actionable feedback.\n"
        'Return ONLY JSON: {"score": 7, "feedback": "..."}'
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(response_text(resp))
    except json.JSONDecodeError:
        return {"score": 5, "feedback": response_text(resp)}


def _optimize(draft: str, feedback: str, client: anthropic.Anthropic) -> str:
    """Rewrite the draft using the feedback."""
    prompt = (
        "You are refining an investment analysis based on reviewer feedback.\n\n"
        f"Original draft:\n{draft}\n\n"
        f"Reviewer feedback:\n{feedback}\n\n"
        "Rewrite the analysis addressing every point of feedback. "
        "Return only the improved analysis."
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    return response_text(resp)


def run_evaluator_optimizer(
    draft: str,
    criteria: list[str] | None = None,
    threshold: int = 8,
    max_iterations: int = 3,
) -> dict:
    """
    Iteratively evaluate and refine a draft analysis.

    Returns:
      {final_draft, iterations, history}
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    criteria = criteria or DEFAULT_CRITERIA

    current = draft
    history = []

    for i in range(1, max_iterations + 1):
        print(f"[EvalOpt] Iteration {i}: evaluating...")
        evaluation = _evaluate(current, criteria, client)
        score = evaluation.get("score", 0)
        feedback = evaluation.get("feedback", "")
        history.append({"iteration": i, "score": score, "feedback": feedback})
        print(f"[EvalOpt] Score: {score}/10")

        if score >= threshold:
            print(f"[EvalOpt] Passed threshold ({threshold}). Stopping.")
            break

        if i < max_iterations:
            print(f"[EvalOpt] Below threshold. Refining...")
            current = _optimize(current, feedback, client)

    return {
        "final_draft": current,
        "iterations": len(history),
        "history": history,
    }
