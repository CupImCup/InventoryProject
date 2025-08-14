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
DELETE FROM daily_inventory
WHERE id IN (
    SELECT id
    FROM duplicates
    WHERE row_num > 1
);