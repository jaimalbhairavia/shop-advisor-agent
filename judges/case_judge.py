"""
case_judge.py
LLM-as-judge checks for specific quality criteria.
Runs on every test case.
"""

import json
import anthropic
from pathlib import Path
from langsmith.schemas import Run, Example

client = anthropic.Anthropic()


def _load_categories() -> list[str]:
    """
    Load available product categories from the catalog.
    Stays in sync with products.json automatically.
    """
    catalog_path = Path(__file__).parent.parent / "data" / "products.json"
    with open(catalog_path) as f:
        products = json.load(f)

    # extract unique categories from catalog
    categories = list({p["category"] for p in products})
    return categories


def _ask_judge(prompt: str) -> tuple[int, str]:
    """
    Helper — sends a prompt to the judge and parses YES/NO response.
    Returns (score, reason).
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.content[0].text.strip()
    score = 1 if answer.upper().startswith("YES") else 0
    return score, answer


def understood_user_intent(run: Run, example: Example) -> dict:
    """
    Check the agent correctly understood what product the user
    was looking for, even when described indirectly.
    Scores the understanding — not whether a product was found.
    """
    query = example.inputs["query"]
    output = run.outputs.get("output", "")
    expected_categories = example.outputs["expected"].get("product_categories", [])
    available_categories = _load_categories()
 
    if not output:
        return {"key": "understood_user_intent", "score": 0, "reason": "No output returned"}
 
    if not expected_categories:
        return {"key": "understood_user_intent", "score": None, "reason": "Skipped — no expected categories defined"}
 
    prompt = f"""
You are evaluating an AI shopping assistant.
 
The assistant operates on the following product categories only:
{", ".join(available_categories)}
 
User query: {query}
Expected product categories for this query: {", ".join(expected_categories)}
Agent response: {output}
 
Your job is to evaluate whether the agent understood what the user was looking for.
This is independent of whether the agent found a matching product or not.
 
A correct understanding means:
- The agent interpreted the user's intent as looking for {", ".join(expected_categories)}
- If no product was found, the agent communicated that clearly while still showing
  it understood the user was looking for {", ".join(expected_categories)}
- The agent did NOT interpret the query as a different product category
 
Question: Did the agent correctly understand what the user was looking for,
regardless of whether a matching product was found?
 
Answer YES or NO only. Then on a new line explain why in one sentence.
"""
    score, reason = _ask_judge(prompt)
    return {"key": "understood_user_intent", "score": score, "reason": reason}

def helpful_tone(run: Run, example: Example) -> dict:
    """
    Check the agent's response is helpful and uses the correct tone
    for a shopping assistant — confident, friendly, and actionable.
    Skips when no results are expected since tone expectations differ.
    """
    query = example.inputs["query"]
    output = run.outputs.get("output", "")

    if not output:
        return {"key": "helpful_tone", "score": 0, "reason": "No output returned"}

    # tone expectations differ when no results — skip
    if not example.outputs["expected"].get("has_results", True):
        return {"key": "helpful_tone", "score": None, "reason": "Skipped — no results expected for this case"}

    prompt = f"""
You are evaluating an AI shopping assistant.

User query: {query}
Agent response: {output}

Evaluate the response on two things:
1. Helpful — does it give the user something actionable, not vague or generic?
2. Tone — is it confident, friendly, and concise? Not robotic or overly cautious?

Question: Does the response meet both criteria — helpful AND correct tone?
Answer YES or NO only. Then on a new line explain why in one sentence.
"""
    score, reason = _ask_judge(prompt)
    return {"key": "helpful_tone", "score": score, "reason": reason}