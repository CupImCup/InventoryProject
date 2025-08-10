import { pgTable, serial, text, integer, doublePrecision, date  } from 'drizzle-orm/pg-core';

export const items = pgTable('items', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  marketable: text('marketable').notNull()
});

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull()
});

export const daily_inventory = pgTable('daily_inventory', {
  id: serial('id').primaryKey(),
  item_id: integer('item_id').notNull(),      // <-- Use integer, not serial!
  user_id: integer('user_id').notNull(),      // <-- Same here
  date: date('date').notNull(),
  amount: integer('amount').notNull(),
  price_low_eur: doublePrecision('price_low_eur').notNull(),
  price_med_eur: doublePrecision('price_med_eur').notNull(),
  total_worth_eur: doublePrecision('total_worth_eur').notNull()
});
