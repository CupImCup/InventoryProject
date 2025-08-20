from asyncio import threads
import threading
from pythonProxy import testFetchViaList

def chunkTheList(list):
    chunkedList = []
    threshold = 2
    for i in range(0, len(list), threshold):
        chunkedList.append(list[i:i + threshold])
    return chunkedList

def threadIt(FullList, results):
    # Start threads for each link
    threads = []
    #[Item(classid=4956553487, amount=0, users='thealssla', name='10 Year Birthday Coin', marketable=1), ... ]
    # [JSONItem(ItemDefinition=ItemDefinition(Name='Patch', Category='Patches'), amount=2), ...]
    id = 0
    chunkList = chunkTheList(FullList)
    for linkList in chunkList:
        # Using `args` to pass positional arguments and `kwargs` for keyword arguments
        t = threading.Thread(target=testFetchViaList, args=(linkList, results, id))
        #t = threading.Thread(target=crawl, args=(linkList, results, id))
        threads.append(t)
        id += 1

    # Start each thread
    for t in threads:
        t.start()
        
    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("All threads have finished execution.")
    print("Results:", results)
    return results
