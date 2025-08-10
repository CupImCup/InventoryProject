from dataclasses import dataclass
from datetime import date
from pathlib import Path
from random import random, uniform
import time
from unicodedata import name
import requests
import pickle
import psycopg2

@dataclass
class Item:
    classid: str
    amount: int
    users: str
    name: str
    marketable: int

def takeName(elem):
    return dictionary[elem]["name"]

# Fetch inventory for every user -> add to dictonary with (user, amount)
# loop through dictionary -> getMarketValue
# Write dictionary in excel file  "Name","Amount","MarketValueSingle","Value * amount", "users"


#users = ["CasesAmStoren", "Undisputed_62","thealssla", "SWAG-StoreHustler", "CashflowAmLaufenErhalten"]
users = ["thealssla"]
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
    "Cookie": "steamLoginSecure=76561198107140685%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MDAwN18yNjkxRUNCMV84MUNCQSIsICJzdWIiOiAiNzY1NjExOTgxMDcxNDA2ODUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3NTQ1MTI4OTMsICJuYmYiOiAxNzQ1Nzg1MjE5LCAiaWF0IjogMTc1NDQyNTIxOSwgImp0aSI6ICIwMDA4XzI2Qjk0QjVEX0ZEQUY1IiwgIm9hdCI6IDE3NTIwMDQ2NjEsICJydF9leHAiOiAxNzcwMDE4NDExLCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTQxLjcyLjIzMS4yMjAiLCAiaXBfY29uZmlybWVyIjogIjE0MS43Mi4yMzEuMjIwIiB9.2ZdVXbMj2GUvqmCtuldXn6CmUUtSiMsDIPnwGNYUwf9QfxBdAfrgjVNDi0WPXOjSv-9HR-vsAQEcFXuYL9OaDQ; sessionid=15de0fcbfad05405a14a7c0b; steamCountry=DE%7C123abc..."
}

# Connect to the PostgreSQL database
connection = psycopg2.connect(database="steam_inventory", user="postgres", password="sudo", port=5432)
cursor = connection.cursor()

QUERY_CURRENT_ITEMS = "SELECT id, name FROM items;"

database_items = cursor.execute(QUERY_CURRENT_ITEMS).fetchall()

changesInInventory = False

# Get script directory
PATH = Path(__file__).parent

# Correct way to build the full path
savedDictionaryPath = PATH / 'InventoryTables' / 'saved_dictionary.pkl'

# Create folder if it doesn't exist
savedDictionaryPath.parent.mkdir(parents=True, exist_ok=True)

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
                print(user)
                invData = inventory.json()
                # counting amount and users of each unique item 
                for attr in invData["rgInventory"]:
                    if invData["rgInventory"][attr]["classid"] not in dictionary:
                        dictionary[invData["rgInventory"][attr]["classid"]] = {"classid": invData["rgInventory"][attr]["classid"], "amount": 1, "users": user}
                    else :
                        dictionary[invData["rgInventory"][attr]["classid"]]["amount"] = dictionary[invData["rgInventory"][attr]["classid"]]["amount"] + 1
                        if user not in dictionary[invData["rgInventory"][attr]["classid"]]["users"]:
                            dictionary[invData["rgInventory"][attr]["classid"]] = {"classid": invData["rgInventory"][attr]["classid"],
                                                                                    "amount": dictionary[invData["rgInventory"][attr]["classid"]]["amount"],
                                                                                    "users": dictionary[invData["rgInventory"][attr]["classid"]]["users"] + "; " + user}
                
                #adding metadata to the counted items
                for attr in invData["rgDescriptions"]:
                    if invData["rgDescriptions"][attr]["classid"] in dictionary:
                        print(dictionary[invData["rgDescriptions"][attr]["classid"]])
                        dictionary[invData["rgDescriptions"][attr]["classid"]] = {  "classid": dictionary[invData["rgDescriptions"][attr]["classid"]]["classid"],
                                                                                    "amount": dictionary[invData["rgDescriptions"][attr]["classid"]]["amount"],
                                                                                    "users": dictionary[invData["rgDescriptions"][attr]["classid"]]["users"], 
                                                                                    "name": invData["rgDescriptions"][attr]["market_hash_name"],
                                                                                    "marketable": invData["rgDescriptions"][attr]["marketable"]}
                    else:
                        print(hasattr(invData["rgDescriptions"][attr], "classid"))
                        print("No such thing as a classid in attribute " + attr)
                        print(invData["rgDescriptions"][attr]["classid"])
                        print(dictionary[invData["rgDescriptions"][attr]["classid"]])
                        print(invData["rgDescriptions"][attr]["market_hash_name"])
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
for item in sorted(dictionary, key=takeName):
    sorted_dictionary[item] = dictionary[item]
#save most recent Inventory to file
with open(savedDictionaryPath, 'wb') as f:
    pickle.dump(sorted_dictionary, f)
    print("Most recent dictionary version saved successfully")



# save most recent dictionary, so that it can be used when there haven't been any changes


#get marketvalue of each item
    #https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=markethashname



today = date.today()
d1 = today.strftime("%d%m%Y")

# This will safely construct: PATH/InventoryTables/inventory/05082025.csv
dataStrPath = PATH / 'InventoryTables' / 'inventory' / f'{d1}.csv'
# Ensure parent directories exist
dataStrPath.parent.mkdir(parents=True, exist_ok=True)
ISPRICEFETCHED = False

with open(dataStrPath, 'w+', newline ='\n') as csvfile:
    csvfile.write("Name,Amount,Lowest price in Euro,Median price in Euro,Total worth in Euro,User" + "\n")
    TOTALSUM = 0
    #for debug print sorted
    print("Sorted dictionary:")
    print(sorted_dictionary)
    print("Total items in inventory: " + str(len(sorted_dictionary)))
    for item in sorted_dictionary:
        if dictionary[item]["marketable"] == 1:
            ISPRICEFETCHED = False
            while not ISPRICEFETCHED:
                response = requests.get("https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=" + dictionary[item]["name"])
                time.sleep(uniform(1.0, 1.8))
                if response.ok:
                    ISPRICEFETCHED = True
                    marketItem = response.json()
                    print(marketItem)
                    if "lowest_price" in marketItem:
                        if "median_price" in marketItem:
                            worth = dictionary[item]["amount"] * float(marketItem["lowest_price"][:-1].replace(",",".").replace("--", "00"))
                            TOTALSUM += worth
                            print(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ marketItem['lowest_price'].replace(",",".").replace("--", "00") +","+ marketItem['median_price'].replace(",",".").replace("--", "00")+","+str(worth) +","+ dictionary[item]["users"] + "\n")
                            csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ marketItem['lowest_price'].replace(",",".").replace("--", "00") +","+ marketItem['median_price'].replace(",",".").replace("--", "00")+","+str(worth) +","+ dictionary[item]["users"] + "\n")
                        else:
                            worth = dictionary[item]["amount"] * float(marketItem["lowest_price"][:-1].replace(",",".").replace("--", "00"))
                            TOTALSUM += worth
                            print(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+  marketItem['lowest_price'].replace(",",".").replace("--", "00") + ",0" +","+","+str(worth) +","+ dictionary[item]["users"] + "\n")
                            csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ marketItem['lowest_price'].replace(",",".").replace("--", "00")+ ",0" +","+","+str(worth) +","+ dictionary[item]["users"] + "\n")
                    else:
                        #Neither lowest price nor median price available
                        print("Neither lowest price nor median price available for " + dictionary[item]["name"])
                        csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ "-" +","+ "-" +","+ "0" +","+ dictionary[item]["users"] + "\n")
              
                else: 
                    print("There was a problem trying to fetch the price of " + dictionary[item]["name"])
                    print("Status code: " + str(response.status_code))
                    print("Too many requests to the market place, waiting 60 seconds.")
                    time.sleep(60)
                
        else:
            print(dictionary[item]["name"] + " is not a marketable item. Skipping this one.")
                     
    print("Total worth for " + str(today) + " amounts to: " + str(TOTALSUM))
    csvfile.write(","+","+","+","+ str(TOTALSUM) +","+ "\n")    




