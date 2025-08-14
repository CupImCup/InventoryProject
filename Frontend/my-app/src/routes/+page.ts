import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch('/api/items'); // path to your +server.ts
  const { inventory, dailyTotals } = await res.json();

  return { inventory, dailyTotals };
}