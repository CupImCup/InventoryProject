import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
  const { name } = params;
  // call your backend API to get the joined data
  const res = await fetch(`/api/items/${encodeURIComponent(name)}`);
  if (!res.ok) {
    return {
      status: res.status,
      error: new Error('Failed to load item data')
    };
  }
  const dailyInventory = await res.json();

  return { dailyInventory };
};