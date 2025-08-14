import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
  const res = await fetch(`/api/items/${params.name}`);
  const inventory = await res.json();

  return { inventory };
};