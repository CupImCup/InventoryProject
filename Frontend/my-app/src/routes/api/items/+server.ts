import type { RequestHandler } from '@sveltejs/kit';
import { json } from '@sveltejs/kit';
import { pool } from '$lib/db';

export const GET: RequestHandler = async () => {
  try {
    const result = await pool.query('SELECT * FROM items');
    return json(result.rows);
  } catch (error) {
    console.error('DB query error:', error);
    return json({ error: 'Failed to fetch items' }, { status: 500 });
  }
};