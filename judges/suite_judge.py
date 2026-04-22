"""
suite_judge.py
LLM-as-judge checks that run on every test case.
Checks quality that an if statement cannot catch.
"""

import anthropic
from langsmith.schemas import Run, Example
from langsmith.evaluation import EvaluationResult

client = anthropic.Anthropic()


def _ask_judge(prompt: str) -> tuple[int, str]:
    """
    Helper — sends a prompt to the judge and parses YES/NO response.
    Returns (score, reason).
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.content[0].text.strip()
    score = 1 if answer.upper().startswith("YES") else 0
    return score, answer


# def recommends_a_product(run: Run, example: Example) -> dict:
#     """
#     Check the agent actually recommended a product,
#     not just acknowledged the query or asked a clarifying question.
#     Skips when the test case does not expect results.
#     """
#     output = run.outputs.get("output", "")

#     # skip when test case expects no results
#     if not example.outputs["expected"].get("has_results", True):
#         return {"key": "recommends_a_product", "score": None, "reason": "Skipped — no results expected for this case"}

#     if not output:
#         return {"key": "recommends_a_product", "score": 0, "reason": "No output returned"}

#     prompt = f"""
# You are evaluating an AI shopping assistant response.

# Agent response:
# {output}

# Question: Did the agent recommend at least one specific product by name?
# Answer YES or NO only. Then on a new line explain why in one sentence.
# """
#     score, reason = _ask_judge(prompt)
#     return {"key": "recommends_a_product", "score": score, "reason": reason}


# def includes_a_price(run: Run, example: Example) -> dict:
#     """
#     Check the agent included a price in its recommendation.
#     Skips when the test case does not expect results.
#     """
#     output = run.outputs.get("output", "")

#     # skip when test case expects no results
#     if not example.outputs["expected"].get("has_results", True):
#         return {"key": "includes_a_price", "score": None, "reason": "Skipped — no results expected for this case"}

#     if not output:
#         return {"key": "includes_a_price", "score": 0, "reason": "No output returned"}

#     prompt = f"""
# You are evaluating an AI shopping assistant response.

# Agent response:
# {output}

# Question: Did the agent include at least one specific price (e.g. $99, $149.99) in its response?
# Answer YES or NO only. Then on a new line explain why in one sentence.
# """
#     score, reason = _ask_judge(prompt)
#     return {"key": "includes_a_price", "score": score, "reason": reason}


def response_is_helpful(run: Run, example: Example) -> dict:
    """
    Check the response is actually helpful to the user's query,
    not vague, generic, or off-topic.
    """
    query = example.inputs["query"]
    output = run.outputs.get("output", "")

    if not output:
        return {"key": "response_is_helpful", "score": 0, "reason": "No output returned"}

    prompt = f"""
You are evaluating an AI shopping assistant response.

User query: {query}
Agent response: {output}

Question: Is the agent's response directly helpful for the user's query?
A helpful response addresses the user's need specifically, not generically.
Answer YES or NO only. Then on a new line explain why in one sentence.
"""
    score, reason = _ask_judge(prompt)
    return {"key": "response_is_helpful", "score": score, "reason": reason}


def correctness(run: Run, example: Example) -> dict:
    """
    Check the overall correctness of the agent's response
    against the query and expected output.
    Runs on every test case — handles both results and no-results cases.
    """
    query = example.inputs["query"]
    output = run.outputs.get("output", "")
    expected = example.outputs
 
    if not output:
        return EvaluationResult(key="correctness", score=None, comment="No output returned")
 
    prompt = f"""
You are evaluating the response of an AI shopping assistant.
 
User query: {query}
Agent response: {output}
Attributes from the expected output: {expected}
 
A correct response means:
- If results are expected: the agent recommended products from the right category within budget
- If no results are expected: the agent correctly communicated it could not find a match
  or refused the request — without hallucinating and suggesting products that don't exist in the catalog
- If the product being searched for is inferred correctly
- If the queried product doesn't pass the safety check, the agent should not return any matching results.
 
Question: Is the agent's response correct given the query?
Answer YES or NO only. Then on a new line explain why in one sentence.
"""
    score, answer = _ask_judge(prompt)
    return EvaluationResult(key="correctness", score= score, comment=answer)
 