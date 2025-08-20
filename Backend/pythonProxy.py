from dataclasses import dataclass
import enum
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import quote_plus


### Enums

@enum.unique
class Category(enum.Enum):
    STICKERS = 1
    SKINS = 2
    CASES = 3
    SPECIAL_ITEMS = 4
    MAJOR_STICKER_CAPSULES = 5
    SOUVENIRS = 6
    AUTOGRAPH_CAPSULES = 7
    PASSES = 8
    COLLECTIBLE_PINS = 9
    PATCH_PACKS = 10
    STICKER_CAPSULES = 11
    OTHERS = 12
    PATCHES = 13

    def __str__(self):
        return self.name

### Data Classes

@dataclass
class ItemDefinition:
    Name: str
    Category: Category

@dataclass
class JSONItem:
    ItemDefinition: ItemDefinition
    amount: int = -1


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
start_time = time.time()  # start counting from first fetch

def get_random_proxy():
    return random.choice(PROXY_LIST)

lastSuccessfulProxy = "None"
start_time = time.time()    

def timer(start):
    elapsed_time = time.time() - start
    return elapsed_time

def fetch_price(item: JSONItem, maxRetries=500):
    itemName = item.ItemDefinition.Name
    start_time = time.time()
    lastSuccessfulProxy = None
    tryCounter = 0
    isFetched = False

    response = requests.Response()
    response.status_code = 400  # default "bad request"
    
    while not isFetched:
        # Refresh proxy list every 5 minutes
        if time.time() - start_time > 300:
            PROXY_LIST = get_free_proxies()
            start_time = time.time()

        proxy = get_random_proxy()
        proxies = {"http": proxy, "https": proxy}

        if lastSuccessfulProxy:
            proxies = {"http": lastSuccessfulProxy, "https": lastSuccessfulProxy}
            lastSuccessfulProxy = None

        try:
            encoded_name = quote_plus(itemName)
            response = requests.get(
                f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name={encoded_name}",
                proxies=proxies,
                timeout=5
            )

            if response.ok and len(response.json()) > 1:
                isFetched = True
                lastSuccessfulProxy = proxy

        except requests.RequestException as e:
            pass  # optionally log e

        tryCounter += 1
        if tryCounter >= maxRetries:
            response.status_code = 599  # custom "too many tries"
            isFetched = True
    print(f"Fetched {itemName} in {timer(start_time)}")
    return response



def testFetchViaList(listOfItems, results, id):
    # [JSONItem(ItemDefinition=ItemDefinition(Name='Patch', Category='Patches'), amount=2), ...]
    for item in listOfItems:
        # Known faulty item Patch
        if item.ItemDefinition.Name == "Patch":
            print(f"Skipping empty item in thread {id}")
            continue
        response = fetch_price(item)
        results.append((id, item, response))
        print(f"Thread {id} fetched {item.ItemDefinition.Name} with response: {response.json() if response else 'No response'}")


# Test
def test():
    print(fetch_price(JSONItem(ItemDefinition=ItemDefinition(Name='', Category='Patches'), amount=2)))
    print(fetch_price(JSONItem(ItemDefinition=ItemDefinition(Name='Empty', Category='Patches'), amount=2)))

if __name__ == "__main__":
    NEEDTOTEST = False
    if NEEDTOTEST:
        test()
    else:
        print("Ready to fetch URLs.")