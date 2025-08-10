from datetime import date
from pathlib import Path
import time
import requests

# Fetch inventory for every user -> add to dictonary with (user, amount)
# loop through dictionary -> getMarketValue
# Write dictionary in excel file  "Name","Amount","MarketValueSingle","Value * amount", "users"

users = ["CasesAmStoren", "Undisputed_62","thealssla", "SWAG-StoreHustler", "CashflowAmLaufenErhalten"]
#users = ["thealssla"]
dictionary = dict()
ISFAIRREQUEST = False
for user in users:
    ISFAIRREQUEST = False
    while not ISFAIRREQUEST:
        inventory = requests.get("https://steamcommunity.com/id/"+ user +"/inventory/json/730/2")
        if inventory.ok:
            ISFAIRREQUEST = True
            print(inventory.status_code)
            print(user)
            invData = inventory.json()
            for attr in invData["rgInventory"]:
                if invData["rgInventory"][attr]["classid"] not in dictionary:
                    dictionary[invData["rgInventory"][attr]["classid"]] = {"classid": invData["rgInventory"][attr]["classid"], "amount": 1, "users": user}
                else :
                    dictionary[invData["rgInventory"][attr]["classid"]]["amount"] = dictionary[invData["rgInventory"][attr]["classid"]]["amount"] + 1
                    if user not in dictionary[invData["rgInventory"][attr]["classid"]]["users"]:
                        dictionary[invData["rgInventory"][attr]["classid"]] = {"classid": invData["rgInventory"][attr]["classid"], "amount": dictionary[invData["rgInventory"][attr]["classid"]]["amount"], "users": dictionary[invData["rgInventory"][attr]["classid"]]["users"] + "; " + user}
            for attr in invData["rgDescriptions"]:
                if invData["rgDescriptions"][attr]["classid"] in dictionary:
                    print(dictionary[invData["rgDescriptions"][attr]["classid"]])
                    dictionary[invData["rgDescriptions"][attr]["classid"]] = {"classid": dictionary[invData["rgDescriptions"][attr]["classid"]]["classid"],
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
            print(inventory.status_code)
            print("Will try again in 60 seconds")
            time.sleep(60)

for item in dictionary:
    print(dictionary[item])

#get marketvalue of each item
    #https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=markethashname


today = date.today()

d1 = today.strftime("%d%m%Y")


PATH = str(Path(__file__).parent)
strPath = PATH + '\InventoryTables\inventory'+d1+'.csv'
print(PATH)
print(strPath)

ISPRICEFETCHED = False

with open(strPath, 'w+', newline ='\n') as csvfile:
    csvfile.write("Name,Amount,Lowest price in €,Median price in €,Total worth in €,User" + "\n")
    TOTALSUM = 0
    for item in dictionary:
        if dictionary[item]["marketable"] == 1:
            ISPRICEFETCHED = False
            while not ISPRICEFETCHED:
                response = requests.get("https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=" + dictionary[item]["name"])
                if response.ok:
                    ISPRICEFETCHED = True
                    marketItem = response.json()
                    print(marketItem)
                    if hasattr(marketItem, "lowest_price"):
                        worth = dictionary[item]["amount"] * float(marketItem["lowest_price"][:-1].replace(",","."))
                        TOTALSUM += worth
                        print(dictionary[item]["name"] +","+ str(dictionary[item]["amount"]) +","+ marketItem["lowest_price"].replace(",",".") +","+ marketItem['median_price'].replace(",",".")+","+ str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                        csvfile.write(dictionary[item]["name"] +","+ str(dictionary[item]["amount"]) +","+ marketItem["lowest_price"].replace(",",".") +","+ marketItem['median_price'].replace(",",".")+","+ str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                    else:
                        worth = dictionary[item]["amount"] * float(marketItem["median_price"][:-1].replace(",","."))
                        TOTALSUM += worth
                        print(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ "0" +","+ marketItem['median_price'].replace(",",".")+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                        csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ "0" +","+ marketItem['median_price'].replace(",",".")+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                else:
                    print("There was a problem trying to fetch the price of " + dictionary[item]["name"])
                    print(response.status_code)
                    print("Too many requests to the market place, waiting 60 seconds.")
                    time.sleep(60)
        else:
            print(dictionary[item]["name"] + " is not a tradeable item. Skipping this one.")

    csvfile.write(","+","+","+","+ str(TOTALSUM) +"€,"+ "\n")
    