SELECT * FROM items  INNER JOIN daily_inventory as di on di.item_id = items.id INNER JOIN users ON users.id = di.user_id WHERE Date = CuRRENT_DATE;


