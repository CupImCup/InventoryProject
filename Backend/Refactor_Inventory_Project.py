from dataclasses import dataclass
import datetime
import enum
import json
from pathlib import Path
from random import random, uniform
import time
from datetime import date
from unicodedata import name
import psycopg2
from dotenv import load_dotenv
import os
import Threading

### Data Classes

@dataclass
class Item:
    classid: str
    amount: int
    users: str
    name: str = ""
    marketable: int = 0

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

@dataclass 
class ItemDefinition:
    Name: str
    Category: Category

@dataclass
class JSONItem:
    ItemDefinition: ItemDefinition
    amount: int = -1

### Initialization

load_dotenv()  # loads from .env file

listOfFailedItems = []
users = os.getenv("USERS")
steam_login_secure = os.getenv("STEAM_LOGIN_SECURE")
session_id = os.getenv("SESSION_ID")
steamLoginSecure = os.getenv("STEAM_LOGIN_SECURE")
session_id = os.getenv("SESSION_ID")
changesInInventory = os.getenv("changesInInventory") == "True"
user_id = 1
dictionary = dict()
sorted_dictionary = dict()
changesInInventory = False
today =  datetime.datetime.now()
today = today.strftime("%Y-%m-%d %H:%M:%S")
d1 = today.replace("-", "").replace(" ", "").replace(":", "")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Referer": "https://steamcommunity.com/",  # optional but may help
    "Cookie": f"steamLoginSecure={steamLoginSecure}; sessionid={session_id};"
}

# Connect to the PostgreSQL database
connection = psycopg2.connect(database=os.getenv("DB_NAME"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), port=os.getenv("DB_PORT"))
cursor = connection.cursor()

# Get script directory
PATH = Path(__file__).parent

savedDictionaryPath = PATH / 'InventoryTables' / 'TESTsaved_dictionary.pkl'
        
savedDictionaryPath.parent.mkdir(parents=True, exist_ok=True)
database_items = []

### Helper Functions

def sanitize(price_str: str) -> str:
        return price_str[:-1].replace(",", ".").replace("--", "00") if price_str else "0"  

def get_category(category_str: str) -> Category:
    key = category_str.upper().replace(" ", "_")
    try:
        return Category[key]
    except KeyError:
        return Category.OTHERS

def already_in_database_today(item: ItemDefinition, cursor) -> bool:
    """
    Check if an item with the same name and category already exists in new_daily_inventory for today.
    Returns True if a duplicate exists, False otherwise.
    """
    today = date.today()
    cursor.execute(
        """
        SELECT j.name
        FROM jsonitems AS j
        INNER JOIN new_daily_inventory AS di
            ON di.item_name = j.name AND di.item_category = j.category
        WHERE j.name = %s AND j.category = %s AND di.inventory_date = %s;
        """,
        (item.Name, get_category(item.Category).name, today)
    )
    return cursor.fetchone() is not None


def import_inventory_data_from_json():
    # Import inventory data from JSON file
    with open("Storage_UNIT_inventory.json", "r", encoding="utf-8") as file:
        inventory_data = json.load(file)
    # Process each item in the inventory data
    return parse_inventory_dict(inventory_data)

def parse_inventory_dict(inventory_dict: dict) -> list[JSONItem]:
    items = []
    for category_name, entries in inventory_dict.items():
        for item_name, amount in entries.items():
            definition = ItemDefinition(Name=item_name, Category=category_name)
            items.append(JSONItem(ItemDefinition=definition, amount=amount))
    return items

### Main Functions

def fetch_inventory():
    testing = True
    if testing:
       inventory = import_inventory_data_from_json()
    else:
        pass
        # TODO implement steam micro-service
    return inventory

def fetch_item_definitions(cursor) -> list[ItemDefinition]:
    """Load all item definitions (no amount) from DB."""
    cursor.execute("SELECT name, category FROM JSONitems;")
    results = cursor.fetchall()
    return [
        ItemDefinition(name=row[0], category=get_category(row[1]))
        for row in results
    ]

def fetch_prices_of_inventory(inventory):
    responseList = []
    for item in inventory:
        if already_in_database_today(item.ItemDefinition, cursor):
            print(f"Already found an entry for today for : {item.ItemDefinition.Name}. Skipping.")
            inventory.remove(item)
    Threading.threadIt(inventory, responseList)
    return responseList


def index_json_items(connection, cursor, items: list[JSONItem]):
    """Insert new item definitions into DB (ignore if exists)."""
    for item in items:
        defn = item.ItemDefinition
        cursor.execute(
            """
            INSERT INTO JSONitems (name, category)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (defn.Name, get_category(defn.Category).name)  # store enum name
        )
    connection.commit()

def write_inventory_data_to_db(connection, cursor, responseList):
    for response in responseList:
        # response = [threadID, item, item_response]
        # response[0] = 3
        # response[1] = Item(classid=10665862, amount=1, users='thealssla', name='Sticker | Nemiga | 2020 RMR', marketable=1)
        # response[1] = JSONItem(ItemDefinition=ItemDefinition(Name='Sticker | Nemiga | 2020 RMR', Category='Stickers'), amount=1))
        # response[2] = <Response [200]>
        # response[2].json() = {"lowest_price": "€0.50", "median_price": "€0.75"}

        threadID = response[0]
        item = response[1]
        item_response = response[2]
        
        if item_response.ok:
            ISPRICEFETCHED = True
            market_data = item_response.json()
            lowest = market_data.get("lowest_price")
            median = market_data.get("median_price")
            if lowest:
                try:
                    sanitized_lowest = float(sanitize(lowest))
                except ValueError:
                    sanitized_lowest = 0.0
            else:
                sanitized_lowest = 0.0

            sanitized_median = float(sanitize(median)) if median else 0.0
            if sanitized_lowest > 0.0:
                worth = item.amount * sanitized_lowest
            elif sanitized_median > 0.0:
                worth = item.amount * sanitized_median
            else:
                worth = 0.0

            #response[1] = Item(classid=10665862, amount=1, users='thealssla', name='Sticker | Nemiga | 2020 RMR', marketable=1)
            successful = False
            while not successful:
                try:  
                    sql_insert = """
                        INSERT INTO new_daily_inventory (
                            item_name, item_category, user_id, inventory_date, amount, price_low, price_med, total_worth
                        )
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (
                        item.ItemDefinition.Name,
                        get_category(item.ItemDefinition.Category).name,
                        user_id,
                        today,
                        item.amount, 
                        sanitized_lowest,
                        sanitized_median,
                        worth
                    )
                    cursor.execute(sql_insert, data)
                    connection.commit()
                    successful = True
                except Exception as e:
                    print(f"Error inserting data for item: {item.ItemDefinition.Name}, Error: {e}")
                    listOfFailedItems.append(item)
                    connection.rollback()
        else:
            print(f"Failed to fetch market data for item: {item.ItemDefinition.Name}")
            

#get marketvalue of each item
    #https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=markethashname

def main():
    global changesInInventory
    changesInInventory = False  # Set to True to fetch new inventory data

    # Fetch inventory
    inventory = fetch_inventory()  # [{name, category, amount}, ...]

    # Ensure definitions exist
    index_json_items(connection, cursor, inventory)

    # Fetch market prices (dict: name -> price)
    responseList = fetch_prices_of_inventory(inventory)
    write_inventory_data_to_db(connection, cursor, responseList)

    # Close the database connection
    print("List of failed items:")
    print(listOfFailedItems)
    if connection:
        connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Script executed in {end_time - start_time:.2f} seconds.")
    print("Done.")  