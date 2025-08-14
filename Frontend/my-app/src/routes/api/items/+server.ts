import type { RequestHandler } from './$types';
import { pool } from '$lib/db';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  try {
    const sql1 = `
      SELECT 
        daily_inventory.*,
        items.name AS item_name,
        items.marketable,
        users.name AS user_name
      FROM daily_inventory
      INNER JOIN items ON daily_inventory.item_id = items.id
      INNER JOIN users ON daily_inventory.user_id = users.id
      WHERE daily_inventory.date = CURRENT_DATE
      ORDER BY daily_inventory.date DESC
    `;

    const sql2 = `
      SELECT 
        SUM(total_worth_eur) AS total_worth,
        date
      FROM daily_inventory
      GROUP BY date
      ORDER BY date DESC
    `;

    // Run both queries in parallel
    const [result1, result2] = await Promise.all([
      pool.query(sql1),
      pool.query(sql2)
    ]);

    return json({
      inventory: result1.rows,
      dailyTotals: result2.rows
    });

  } catch (error) {
    console.error('DB query error:', error);
    return json({ error: 'Failed to fetch items' }, { status: 500 });
  }
};
