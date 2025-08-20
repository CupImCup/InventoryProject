<script lang="ts">
  import { onMount } from 'svelte';
  export let data;
  const inventory = data.inventory;

  let chartDiv;
  let chart;

  onMount(() => {
    (async () => {
    if (!inventory || inventory.length === 0) return;

    // Dynamically import ApexCharts only on clientloading
    const ApexCharts = (await import('apexcharts')).default;

    inventory.map(d => {
      if (!(d.price_low > 0)) {
        if (!(d.price_med > 0)) {
          // Neither low nor medium prices are available
          if (!(d.total_worth > 0)) {
            // No prices are available
            console.log('No prices available for item:', d);
          }
          else {
            // Only total worth is available
            d.price_low = d.total_worth / d.amount;
          }
        } else {
          // Only low price is available
          d.price_low = d.price_med;
        }
      } 
    });
    const options = {
      chart: { 
        type: 'line', 
        height: 350,
        background: '#121212',     // Optional: dark background for chart area
        foreColor: '#fff'          // General text color (axis, legend, etc)
      },
      series: [{
        name: 'Price',
        data: inventory.map(d => ({ x: d.inventory_date, y: d.price_low, amount: d.amount}))
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
          const data = inventory[dataPointIndex];
          return `<div style="
                background-color: #222;
                color: #eee;
                padding: 8px;
                border-radius: 6px;
                font-size: 0.9rem;
                box-shadow: 0 0 8px rgba(0,0,0,0.7);
              ">
            <strong>Date:</strong> ${new Date(data.inventory_date).toLocaleDateString('en-US', {
              weekday: "short",
              year: 'numeric',
              month: '2-digit',
              day: '2-digit'
            })} <br/>
            <strong>Price:</strong> ${data.price_low} €<br/>
            <strong>Amount:</strong> ${data.amount} <br/>
            <strong>Total worth:</strong> ${data.total_worth} €
          </div>`;
        }
      }
    };

        chart = new ApexCharts(chartDiv, options);
        chart.render();

        return () => {
          if (chart) chart.destroy();
        };
  })();
});

</script>

<div class="dark-page">
  <a href="/" class="back-arrow" aria-label="Go back to main page">
    ← Back
  </a>
  <h1>{inventory[0]?.item_name || 'Loading...'}</h1>

  <div bind:this={chartDiv}></div>
</div>

<style>
  .chart-container {
    max-width: 800px;
    margin: 0 auto;
  }

  .dark-page {
    background-color: #333333;
    color: #eee;
    min-height: 100vh;
    padding: 1rem;
  }

  .back-arrow {
    text-decoration: none;
    font-size: 1.2rem;
    color: #0070f3;
    cursor: pointer;
  }

  .back-arrow:hover {
    text-decoration: underline;
  }
</style>