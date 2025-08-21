import type { RequestHandler } from './$types';
import { pool } from '$lib/db';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async () => {
  try {
    const sql1 = `
      SELECT di.*, users.name as user_name, CURRENT_DATE as current_date FROM new_daily_inventory di INNER JOIN users ON di.user_id = users.id
      ORDER BY di.inventory_date DESC
    `;


    // Run both queries in parallel
    const [result1] = await Promise.all([
      pool.query(sql1)
    ]);
    return json({
      inventory: result1.rows
    });

  } catch (error) {
    console.error('DB query error:', error);
    return json({ error: 'Failed to fetch items' }, { status: 500 });
  }
};
