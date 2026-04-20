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
