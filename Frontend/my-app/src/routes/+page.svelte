<script lang="ts">
  import Header from '$lib/Header.svelte';
  import { onMount } from 'svelte';

  let items: { id: number; name: string; marketable: int }[] = [];

  onMount(async () => {
    const res = await fetch('/api/items');
    items = await res.json();

      // Sort items: marketable ones first
  items.sort((a, b) => b.marketable - a.marketable);
  });
</script>

<Header title="My PostgreSQL App" />

<main>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Marketable</th>
      </tr>
    </thead>
    <tbody>
      {#each items as item}
        <tr>
          <td>{item.id}</td>
          <td><a href={`/items/${encodeURIComponent(item.name)}`}>{item.name}</a></td>
          <td>{item.marketable}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</main>

<style>
  main {
    background: #333;
    color: white;
    padding: 1rem;
    min-height: 100vh;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    padding: 0.5rem;
    border: 1px solid #555;
  }
</style>