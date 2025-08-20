import random
from bs4 import BeautifulSoup
import requests


# Step 1: Fetch free proxy list
def get_free_proxies():
    url = "https://free-proxy-list.net/"  # public free proxies
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    proxies = []
    # Kids, do not do it like this
    firstShave = response.text.split('UTC.')[1]

    secondShave = firstShave.split('</textarea>')[0]

    for line in secondShave.split('\n'):
        if line.strip() and not line.startswith('#'):
            proxies.append(line.strip())
    return proxies

# Step 2: Create a rotating proxy list
# Initial proxy fetch
PROXY_LIST = get_free_proxies()

def get_random_proxy():
    return random.choice(PROXY_LIST)
    
response = requests.get(f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=",
                                    proxies=get_random_proxy(), timeout=5)
print("Status Code:", response.status_code)
if response.ok:
    data = response.json()
    print("Data fetched successfully.")
    print(data)