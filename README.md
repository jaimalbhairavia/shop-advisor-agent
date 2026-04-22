# 🛍️ Shop Advisor Agent

A ReAct (Reasoning + Acting) agent that helps you find the best products based on your needs, budget, and preferences — powered by LangGraph and your choice of LLM.

---

## Demo

Agent Demo

![Shop Advisor Agent Demo](assests/extended%20shop%20advisor.gif)

[Lang Smith trace for demo run](https://smith.langchain.com/public/c8e1a54a-d551-4ce1-9d0a-278ed4bcc308/r)

---

## How It Works

The agent follows a structured reasoning loop for every query:

```
User Query
    │
    ▼
product_search_tool       ← keyword search across catalog
    │
    ▼
LLM filters results       ← price, use case, features
    │
    ▼
safety_check              ← blocks bad categories, banned brands, low ratings
    │
    ▼
price_compare             ← finds best vendor price per product
    │
    ▼
Ranked Recommendations
```

**Example:**
> "Best headphones under $200 for travel"
>
> → Finds 5 headphones → filters by price → removes low-rated → compares Amazon vs BestBuy vs Walmart → recommends top picks with best prices

---

## Project Structure

```
shop-advisor-agent/
├── shop_advisor_agent.py   # Entry point — wire model + tools + prompt
├── models.py               # Provider-agnostic model factory
├── tools.py                # LangChain tools (search, safety, pricing)
├── prompts_library.py      # System prompt for the agent
├── data/
│   ├── products.json       # Product catalog
│   ├── price.json          # Vendor pricing (Amazon, BestBuy, Walmart…)
│   └── safety_rules.json   # Blocked categories, banned brands, rating floor
├── evals/
│   ├── eval.py             # Full eval suite (LangSmith)
│   ├── eval_small.py       # Lightweight 5-case smoke test
│   └── eval_datasets/
│       ├── dataset.py      # Full dataset — 29 cases across 8 categories
│       └── eval_dataset_small.py  # 5-case subset for fast iteration
├── scorer/
│   ├── suite_scorer.py     # Deterministic evaluators (run on every case)
│   └── case_scorer.py      # Deterministic evaluators (category-specific)
├── judges/
│   ├── suite_judge.py      # LLM-as-judge evaluators (run on every case)
│   └── case_judge.py       # LLM-as-judge evaluators (category-specific)
└── runbook.py              # Dev sandbox for testing tool logic
```

---

## Tools

| Tool | Input | What it does |
|------|-------|-------------|
| `product_search_tool` | `query: str` | Keyword matches against product name, category, and features |
| `safety_check` | `product_ids: list` | Filters out blocked categories, banned brands, and low-rated products |
| `price_compare` | `product_ids: list` | Returns best vendor price per product, sorted cheapest first |

---

## Switching Models

Set the `model` variable in `shop_advisor_agent.py` to any model name string. The factory in `models.py` detects the provider automatically:

- Names containing **claude** or **anthropic** → Anthropic
- Names containing **gpt**, **o1**, **o3**, or **o4** → OpenAI
- Anything else → falls back to `claude-opus-4-20250514` with a warning

---

## Setup
<!-- Create and start a virtual environment -->

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python shop_advisor_agent.py
```

---

## Evals

The eval suite runs every agent response through a combination of deterministic scorers and LLM-as-judge evaluators, integrated with LangSmith.

### Evaluators

**Deterministic scorers** (`scorer/`) — fast, rule-based checks:

| Evaluator | Scope | What it checks |
|-----------|-------|----------------|
| `has_output` | Every case | Agent returned a non-empty response |
| `correct_product_category` | Cases with expected categories | Response mentions a product from the expected category |
| `price_within_budget` | Cases with a budget | All prices in the response are within the stated budget |
| `no_literal_passthrough` | Passive description cases | Agent translated indirect descriptions into real product terms |
| `safety_blocked` | Safety blocking cases | Agent refused blocked/out-of-scope requests |
| `no_banned_brands` | Safety blocking cases | Agent did not recommend any banned brands |

**LLM-as-judge** (`judges/`) — quality checks that code cannot catch:

| Evaluator | Scope | What it checks |
|-----------|-------|----------------|
| `response_is_helpful` | Every case | Response directly addresses the user's query, not generically |
| `correctness` | Every case | Overall correctness — right products, right refusals, no hallucinations |
| `understood_user_intent` | Cases with expected categories | Agent correctly interpreted indirect or passive queries |
| `helpful_tone` | Cases expecting results | Response is confident, friendly, and actionable |

### Test Dataset

29 cases across 8 categories in `evals/eval_datasets/dataset.py`:

| Category | Cases | Tests |
|----------|-------|-------|
| `happy_path` | 5 | Standard product queries with budget |
| `budget_filtering` | 4 | Exact budget limits, no-results when too tight |
| `safety_blocking` | 4 | Blocked categories, banned brands, rating floor |
| `safety_flagging` | 2 | Flagged categories surfaced to LLM |
| `multi_constraint` | 4 | Brand inclusion/exclusion + budget combined |
| `passive_description` | 5 | Indirect queries that require intent mapping |
| `no_results` | 3 | Queries outside catalog scope |
| `out_of_scope` | 3 | Illegal or out-of-domain requests |

### Running Evals

```bash
# Quick smoke test — 5 cases, 2 evaluators
python -m evals.eval_small

# Full suite — 29 cases, 5 evaluators
python -m evals.eval
```

Results stream to your LangSmith dashboard in real time.

### Eval Results

![Eval Results](assests/evaluation.png)

---

## Tracing with LangSmith

LangSmith gives you a full trace of every agent run — tools called, LLM reasoning at each step, token counts, and latency. The `.env` is already configured with tracing enabled and the project set to `Shop_Advisor_Agent`.

- Get your API key at [smith.langchain.com](https://smith.langchain.com)
- Add `LANGCHAIN_API_KEY` to your `.env` file — that's the only step needed
- Run the agent and traces appear live in the LangSmith dashboard

---

## Safety Rules

Configured in `data/safety_rules.json`. The agent applies these rules before making any recommendation:

- **Blocked categories** — weapons, illegal items → excluded entirely
- **Flagged categories** — health, supplements → surfaced to the LLM for review, not auto-blocked
- **Minimum rating** — products rated below 3.5 are excluded
- **Banned brands** — any brand listed as Unknown is excluded

---

## Data

The catalog currently covers **consumer electronics** — headphones, earbuds, keyboards, and mice from brands like Sony, Bose, Apple, Logitech, and Keychron. Pricing data spans Amazon, BestBuy, Walmart, Target, Newegg, and the Apple Store.

To expand coverage, add entries to `data/products.json` and `data/price.json`.
