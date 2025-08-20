WITH duplicates AS (
    SELECT 
        id,  -- the unique internal ID
        ROW_NUMBER() OVER (
            PARTITION BY 
                item_id,
				user_id,
                date,
                amount
         
            ORDER BY id  -- keep the lowest ID, for example
        ) AS row_num
    FROM daily_inventory
)

--RUN to view duplicates
SELECT * FROM daily_inventory INNER JOIN items ON daily_inventory.item_id = items.id WHERE daily_inventory.id IN ( SELECT id FROM duplicates WHERE row_num > 1) ORDER BY items.name ASC ;

--RUN to delete duplicates WHERE total_worth = 0
-- i.e. faulty duplicates get deleted with priority
--DELETE FROM daily_inventory WHERE daily_inventory.id IN (     SELECT id    FROM duplicates     WHERE row_num > 1) AND total_worth_eur = 0;

--RUN to delete duplicates
--DELETE FROM daily_inventory WHERE daily_inventory.id IN (     SELECT id    FROM duplicates     WHERE row_num > 1);