import requests

response = requests.get("https://csfloat.com/api/v1/listings")
print("Status Code:", response.status_code)
if response.ok:
    data = response.json()
    print("Data fetched successfully.")
    print(data)