"""
suite_scorer.py
Deterministic checks that run on every test case.
"""

from langsmith.schemas import Run, Example
from langsmith.evaluation import EvaluationResult


def has_output(run: Run, example: Example) -> dict:
    """Check if the agent returned any output at all."""
    output = run.outputs.get("output", "")

    if not output:
        return EvaluationResult(key="has outputs", score=0, comment="Agent returned no output")

    return EvaluationResult(key="has outputs", score=1, comment="Pass")


def correct_product_category(run: Run, example: Example) -> dict:
    """Check if the agent recommended a product from the expected categories."""
    output = run.outputs.get("output", "")
    expected_categories = example.outputs["expected"].get("product_categories", [])

    # if no categories defined for this case, skip
    if not expected_categories:
        return {"key": "correct_product_category", "score": None, "reason": "Skipped — no expected categories defined"}

    categories_hit = any(
        cat.lower() in output.lower()
        for cat in expected_categories
    )

    if not categories_hit:
        return {"key": "correct_product_category", "score": 0, "reason": f"Expected one of {expected_categories} in response"}

    return {"key": "correct_product_category", "score": 1, "reason": "Pass"}


def price_within_budget(run: Run, example: Example) -> dict:

    """Check all prices in the response are within the expected budget."""
    import re

    output = run.outputs.get("output", "")
    max_price = example.outputs["expected"].get("max_price")

    # if no budget defined for this case, skip
    if not max_price:
        return {"key": "price_within_budget", "score": None, "reason": "Skipped — no max price defined"}

    # extract all prices from the response
    prices_found = [float(p.replace(",", "")) for p in re.findall(r"\$([0-9,]+(?:\.[0-9]{2})?)", output)]

    if not prices_found:
        return {"key": "price_within_budget", "score": 0, "reason": "No prices found in response"}

    over_budget = [p for p in prices_found if p > max_price]

    if over_budget:
        return {"key": "price_within_budget", "score": 0, "reason": f"Prices {over_budget} exceed budget of ${max_price}"}

    return {"key": "price_within_budget", "score": 1, "reason": "Pass"}


def correct(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    return outputs["class"] == reference_outputs["label"]