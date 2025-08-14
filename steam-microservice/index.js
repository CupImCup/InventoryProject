require('dotenv').config();
const express = require('express');
const SteamUser = require('steam-user');
const GlobalOffensive = require('globaloffensive');

const app = express();
const port = process.env.PORT || 3000;

const client = new SteamUser();
const csgo = new GlobalOffensive(client);

let loggedIn = false;

client.logOn({
  accountName: process.env.STEAM_USER,
  password: process.env.STEAM_PASS
  //twoFactorCode: process.env.STEAM_2FA // optional, if you have 2FA
});


client.on('loggedOn', () => {
  loggedIn = true;
  console.log('Steam logged in');
  client.gamesPlayed([730]);
  console.log('Playing CS:GO');
  csgo.on('connectedToGC', () => {
    console.log('Connected to CS:GO Game Coordinator');
    csgo.inventory.forEach(item => {
      process.stdout.write(JSON.stringify(item) + '\n');
    });
  });

});


app.get('/inventory', async (req, res) => {
  if (!loggedIn) return res.status(503).send({ error: 'Not logged in yet' });

  try {
    const inventory = await new Promise((resolve, reject) => {
      csgo.requestInventoryContents(730, 2, true, (err, inv) => {
        console.log('Inventory requested');
        if (err) reject(err);
        else resolve(inv);
      });
    });
    res.json(inventory);
  } catch (error) {
    res.status(500).send({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Steam microservice listening on port ${port}`);
});
