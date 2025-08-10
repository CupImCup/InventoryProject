<script lang="ts">
  export let data;
  const dailyInventory = data.dailyInventory;

  import { onMount } from 'svelte';
  let chartDiv;
  let chart;

  onMount(async () => {
    if (!dailyInventory || dailyInventory.length === 0) return;

    // Dynamically import ApexCharts only on client
    const ApexCharts = (await import('apexcharts')).default;
const options = {
  chart: { 
    type: 'line', 
    height: 350,
    background: '#121212',     // Optional: dark background for chart area
    foreColor: '#fff'          // General text color (axis, legend, etc)
  },
  series: [{
    name: 'Price',
    data: dailyInventory.map(d => ({ x: d.date, y: d.price_low_eur, amount: d.amount }))
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
    custom: ({ series, seriesIndex, dataPointIndex, w }) => {
      const data = dailyInventory[dataPointIndex];
      return `<div style="
            background-color: #222;
            color: #eee;
            padding: 8px;
            border-radius: 6px;
            font-size: 0.9rem;
            box-shadow: 0 0 8px rgba(0,0,0,0.7);
          ">
        <strong>Date:</strong> ${data.date} <br/>
        <strong>Price:</strong> ${data.price_low_eur} €<br/>
        <strong>Amount:</strong> ${data.amount} <br/>
        <strong>Total worth:</strong> ${data.total_worth_eur} €
      </div>`;
    }
  }
};

    chart = new ApexCharts(chartDiv, options);
    chart.render();

    return () => {
      if (chart) chart.destroy();
    };
  });


</script>

<div class="dark-page">
  <a href="/" class="back-arrow" aria-label="Go back to main page">
    ← Back
  </a>

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