import requests
from bs4 import BeautifulSoup
import random
import time

# Step 1: Fetch free proxy list
def get_free_proxies():
    url = "https://free-proxy-list.net/"  # public free proxies
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    proxies = []
    print(f"Fetched proxies: {soup}")
    # Kids, do not do it like this
    firstShave = response.text.split('UTC.')[1]
    print("First shave:")
    print(firstShave)
    secondShave = firstShave.split('</textarea>')[0]
    print("Second shave:")
    print(secondShave)
    for line in secondShave.split('\n'):
        if line.strip() and not line.startswith('#'):
            proxies.append(line.strip())
    return proxies

# Step 2: Create a rotating proxy list
# Initial proxy fetch
PROXY_LIST = get_free_proxies()
start_time = time.time()  # start counting from first fetch
'''PROXY_LIST = [
    "66.36.234.130:1339",
    "124.6.51.227:8099",
    "85.133.240.75:8080",
    "42.118.1.72:16000",
    "223.135.156.183:8080",
    "165.154.36.27:10080",
    "117.54.114.98:80",
    "152.53.107.230:80",
    "154.118.231.30:80",
    "38.54.71.67:80",
    "139.59.1.14:80",
    "159.203.61.169:3128",
    "42.118.2.137:16000",
    "57.129.81.201:8080",
    "116.203.56.216:2212",
    "138.68.60.8:80",
    "27.79.176.68:16000",
    "41.59.90.175:80",
    "40.192.110.77:51773",
    "154.236.177.102:1977",
    "139.162.78.109:8080",
    "202.232.52.162:8080",
    "147.75.34.105:443",
    "134.209.29.120:80",
    "47.74.157.194:80",
    "41.59.90.171:80",
    "198.74.51.79:8888",
    "41.59.90.168:80",
    "27.79.178.6:16000",
    "219.93.101.60:80",
    "95.47.239.75:3128",
    "140.238.64.65:80",
    "5.45.126.128:8080",
    "192.73.244.36:80",
    "176.126.103.194:44214",
    "47.251.43.115:33333",
    "8.219.97.248:80",
    "190.103.177.131:80",
    "82.102.10.253:80",
    "27.71.129.110:16000",
    "27.71.139.208:16000",
    "123.30.154.171:7777",
    "188.166.197.129:3128",
    "32.223.6.94:80",
    "133.18.234.13:80",
    "181.174.164.221:80",
    "190.58.248.86:80",
    "50.122.86.118:80",
    "23.247.136.248:80",
    "200.174.198.86:8888",
    "4.245.123.244:80",
    "92.67.186.210:80",
    "45.146.163.31:80",
    "124.108.6.20:8085",
    "59.7.246.4:80",
    "201.148.32.162:80",
    "90.162.35.34:80",
    "123.141.181.49:5031",
    "91.107.147.219:80",
    "41.191.203.162:80",
    "89.58.55.33:80",
    "219.65.73.81:80",
    "159.69.57.20:8880",
    "89.58.57.45:80",
    "152.53.168.53:44887",
    "123.141.181.1:5031",
    "157.180.121.252:46206",
    "89.19.175.122:8008",
    "103.94.52.70:3128",
    "123.141.181.53:5031",
    "116.105.31.185:9100",
    "161.35.70.249:8080",
    "198.199.86.11:8080",
    "113.160.132.195:8080",
    "123.141.181.84:5031",
    "123.141.181.7:5031",
    "154.62.226.126:8888",
    "4.156.78.45:80",
    "47.252.29.28:11222",
    "38.147.98.190:8080",
    "23.247.136.254:80",
    "4.195.16.140:80",
    "108.141.130.146:80",
    "195.158.8.123:3128",
    "62.99.138.162:80",
    "189.202.188.149:80",
    "41.191.203.161:80",
    "152.53.194.55:21609",
    "213.143.113.82:80",
    "185.82.218.85:80",
    "198.49.68.80:80",
    "85.239.144.149:8080",
    "35.197.89.213:80",
    "104.222.32.98:80",
    "219.93.101.63:80",
    "0.0.0.0:80",
    "97.74.87.226:80",
    "68.185.57.66:80",
    "127.0.0.7:80",
    "209.97.150.167:8080",
    "200.39.60.34:999",
    "46.161.194.86:8085",
    "123.20.50.125:8080",
    "122.52.234.54:8081",
    "90.156.194.70:8026",
    "103.187.162.75:8085",
    "152.32.77.213:8095",
    "193.43.145.250:8080",
    "213.132.76.9:8081",
    "102.135.198.94:8082",
    "187.251.130.140:8080",
    "103.228.246.199:1111",
    "78.9.232.205:8080",
    "121.101.132.39:8080",
    "103.155.198.142:1080",
    "103.165.64.53:82",
    "180.190.188.183:8082",
    "77.51.222.239:8080",
    "124.106.151.205:8082",
    "190.153.22.149:999",
    "103.134.220.145:8080",
    "175.100.91.80:8080",
    "190.15.211.43:8080",
    "103.231.236.239:8182",
    "103.189.251.81:1111",
    "58.147.187.20:8080",
    "103.48.68.68:83",
    "86.100.108.89:8091",
    "190.97.230.198:999",
    "187.19.198.130:8080",
    "103.125.154.233:8080"]
'''
def get_random_proxy():
    return random.choice(PROXY_LIST)



lastSuccessfulProxy = "None"
start_time = time.time()    

def timer(start):
    elapsed_time = time.time() - start
    return elapsed_time

def fetch_Url(itemName):
    global lastSuccessfulProxy
    global start_time  
    
    isFetched = False
    while not isFetched:
        # Refetch proxies if more than 5 minutes have passed
        if timer(start_time) > 300:
            PROXY_LIST = get_free_proxies()
            start_time = time.time()
        proxy = get_random_proxy()
        print("Using proxy:", proxy)
        print("Fetching URL for item:", itemName)
        proxies = {"http": proxy, "https": proxy}
        try:
            if lastSuccessfulProxy != "None":
                print("Last successful proxy:", lastSuccessfulProxy)
                proxies = {"http": lastSuccessfulProxy, "https": lastSuccessfulProxy}
                lastSuccessfulProxy = "None"
            response = requests.get(f"https://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name={itemName}",
                                    proxies=proxies, timeout=1)
            isFetched = True
            lastSuccessfulProxy = proxy
            return response
        except Exception as e:
            print("Request failed:", e)


# Test
def test():
    print(fetch_Url("Glove Case"))
    print(fetch_Url("Gallery Case"))

if __name__ == "__main__":
    NEEDTOTEST = False
    if NEEDTOTEST:
        test()
    else:
        print("Ready to fetch URLs.")