import requests
from bs4 import BeautifulSoup
import random
import time

# Step 1: Fetch free proxy list
def get_free_proxies():
    url = "https://free-proxy-list.net/"  # public free proxies
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    proxies = []
    print(f"Fetched proxies: {soup}")
    # Kids, do not do it like this
    firstShave = response.text.split('UTC.')[1]
    print("First shave:")
    print(firstShave)
    secondShave = firstShave.split('</textarea>')[0]
    print("Second shave:")
    print(secondShave)
    for line in secondShave.split('\n'):
        if line.strip() and not line.startswith('#'):
            proxies.append(line.strip())
    return proxies

# Step 2: Create a rotating proxy list
# Initial proxy fetch
PROXY_LIST = get_free_proxies()
start_time = time.time()  # start counting from first fetch

def get_random_proxy():
    return random.choice(PROXY_LIST)

lastSuccessfulProxy = "None"
start_time = time.time()    

def timer(start):
    elapsed_time = time.time() - start
    return elapsed_time

def fetch_Url(itemName):
    global lastSuccessfulProxy
    global start_time  
    
    isFetched = False
    while not isFetched:
        # Refetch proxies if more than 5 minutes have passed
        if timer(start_time) > 300:
            PROXY_LIST = get_free_proxies()
            start_time = time.time()
        proxy = get_random_proxy()
        print("Using proxy:", proxy)
        print("Fetching URL for item:", itemName)
        proxies = {"http": proxy, "https": proxy}
        try:
            if lastSuccessfulProxy != "None":
                print("Last successful proxy:", lastSuccessfulProxy)
                proxies = {"http": lastSuccessfulProxy, "https": lastSuccessfulProxy}
                lastSuccessfulProxy = "None"
            response = requests.get(f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name={itemName}",
                                    proxies=proxies, timeout=1)
            isFetched = True
            lastSuccessfulProxy = proxy
            return response
        except Exception as e:
            print("Request failed:", e)


def testFetchViaList(listOfItems):
    for item in listOfItems:
        print(fetch_Url(item))

# Test
def test():
    print(fetch_Url("Glove Case"))
    print(fetch_Url("Gallery Case"))

if __name__ == "__main__":
    NEEDTOTEST = False
    if NEEDTOTEST:
        test()
    else:
        print("Ready to fetch URLs.")