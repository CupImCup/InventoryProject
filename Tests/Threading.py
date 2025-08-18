import threading
import time
import random
from Inventoryproject-main.pythonProxy import pythonProxy

def crawl(link, id, delay=3):
    print(f"crawl started for {link} with id {id}")
    print(f"Delay: {delay}")
    time.sleep(delay)  # Blocking I/O (simulating a network request)

    print(f"crawl ended for {link} with id {id}")

links = ["Austin 2025 Dust II Souvenir Highlight Package",
"Austin 2025 Mirage Souvenir Highlight Package",
"Sticker | Virtus.Pro | Atlanta 2017",
"Sticker | FaZe Clan | Atlanta 2017",
"Sticker | Fnatic | Atlanta 2017",
"Sticker | FaZe Clan | Boston 2018",
"Sticker | Cloud9 | Katowice 2019",
"Sticker | FaZe Clan | Katowice 2019",
"Sticker | Battle Scarred (Holo)",
"Sticker | Battle Scarred"]

print("Total links to crawl:", len(links))
threshold = 2
chunkList = []
for i in range(0, len(links), threshold):
    # Process links in chunks
    chunkList.append(links[i:i + threshold])
print(f"Final Chunklist {chunkList}")
print("Total chunks:", len(chunkList))


# Start threads for each link
threads = []
id = 0
for link in chunkList:
    # Using `args` to pass positional arguments and `kwargs` for keyword arguments
    t = threading.Thread(target=pythonProxy.testFetchViaList, args=(link,))
    threads.append(t)
    id += 1

# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()