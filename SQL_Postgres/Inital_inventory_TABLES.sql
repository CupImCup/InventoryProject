DROP TABLE IF EXISTS daily_inventory;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;
CREATE TABLE items (
	id BIGINT PRIMARY KEY,
	name TEXT NOT NULL,
    marketable INTEGER DEFAULT 0
);

CREATE TABLE users ( 
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE daily_inventory(
    id SERIAL PRIMARY KEY,
    item_id BIGINT REFERENCES items(id),
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    amount INTEGER NOT NULL,
    price_low_eur NUMERIC(10,2),
    price_median_eur NUMERIC(10,2),
    total_worth_eur NUMERIC(12,2) 
);

CREATE INDEX on daily_inventory(date);
CREATE INDEX on daily_inventory(item_id);

INSERT INTO users(name) VALUES ('thealssla');

--- Sample data

--INSERT INTO items(id, name) VALUES (5710094579, 'Kilowatt Case');
--INSERT INTO users(name) VALUES ('thealssla');

--INSERT INTO daily_inventory(item_id, user_id, date, amount, price_low_eur, price_median_eur, total_worth_eur) VALUES (5710094579, 1, '2025-06-08', 174, 0.61, 0.60, 106.14);