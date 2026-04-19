import json

#  load products from json file
with open("data/products.json") as f:
        products =json.load(f)

def product_search_tool(query: str) -> list:
    """Search the product data to find matching products"""

    query_words = query.lower().split()
    # print(query_words)

    results = set()
    
    # load products from json file
    with open("data/products.json") as f:
        products =json.load(f)
    
    for product in products:
        # check if any words from the query match the product name or category
        # print(product["name"])
        for word in query_words:
            if word in product["name"] or word in product["category"]:
                results.add(product["id"])

    # return results
    print(results)       

product_search_tool("Best headphones under $150 for travel")



def price_compare(product_id:list, max_price: str) -> dict:
    max_price_int = int(max_price)
    # strip the first charcter of the string and match
    for id in product_id:
        # print(id[1:])
        # strip the first charcter of the string and match
        id_new: int = int(id[1:])
        # if  not products["price"] in products[id_new] > max_price_int:
        #       print(products["price"])
        
        
        # print(products[id_new])
        # prices = 
        

price_compare(["p1", "p2", "p5"], 200)