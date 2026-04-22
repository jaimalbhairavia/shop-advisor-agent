import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shop_advisor_agent import run_agent
from langsmith import Client
from eval_datasets.eval_dataset_small import EVAL_DATASET_SMALL
from langsmith.evaluation import evaluate
from shop_advisor_agent import run_agent
from scorer.suite_scorer import has_output, correct_product_category, price_within_budget
from judges.suite_judge import response_is_helpful, correctness

# Interacting with langsmith API 
client = Client()

# Define dataset
dataset_name = "small-eval-shop-advisor-v2"

def create_dataset():
    if client.has_dataset(dataset_name=dataset_name):
        print(f"Data set {dataset_name} already exists")
        return
    
    else: 
        dataset = client.create_dataset(dataset_name)
        for case in EVAL_DATASET_SMALL:
                client.create_example(
                    inputs = case["input"],
                    outputs = case['output'],
                    dataset_id = dataset.id
                )
        print(f"Dataset '{dataset}' created with '{len(EVAL_DATASET_SMALL)}' cases(s)")

     
def run():
    results = evaluate(
        run_agent,
        data= dataset_name,
        evaluators = [
            #  code evalutors
             has_output, 
            
            # LLM as a judge 
            correctness],
        experiment_prefix= "Shop Advisor - Small Eval "
    )
    print(results)



if __name__ == "__main__":
    create_dataset()
    run()