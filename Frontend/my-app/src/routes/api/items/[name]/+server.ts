import { pool } from '$lib/db'; // the raw pg pool

export async function GET({ params }: { params: { name: string } }) {
  const { name } = params;

  const sql = `
    SELECT *
    FROM daily_inventory di
    INNER JOIN items i ON di.item_id = i.id
    WHERE i.name = $1
  `;

  try {
    const result = await pool.query(sql, [name]);
    return new Response(JSON.stringify(result.rows), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return new Response(JSON.stringify({ error: message }), { status: 500 });
  }
}