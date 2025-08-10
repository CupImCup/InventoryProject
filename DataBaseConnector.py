import psycopg2

connection = psycopg2.connect(database="steam_inventory", user="postgres", password="sudo", port=5432)

cursor = connection.cursor()
{'classid': '1293508920', 'amount': 170, 'users': 'thealssla', 'name': 'Shadow Case', 'marketable': 1},
try:
    #cursor.execute("INSERT INTO items(id,name) VALUES  (1293508920, 'Shadow Case');")
    #cursor.execute("INSERT INTO daily_inventory(item_id, user_id, date, amount, price_low_eur, price_median_eur, total_worth_eur) VALUES (1293508920, 1, '2025-06-08', 170, 0.61, 0.60, 106.14);")
    #connection.commit()
    cursor.execute("SELECT * from items;")
except psycopg2.Error as e:
    print("Error inserting data into database:", e)

# Fetch all rows from database
database_items = cursor.fetchall()

print("Data from Database:- ", database_items)

for item in database_items:

    print(item[0] == 5710094579)
if connection:        
    connection.close()
    print("Database connection closed.")
