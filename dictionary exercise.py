import pickle
from pathlib import Path

dictionary = dict()
loaded_dict = dict()

dictionary[3213411179] = {'classid': '3213411179', 'amount': 15, 'users': 'CasesAmStoren; thealssla', 'name': 'Prisma Case', 'marketable': 1}
dictionary[2727227113] = {'classid': '2727227113', 'amount': 40, 'users': 'CasesAmStoren; thealssla', 'name': 'Clutch Case', 'marketable': 1}

PATH = str(Path(__file__).parent)
strPath = PATH + '\InventoryTables\saved_dictionary.pkl'

for item in dictionary:
    print(dictionary[item])

with open(strPath, 'wb') as f:
    pickle.dump(dictionary, f)
    print("saved successfully")
        
with open(strPath, 'rb') as f:
    loaded_dict = pickle.load(f)
    print("loaded successfully")

for item in loaded_dict:
    print(loaded_dict[item])