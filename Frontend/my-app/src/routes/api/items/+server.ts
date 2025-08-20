import type { RequestHandler } from './$types';
import { pool } from '$lib/db';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  try {
    const sql1 = `
      SELECT di.*, users.name as user_name FROM new_daily_inventory di INNER JOIN users ON di.user_id = users.id
      WHERE di.inventory_date = CURRENT_DATE
      ORDER BY di.inventory_date DESC
    `;

    const sql2 = `
      SELECT 
        SUM(total_worth) AS total_worth,
        inventory_date
      FROM new_daily_inventory
      GROUP BY inventory_date
      ORDER BY inventory_date DESC
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
