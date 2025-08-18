from dataclasses import dataclass
import datetime
import json
from pathlib import Path
from random import random, uniform
import time
from unicodedata import name
import requests
import pickle
import psycopg2
from dotenv import load_dotenv
import os
import pythonProxy


@dataclass
class Item:
    classid: str
    amount: int
    users: str
    name: str = ""
    marketable: int = 0

@dataclass
class jsonItem:
    Stickers: list
    Skins: list
    Cases: list
    Special_Items: list
    Major_Sticker_Capsules: list
    Souvenirs: list
    Autograph_Capsules: list
    Passes: list
    Collectible_Pins: list
    Patch_Packs: list
    Sticker_Capsules: list
    Others: list
    Patches: list

def takeName(elem):
    return dictionary[elem]

# Fetch inventory for every user -> add to dictonary with (user, amount)
# loop through dictionary -> getMarketValue
# Write dictionary in excel file  "Name","Amount","MarketValueSingle","Value * amount", "users"

load_dotenv()  # loads from .env file

users = os.getenv("USERS")
steam_login_secure = os.getenv("STEAM_LOGIN_SECURE")
session_id = os.getenv("SESSION_ID")
steamLoginSecure = os.getenv("STEAM_LOGIN_SECURE")
session_id = os.getenv("SESSION_ID")
changesInInventory = os.getenv("changesInInventory") == "True"
user_id = 1
dictionary = dict()
sorted_dictionary = dict()
#pythonProxy = pythonProxy()

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

with open("Storage_UNIT_inventory.json", "r", encoding="utf-8") as file:
    inventory_data = json.load(file)
database_items = [list(x) for x in database_items]

for category in inventory_data:
    for item_name in inventory_data[category]:
        value = inventory_data[category][item_name] 
        print(item_name, value)
        
        # Find the matching sublist in database_items
        for sublist in database_items:
            if sublist[1] == item_name:
                sublist.append(value)  # Add only to the matching item

print(f"Current items in database: {database_items}")

def fetch_inventory():
    dictionary = {}
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
                    #print("Will try again in 60 seconds")
                    #time.sleep(60)
    else:
        for item in database_items:
            classid = item[0]
            name = item[1]
            amount = item[2] if len(item) > 2 else 1  # Default amount to 1 if not specified
            dictionary[classid] = Item(classid=classid, name=name, amount=amount, users="thealssla", marketable=1)

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
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}
def fetch_market_and_register_daily_inventory(skipUntilSpecificItem, itemToSkipTo):
    today =  datetime.datetime.now()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    d1 = today.replace("-", "").replace(" ", "").replace(":", "")
  
    #old
    sorted_dictionary = fetch_inventory()

    #sorted_dictionary = database_items
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
        specificItemFound = False
        specificItem = itemToSkipTo
        if skipUntilSpecificItem:
            if not specificItemFound:
                if item_obj.name == specificItem:
                    specificItemFound = True
                    skipUntilSpecificItem = False
                    print(f"Found specific item: {item_obj.name}")
                    #continue
                else:
                    print(f"Skipping {item_obj.name}")
                    continue
        while not ISPRICEFETCHED:
            response = pythonProxy.fetch_Url(item_obj.name)
            time.sleep(uniform(1.0, 1.8))
            print("Response received for item:", item_obj.name)
            print(response)
            if response.ok:
                ISPRICEFETCHED = True
                market_data = response.json()
                print(market_data)
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
                #print("Too many requests to the marketplace, waiting 60 seconds.")
                #time.sleep(60)




# For testing purposes only
def manual_adding_of_items():
    # Emergency manual adding of items to the database
    itemJSON = Item(**{'classid': '721396034', 'amount': 1, 'users': 'thealssla', 'name': '★ Flip Knife | Doppler (Factory New)', 'marketable': 1})
    cursor.execute("INSERT INTO items(id, name, marketable) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", (itemJSON.classid, itemJSON.name, itemJSON.marketable))
    connection.commit()
    response = requests.get(
                    f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name={itemJSON.name}"
    )
    today = datetime.today()
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



existing_ids = set()  # replace with your real existing IDs

def generate_class_id(existing_ids):
    while True:
        new_id = random.randint(10_000_000, 99_999_999)  # 8-digit number
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id

def import_inventory_data():
    print(f"Current items in database: {database_items}")
    for x in database_items:
        existing_ids.add(x[0])
    # Import inventory data from JSON file
    with open("Storage_UNIT_inventory.json", "r", encoding="utf-8") as file:
        inventory_data = json.load(file)
    print(f"Inventory data loaded: {inventory_data['Cases']}")
    # Process each item in the inventory data
    for category in inventory_data:
        for item in inventory_data[category]:
            print(item, inventory_data[category][item])
            for x in database_items:
                item_added = False
                print(f"Item ID: {x[0]}, Name: {x[1]}")
                if x[1] == item:
                    print(f"Item {item} found in database.")
                elif not item_added:
                    item_added = True
                    print(f"Item {item} not found in database, adding it.")
                    print("Creating new 8-digit classId that does not exists yet.")
                    new_class_id = generate_class_id(existing_ids)
                    cursor.execute("INSERT INTO items(id, name, marketable) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;", (new_class_id, item, 1))
                    existing_ids.add(new_class_id)   
                    connection.commit()




def main():
    global changesInInventory
    changesInInventory = False  # Set to True to fetch new inventory data
    skipUntilSpecificItem = False  # Set to True to skip the unit item
    itemToSkipTo = "Sticker | kRaSnaL | Paris 2023"  # The item to skip to if skipUntilSpecificItem is True
    register_items_in_database()
    fetch_market_and_register_daily_inventory(skipUntilSpecificItem, itemToSkipTo)
    #manual_adding_of_items()
    #import_inventory_data()
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