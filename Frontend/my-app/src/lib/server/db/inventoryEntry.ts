import { pgTable, serial, integer } from 'drizzle-orm/pg-core';

export const dailyInventory = pgTable('daily_inventory', {
    id: serial('id').primaryKey(),
    item_id: integer('item_id'),
    user_id: integer('user_id'),
    date: integer('date'),
    amount: integer('amount'),
    price_low_eur: integer('price_low_eur'),
    price_median_eur: integer('price_median_eur'),
    total_worth_eur: integer('total_worth_eur')
});
