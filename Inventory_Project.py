from datetime import date
from pathlib import Path
import time
from unicodedata import name
import requests
import pickle

def takeName(elem):
    return dictionary[elem]["name"]

# Fetch inventory for every user -> add to dictonary with (user, amount)
# loop through dictionary -> getMarketValue
# Write dictionary in excel file  "Name","Amount","MarketValueSingle","Value * amount", "users"


users = ["CasesAmStoren", "Undisputed_62","thealssla", "SWAG-StoreHustler", "CashflowAmLaufenErhalten"]
#users = ["76561198368317147"]
dictionary = dict()
sorted_dictionary = dict()
PATH = str(Path(__file__).parent)
savedDictionaryPath = PATH + '\InventoryTables\saved_dictionary.pkl'

changesInInventory = True

if(changesInInventory):
    ISFAIRREQUEST = False
    for user in users:
        ISFAIRREQUEST = False
        while not ISFAIRREQUEST:
            inventory = requests.get("https://steamcommunity.com/id/"+ user +"/inventory/json/730/2")
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
    #sort inventory
    for item in sorted(dictionary, key=takeName):
        sorted_dictionary[item] = dictionary[item]
    #save most recent Inventory to file
    with open(savedDictionaryPath, 'wb') as f:
        pickle.dump(sorted_dictionary, f)
        print("Most recent dictionary version saved successfully")
else:
    #Load inventory from file
    with open(savedDictionaryPath, 'rb') as f:
        dictionary = pickle.load(f)
        print("Most recent dictionary loaded from disk")



# save most recent dictionary, so that it can be used when there haven't been any changes


#get marketvalue of each item
    #https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=markethashname


today = date.today()

d1 = today.strftime("%d%m%Y")

dataStrPath = PATH + '\InventoryTables\inventory'+d1+'.csv'

ISPRICEFETCHED = False

with open(dataStrPath, 'w+', newline ='\n') as csvfile:
    csvfile.write("Name,Amount,Lowest price in €,Median price in €,Total worth in €,User" + "\n")
    TOTALSUM = 0
    for item in sorted_dictionary:
        if dictionary[item]["marketable"] == 1:
            ISPRICEFETCHED = False
            while not ISPRICEFETCHED:
                response = requests.get("https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=" + dictionary[item]["name"])
                if response.ok:
                    ISPRICEFETCHED = True
                    marketItem = response.json()
                    print(marketItem)
                    if "lowest_price" in marketItem:
                        if "median_price" in marketItem:
                            worth = dictionary[item]["amount"] * float(marketItem["lowest_price"][:-1].replace(",",".").replace("--", "00"))
                            TOTALSUM += worth
                            print(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ marketItem['lowest_price'].replace(",",".").replace("--", "00") +","+ marketItem['median_price'].replace(",",".").replace("--", "00")+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                            csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ marketItem['lowest_price'].replace(",",".").replace("--", "00") +","+ marketItem['median_price'].replace(",",".").replace("--", "00")+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                        else:
                            worth = dictionary[item]["amount"] * float(marketItem["lowest_price"][:-1].replace(",",".").replace("--", "00"))
                            TOTALSUM += worth
                            print(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+  marketItem['lowest_price'].replace(",",".").replace("--", "00") + "0" +","+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                            csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ marketItem['lowest_price'].replace(",",".").replace("--", "00")+ "0" +","+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                    else:
                        worth = dictionary[item]["amount"] * float(marketItem["median_price"][:-1].replace(",",".").replace("--", "00"))
                        TOTALSUM += worth
                        print(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+  "0" + marketItem['median_price'].replace(",",".").replace("--", "00") +","+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                        csvfile.write(dictionary[item]["name"].replace('★ ', "").replace('StatTrak™', "StatTrak") +","+ str(dictionary[item]["amount"]) +","+ "0"+ marketItem['median_price'].replace(",",".").replace("--", "00") +","+","+str(worth) +"€,"+ dictionary[item]["users"] + "\n")
                else: 
                    print("There was a problem trying to fetch the price of " + dictionary[item]["name"])
                    print("Status code: " + str(response.status_code))
                    print("Too many requests to the market place, waiting 60 seconds.")
                    time.sleep(60)
                
        else:
            print(dictionary[item]["name"] + " is not a marketable item. Skipping this one.")
    print("Total worth for " + str(today) + " amounts to: " + str(TOTALSUM))
    csvfile.write(","+","+","+","+ str(TOTALSUM) +"€,"+ "\n")    
