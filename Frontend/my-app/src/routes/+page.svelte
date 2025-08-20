<script lang="ts">
  import { Button } from "flowbite-svelte";
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
    
  export let data;
  
  let inventory = data.inventory;
  let dailyTotals = data.dailyTotals;
  //inventory []

  let chartDiv;
  let chart;
  let valueOfInventory: number = 0;

  let userInput =  writable("");
  onMount(async () => {
    if (!inventory || inventory.length === 0) return;
    inventory.sort((a, b) => b.price_low - a.price_low);
    inventory.forEach(element => {
      if(!isNaN(Number(element.total_worth))){
        valueOfInventory += Number(Number(element.total_worth).toFixed(2));
      }
    });
    valueOfInventory = Number(valueOfInventory).toFixed(2);

    await createGraph();

  });

  async function createGraph(){
    if (!dailyTotals || dailyTotals.length === 0) return;

    const ApexCharts = (await import('apexcharts')).default;
    const options = {
      chart: { 
        type: 'line', 
        height: 350,
        background: '#121212',     // Optional: dark background for chart area
        foreColor: '#fff'          // General text color (axis, legend, etc)
      },
      series: [{
        name: 'Worth',
        data: dailyTotals.map(d => ({ x: d.inventory_date, y: Number(d.total_worth).toFixed(2) }))
      }],
      xaxis: { 
        type: 'datetime',
        labels: {
          style: {
            colors: '#fff'        // White x-axis labels
          }
        },
        axisBorder: { color: '#555' },  // subtle axis border color
        axisTicks: { color: '#555' }    // subtle axis ticks color
      },
      yaxis: {
        labels: {
          style: {
            colors: '#fff'        // White y-axis labels
          }
        },
        axisBorder: { color: '#555' },
        axisTicks: { color: '#555' }
      },
      tooltip: {
        custom: ({dataPointIndex}) => {
          const data = dailyTotals[dataPointIndex];
          return `<div style="
                background-color: #222;
                color: #eee;
                padding: 8px;
                border-radius: 6px;
                font-size: 0.9rem;
                box-shadow: 0 0 8px rgba(0,0,0,0.7);
              ">
            <strong>Date:</strong> ${new Date(data.inventory_date).toLocaleDateString('de-DE', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit'
            })} <br/>
            <strong>Total worth:</strong> ${Number(data.total_worth).toFixed(2)} €
          </div>`;
        }
      }
    };

        chart = new ApexCharts(chartDiv, options);
        chart.render();

        return () => {
          if (chart) chart.destroy();
        };
  };
  
function handleOnSubmit(){
    if (!userInput) return;

    // Here you would typically send the userInput to your backend
    console.log('User input:', userInput);
  };

  let sortAsc = true;
function sortTable(column: string) {
  if (!inventory || inventory.length === 0) return;

  inventory = [...inventory].sort((a, b) => {
    let valA: any, valB: any;
    const key = column;
    if (['amount', 'price_low', 'total_worth'].includes(key)) {
      valA = Number(a[key]);
      valB = Number(b[key]);
    } else if (key === 'inventory_date') {
      const [dA, mA, yA] = String(a[key]).split('.');
      const [dB, mB, yB] = String(b[key]).split('.');
      valA = new Date(+yA, +mA - 1, +dA).getTime();
      valB = new Date(+yB, +mB - 1, +dB).getTime();
    } else {
      valA = String(a[key] ?? '').toLowerCase().trim();
      valB = String(b[key] ?? '').toLowerCase().trim();
    }
    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;

    // tie-breaker: if sorting by category, use price_low
    if (key === 'item_category') {
      console.log('Sorting by category:', a[key], b[key]);  
      const pA = Number(a.price_low);
      const pB = Number(b.price_low);
      if (pA < pB) return 1; // always ascending
      if (pA > pB) return -1;
    }

    return 0;
  });

  sortAsc = !sortAsc;
}

</script>
<main>
  <div bind:this={chartDiv}></div>
  <table id="inventory-table">
    <thead>
      <tr>
        <th onclick={() => sortTable('inventory_date')}>Date</th>
        <th onclick={() => sortTable('item_name')}>Item</th>
        <th onclick={() => sortTable('item_category')}>Category</th>
        <th onclick={() => sortTable('amount')}>Amount</th>
        <th onclick={() => sortTable('price_low')}>Price Low (€)</th>
  <!--            <th>Price Med (€)</th> -->
        <th onclick={() => sortTable('total_worth')}>Total Worth (€) {valueOfInventory}</th>
        <th onclick={() => sortTable('user_name')}>User</th>
        <th onclick={() => sortTable('price_med')}>Price Med (€)</th>
      <!--<td>{entry.marketable}</td>-->
      </tr>
    </thead>
    <tbody>
      {#each inventory as entry}
        <tr>
          <td>{new Date(entry.inventory_date).toLocaleDateString('de-DE', {
                weekday: "short",
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
              })}</td>
          <td>
            <a href={`/items/${encodeURIComponent(entry.item_name)}`}>
              {entry.item_name}
            </a>
          </td>
          <td>{entry.item_category}</td>
          <td>{entry.amount}</td>
          <td>
            {#if entry.price_low > 0}
                {entry.price_low}
              {:else if entry.price_med > 0}
                {entry.price_med} (Median)
              {:else}
                <span>--</span>
              {/if}
          </td>
          <td>{Number(entry.total_worth).toFixed(2)}</td>
          <td>{entry.user_name}</td>
          <td>
            {#if entry.price_med > 0}
              {entry.price_med}
            {:else if entry.price_low > 0}
              {entry.price_low} (Low)
            {:else}
              <span>--</span>
            {/if}
          </td>
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

  .dark-page {
    background-color: #333333;
    color: #eee;
    padding: 1rem;
  }
</style>