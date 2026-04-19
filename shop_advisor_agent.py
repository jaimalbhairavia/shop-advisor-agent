from dotenv import load_dotenv
from langchain.agents import create_agent
from tools import product_search_tool, safety_check, price_compare
from prompts_library import system_prompt
from models import model_use

load_dotenv()

model = "gpt-5-nano-2025-08-07"

shop_advisor_agent = create_agent(
    model=model_use(model),
    tools=[product_search_tool, safety_check, price_compare],
    system_prompt=system_prompt,
)


if __name__ == "__main__":
    user_query = "Best headphones under $200 for travel"
    print(f"User: {user_query}\n")

    response = shop_advisor_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query,
                }
            ]
        }
    )

    print("Agent:", response["messages"][-1].content)
