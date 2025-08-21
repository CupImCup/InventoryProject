<script lang="ts">
  import { Button, search } from "flowbite-svelte";
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  export let data;
  
  let inventory = data.inventory;


  let justTodaysInventory = inventory.filter(item => item.inventory_date === item.current_date);
  
  //inventory []
  const COMPLETE_INVENTORY = [...inventory];
  const DAILY_INVENTORY = [...justTodaysInventory];
  const DATABASE_TODAY = inventory[0]?.current_date;
  console.log("data_fetched:")
  console.log(COMPLETE_INVENTORY);
  let chartDiv;
  let chart;
  let valueOfInventory: number = 0;

  let userInput =  writable("");
  onMount(async () => {
    if (!inventory || inventory.length === 0) return;
    inventory.sort((a, b) => b.price_low - a.price_low);
    await createGraph();
  });

  async function createGraph(){
    if (!COMPLETE_INVENTORY || COMPLETE_INVENTORY.length === 0) return;
    valueOfInventory = 0;
    let selectedTotal = {};
    const userInputValue = $userInput.trim().toLowerCase();

    let displayInventory = COMPLETE_INVENTORY.filter(item =>
      matches(item.item_name, userInputValue)
    );
    
    displayInventory.forEach(item => {
      if(selectedTotal[item.inventory_date] === undefined) {
        selectedTotal[item.inventory_date] = 0;
      }
      if (!isNaN(Number(item.total_worth))) {
        selectedTotal[item.inventory_date] = Number(selectedTotal[item.inventory_date]) + Number(Number(item.total_worth).toFixed(2));
      }
    });
    
    valueOfInventory = selectedTotal[DATABASE_TODAY].toFixed(2) || 0;
    console.log("Today", DATABASE_TODAY, "value", valueOfInventory, "selectedTotal", selectedTotal);
    document.getElementById('total_worth').innerText = "Total Worth (€)" + valueOfInventory;
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
        data: displayInventory.map(d => ({ x: d.inventory_date, y: Number(selectedTotal[d.inventory_date]).toFixed(2), amount: d.amount}))
      }],
      markers: {
        size: 2,        // dot size
        colors: ['#9D7CF2'], // marker fill color
        strokeColors: '#9D7CF2', // border color
        strokeWidth: 4, // border padding
        hover: { size: 8 }
      },
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
        custom: ({seriesIndex}) => {
          var key = Object.keys(selectedTotal)[seriesIndex];
          var value = selectedTotal[key];
          console.log("Tooltip data:", key, value);
          console.log("Data point index:", seriesIndex);
          return `<div style="
                background-color: #222;
                color: #eee;
                padding: 8px;
                border-radius: 6px;
                font-size: 0.9rem;
                box-shadow: 0 0 8px rgba(0,0,0,0.7);
              ">
            <strong>Date:</strong> ${new Date(key).toLocaleDateString('de-DE', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit'
            })} <br/>
            <strong>Total worth:</strong> ${Number(value).toFixed(2)} €
          </div>`;
        }
      }
    };
    //reset Headers
    sortTable();
    if (chart) chart.destroy();
      chart = new ApexCharts(chartDiv, options);
      chart.render();

      return () => {
        if (chart) chart.destroy();
      };
  };

function matches(input, query) {
  return input.toLowerCase().includes(query.toLowerCase());
}

function handleOnSubmit(){
  if (!userInput) return;
  const userInputValue = $userInput.trim().toLowerCase();
  if (userInputValue === '') {
    justTodaysInventory = DAILY_INVENTORY;
  } else {
    justTodaysInventory = DAILY_INVENTORY.filter(item =>
      matches(item.item_name, userInputValue)
    );
  }
};

let sortAsc = true;
function sortTable(column: string) {  
  if (!justTodaysInventory || justTodaysInventory.length === 0) return;
    justTodaysInventory = [...justTodaysInventory].sort((a, b) => {
      let valA: any, valB: any;
      const key = column;
      if (['amount', 'price_low', 'price_med', 'total_worth'].includes(key)) {
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
      //just in case
      if( key === 'price_med' ) {
        if(valA == 0) {
          valA = Number(a['price_low']);
        }
        if(valB == 0) {
          valB = Number(b['price_low']);
        }
      }
      if (key === 'price_low') {
        if (valA == 0) {
          valA = Number(a['price_med']);
        }
        if (valB == 0) {
          valB = Number(b['price_med']);
        }
      }
      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;

      // tie-breaker: if sorting by category, use price_low
      if (key === 'item_category') {
        const pA = Number(a.price_low);
        const pB = Number(b.price_low);
        if (pA < pB) return 1; // always ascending
        if (pA > pB) return -1;
      }

      return 0;
    });

  if (column !== 'inventory_date') {
  sortAsc = !sortAsc;
    // reset ALL headers to no arrow
    const headers = document.querySelectorAll("th");
    headers.forEach(h => {
      h.innerHTML = h.innerHTML.replace(/▴|▾/g, "");
    });
 
    // add arrow only to the active header
    const header = document.getElementById(column);
    if (header) {
      header.innerHTML = header.innerHTML.replace(/▴|▾/g, "") + (sortAsc ? " ▴" : " ▾");
    }
   }
}


function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleOnSubmit();
    }
  }

function searchButton(){
  createGraph();
}
</script>
<main>
  <div bind:this={chartDiv}></div>
  <form action="#" class="left">
    <div class="my-input-group">
      <input  type="text" bind:value={$userInput} placeholder="Search Item Name..." onkeyup={handleOnSubmit}/>
      <button onclick={searchButton}>
        Render Graph with selection
      </button>
    </div>
  </form>
  <table id="inventory-table">
    <thead>
      <tr>
        <th id="inventory_date" onclick={() => sortTable('inventory_date')}>Date</th>
        <th id="item_name" onclick={() => sortTable('item_name')}>Item &#x25b4;&#x25be;</th>
        <th id="item_category" onclick={() => sortTable('item_category')}>Category &#x25b4;&#x25be;</th>
        <th id="amount" onclick={() => sortTable('amount')}>Amount &#x25b4;&#x25be;</th>
        <th id="price_low" onclick={() => sortTable('price_low')}>Price Low (€) &#x25b4;&#x25be;</th>
        <th id="total_worth" onclick={() => sortTable('total_worth')}>Total Worth (€) {valueOfInventory} &#x25b4;&#x25be;</th>
        <th id="user_name" onclick={() => sortTable('user_name')}>User &#x25b4;&#x25be;</th>
        <th id="price_med" onclick={() => sortTable('price_med')}>Price Med (€) &#x25b4;&#x25be;</th>
      <!--<td>{entry.marketable}</td>-->
      </tr>
    </thead>
    <tbody>
      {#each justTodaysInventory as entry}
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



.my-input-group {
  position: relative;
  width: 100%;
}

.my-input-group input {
  width: 100%;
  padding: 12px 110px 12px 12px; /* extra right padding so text doesn’t overlap button */
  border: 1px solid #555;
  border-radius: 5px;
  background: #222;
  color: white;
  font-size: 14px;
  outline: none;
}

.my-input-group button {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  background: #444;
  color: white;
  border-left: 1px solid #555;
  border-radius: 5px;
  padding: 8px 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.my-input-group button:hover {
  background: #666;
}

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