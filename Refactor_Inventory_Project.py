from dataclasses import dataclass
import datetime
from pathlib import Path
from random import random, uniform
import time
from unicodedata import name
import requests
import pickle
import psycopg2
from dotenv import load_dotenv
import os


@dataclass
class Item:
    classid: str
    amount: int
    users: str
    name: str = ""
    marketable: int = 0

def takeName(elem):
    return dictionary[elem]

# Fetch inventory for every user -> add to dictonary with (user, amount)
# loop through dictionary -> getMarketValue
# Write dictionary in excel file  "Name","Amount","MarketValueSingle","Value * amount", "users"

load_dotenv()  # loads from .env file

users = os.getenv("USERS").split(",")
steam_login_secure = os.getenv("STEAM_LOGIN_SECURE")
session_id = os.getenv("SESSION_ID")
steamLoginSecure = os.getenv("STEAM_LOGIN_SECURE")
session_id = os.getenv("SESSION_ID")
changesInInventory = os.getenv("changesInInventory") == "True"
user_id = 1
dictionary = dict()
sorted_dictionary = dict()

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


changesInInventory = False

# Get script directory
PATH = Path(__file__).parent

# Correct way to build the full path
savedDictionaryPath = PATH / 'InventoryTables' / 'TESTsaved_dictionary.pkl'

# Create folder if it doesn't exist
savedDictionaryPath.parent.mkdir(parents=True, exist_ok=True)

QUERY_CURRENT_ITEMS = "SELECT id, name FROM items;"
cursor.execute(QUERY_CURRENT_ITEMS)
database_items = cursor.fetchall()

def fetch_inventory():
    if(changesInInventory):
        ISFAIRREQUEST = False
        for user in users:
            print(user)
            url = "https://steamcommunity.com/id/TheAlssla/inventory/json/730/2"    
            ISFAIRREQUEST = False
            while not ISFAIRREQUEST:
                inventory = requests.get(url, headers=headers)
                if inventory.ok:
                    ISFAIRREQUEST = True
                    print("Status code: " + str(inventory.status_code))
                    invData = inventory.json()
                    dictionary = {}

                    # Step 1: Count amount and collect user info for each classid
                    for item in invData["rgInventory"].values():
                        classid = item["classid"]
                        if classid not in dictionary:
                            dictionary[classid] = Item(classid=classid, amount=1, users=user)
                        else:
                            dictionary[classid].amount += 1
                            if user not in dictionary[classid].users:
                                dictionary[classid].users += f"; {user}"

                    # Step 2: Add metadata from descriptions
                    for desc in invData["rgDescriptions"].values():
                        classid = desc.get("classid")
                        if classid in dictionary:
                            dictionary[classid].name = desc.get("market_hash_name", "")
                            dictionary[classid].marketable = desc.get("marketable", 0)
                        else:
                            # Optional: logging/debug info
                            print(f"No item with classid {classid} found in dictionary")
                            print(f"Full description: {desc}")
                else:
                    print("Status code: " + str(inventory.status_code))
                    print("Will try again in 60 seconds")
                    time.sleep(60)
    else:
        #Load inventory from file
        with open(savedDictionaryPath, 'rb') as f:
            dictionary = pickle.load(f)
            print("Most recent dictionary loaded from disk")

    #sort inventory
    for item in sorted(dictionary, key=lambda x: dictionary[x].name):
        sorted_dictionary[item] = dictionary[item]
    #save most recent Inventory to file
    with open(savedDictionaryPath, 'wb') as f:
        pickle.dump(sorted_dictionary, f)
        print("Most recent dictionary version saved successfully")

    return sorted_dictionary


def register_items_in_database():
    sorted_dictionary = fetch_inventory()
    # Check if items in sorted_dictionary are already in database
    for item in sorted_dictionary:
        if sorted_dictionary[item].classid not in [i[0] for i in database_items]:
            #  Try to Insert new item into the database
            cursor.execute("INSERT INTO items(id, name, marketable) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", (sorted_dictionary[item].classid, sorted_dictionary[item].name, sorted_dictionary[item].marketable))
            if cursor.rowcount == 0:
                print(f"Item {sorted_dictionary[item].name} with classid {sorted_dictionary[item].classid} already exists in the database.")
            else:
                print(f"Item {sorted_dictionary[item].name} with classid {sorted_dictionary[item].classid} added to the database.")
            connection.commit()



# save most recent dictionary, so that it can be used when there haven't been any changes


#get marketvalue of each item
    #https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=markethashname


def fetch_market_and_register_daily_inventory():
    today =  datetime.datetime.now()


    today = today.strftime("%Y-%m-%d %H:%M:%S")
    d1 = today.replace("-", "").replace(" ", "").replace(":", "")
    sorted_dictionary = fetch_inventory()
    # This will safely construct: PATH/InventoryTables/inventory/05082025.csv
    dataStrPath = PATH / 'InventoryTables' / 'inventory' / f'{d1}.csv'
    # Ensure parent directories exist
    dataStrPath.parent.mkdir(parents=True, exist_ok=True)

    ISPRICEFETCHED = False
    TOTALSUM = 0
    #for debug print sorted
    print("Sorted dictionary:")
    print(sorted_dictionary)
    print("Unique items in inventory: " + str(len(sorted_dictionary)))
    for classid in sorted_dictionary:
        item_obj = sorted_dictionary[classid]
        if item_obj.marketable != 1:
            print(f"{item_obj.name} is not a marketable item. Skipping this one.")
            continue

        ISPRICEFETCHED = False
        while not ISPRICEFETCHED:
            response = requests.get(
                f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name={item_obj.name}"
            )
            time.sleep(uniform(1.0, 1.8))

            if response.ok:
                ISPRICEFETCHED = True
                market_data = response.json()
                #print(market_data)

                lowest = market_data.get("lowest_price")
                median = market_data.get("median_price")

                def sanitize(price_str: str) -> str:
                    return price_str[:-1].replace(",", ".").replace("--", "00") if price_str else "0"

                if lowest:
                    try:
                        sanitized_lowest = float(sanitize(lowest))
                    except ValueError:
                        sanitized_lowest = 0.0
                else:
                    sanitized_lowest = 0.0

                sanitized_median = float(sanitize(median)) if median else 0.0
                if sanitized_lowest > 0.0:
                    worth = item_obj.amount * sanitized_lowest
                elif sanitized_median > 0.0:
                    worth = item_obj.amount * sanitized_median
                else:
                    worth = 0.0

                TOTALSUM += worth

                item_name_clean = item_obj.name.replace('★ ', "").replace('StatTrak™', "StatTrak")
                #
                sql_insert = """
                    INSERT INTO daily_inventory (
                        item_id, user_id, date, amount, price_low_eur, price_median_eur, total_worth_eur
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                data = (
                    classid,
                    user_id,
                    today,
                    item_obj.amount,
                    sanitized_lowest,
                    sanitized_median,
                    worth
                )
                cursor.execute(sql_insert, data)
                connection.commit()
                print(f"Inserted {item_name_clean} into daily_inventory with amount {item_obj.amount} and worth {worth:.2f} EUR.")


            else:
                print(f"There was a problem trying to fetch the price of {item_obj.name}")
                print(f"Status code: {response.status_code}")
                print("Too many requests to the marketplace, waiting 60 seconds.")
                time.sleep(60)




# For testing purposes only
def manual_adding_of_items():
    # Emergency manual adding of items to the database
    itemJSON = Item(**{'classid': '721396034', 'amount': 1, 'users': 'thealssla', 'name': '★ Flip Knife | Doppler (Factory New)', 'marketable': 1})
    cursor.execute("INSERT INTO items(id, name, marketable) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", (itemJSON.classid, itemJSON.name, itemJSON.marketable))
    connection.commit()
    response = requests.get(
                    f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name={itemJSON.name}"
    )
    today = date.today()
    d1 = today.strftime("%d%m%Y")
    if response.ok:
        ISPRICEFETCHED = True
        market_data = response.json()
        print(market_data)

        lowest = market_data.get("lowest_price")
        median = market_data.get("median_price")

        def sanitize(price_str: str) -> str:
            return price_str[:-1].replace(",", ".").replace("--", "00").replace(" ","") if price_str else "0"

        if lowest:
            try:
                sanitized_lowest = float(sanitize(lowest))
            except ValueError:
                sanitized_lowest = 0.0
        else:
            sanitized_lowest = 0.0

        sanitized_median = float(sanitize(median)) if median else 0.0
        if sanitized_lowest > 0.0:
            worth = itemJSON.amount * sanitized_lowest
        elif sanitized_median > 0.0:
            worth = itemJSON.amount * sanitized_median
        else:
            worth = 0.0

        item_name_clean = itemJSON.name.replace('★ ', "").replace('StatTrak™', "StatTrak")
        #
        sql_insert = """
            INSERT INTO daily_inventory (
                item_id, user_id, date, amount, price_low_eur, price_median_eur, total_worth_eur
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        data = (
            itemJSON.classid,
            user_id,
            today,
            itemJSON.amount,
            sanitized_lowest,
            sanitized_median,
            worth
        )
        cursor.execute(sql_insert, data)
        print(f"Inserted {item_name_clean} into daily_inventory with amount {itemJSON.amount} and worth {worth:.2f} EUR.")
        connection.commit()
    else:
        print(f"There was a problem trying to fetch the price of {itemJSON.name}")
        print(f"Status code: {response.status_code}")


def main():
    global changesInInventory
    changesInInventory = False  # Set to True to fetch new inventory data
    
    register_items_in_database()
    fetch_market_and_register_daily_inventory()
    #manual_adding_of_items()

    # Close the database connection
    if connection:
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Script executed in {end_time - start_time:.2f} seconds.")
    print("Done.")  