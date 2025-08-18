require('dotenv').config();
const express = require('express');
const SteamUser = require('steam-user');
const CS2 = require('globaloffensive');
const readline = require('readline');
const ItemNameConverter = require('./convert_Inventory');
const { writeFile } = require('fs');

const app = express();
const port = process.env.PORT || 3000;


const importInventory = "True" ? true : false;
const importStorageUnits = "True" ? true : false;
const importCases = "True" ? true : false;
const importStickerCapsules = "True" ? true : false;
const importStickers = "True" ? true : false;
const importOthers = "True" ? true : false;



let client = new SteamUser();
let cs2;
let nameConverter = new ItemNameConverter();
nameConverter.initialize();
let loggedIn = false;

client.logOn({
  accountName: process.env.STEAM_USER,
  password: process.env.STEAM_PASS
  //twoFactorCode: process.env.STEAM_2FA // optional, if you have 2FA
});

client.on('steamGuard', (domain, callback) => {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  // Email code
  if (domain) {
    rl.question(`Enter Steam Guard code sent to your email (${domain}): `, (code) => {
      callback(code.trim()); // continue login with the code
      rl.close();
    });
  } else {
    // Mobile Authenticator TOTP code
    rl.question("Enter Steam Guard mobile 2FA code: ", (code) => {
      callback(code.trim());
      rl.close();
    });
  }
});
client.on('error', (err) => {
  console.error('Error logging into Steam:', err);
});

client.on('loggedOn', () => {
  
  cs2 = new CS2(client);
  loggedIn = true;
  console.log('Steam logged in');
  client.gamesPlayed([730]);
  console.log('Playing CS:GO');
  cs2.on('connectedToGC', async () => {
    console.log('Connected to CS:GO Game Coordinator');
    cs2.inventory.forEach(item => {
      console.log('Name:');
      process.stdout.write(nameConverter.getItemName(item) + '\n');
      console.log('Type:');
      process.stdout.write(nameConverter.getItemType(item) + '\n');
      console.log('Wear:');
      process.stdout.write(nameConverter.getWearName(item) + '\n');
      console.log('Tradable:');
      process.stdout.write(nameConverter.getItemTradable(item) + '\n');
    });

    let finalItemCounts = {};

    if (importInventory) {
      const inventoryItemCounts = await processInventory();
      mergeItemCounts(finalItemCounts, inventoryItemCounts);
    }

    if (importStorageUnits) {
      const storageUnitItemCounts = await processStorageUnits();
      mergeItemCounts(finalItemCounts, storageUnitItemCounts);
    }

    const outputPath = path.join('/app/output', 'items.json');

  fs.writeFile(outputPath, JSON.stringify(finalItemCounts, null, 2), (err) => {
    if (err) {
      process.stderr.write("Error saving config: " + err + '\n');
    } else {
      console.log("File saved to:", outputPath);
    }
  });
    process.stdout.write("Saving config...");
    writeFile('items.json', JSON.stringify(finalItemCounts, null, 2), (err) => {
      if (err) {
        process.stderr.write("Error saving config: " + err + '\n');
      }
    });
    process.stdout.write(JSON.stringify(finalItemCounts, null, 2) + '\n');
    process.stdout.write("Processing complete.");
    process.stdout.write("This window will automatically close in 10 seconds.");
    await new Promise((resolve) => setTimeout(resolve, 10000));
    client.logOff();
    process.exit(0);
  });
});

app.get('/inventory', async (req, res) => {
  if (!loggedIn) return res.status(503).send({ error: 'Not logged in yet' });

  try {
    const inventory = await new Promise((resolve, reject) => {
      cs2.requestInventoryContents(730, 2, true, (err, inv) => {
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


  async function processInventory() {
    try {
      // filter out items that have the casket_id property set from the inventory
      // because these are items that should be contained in storage units
      const prefilteredInventory = cs2.inventory.filter((item) => {
        return !item.casket_id;
      });

      const convertedItems =
        nameConverter.convertInventory(prefilteredInventory);
      const filteredItems = filterItems(convertedItems);
      const itemCounts = groupAndCountItems(filteredItems);
      process.stdout.write(`${filteredItems.length} items found in inventory\n`);
      process.stdout.write(JSON.stringify(itemCounts, null, 2) + '\n');
      return itemCounts;
    } catch (err) {
      process.stderr.write("An error occurred while processing the inventory: " + err + '\n');
      return {};
    }
  }

  async function processStorageUnits() {
    let finalItemCounts = {};
    try {
      const storageUnitIds = getStorageUnitIds();
      for (const [unitIndex, unitId] of storageUnitIds.entries()) {
        const items = await getCasketContentsAsync(cs2, unitId);
        const convertedItems = nameConverter.convertInventory(items);
        const filteredItems = filterItems(convertedItems);
        const itemCounts = groupAndCountItems(filteredItems);
        mergeItemCounts(finalItemCounts, itemCounts);
        process.stdout.write(
          `${filteredItems.length} items found in storage unit: ${unitIndex + 1}/${storageUnitIds.length}\n`,
        );
        process.stdout.write(JSON.stringify(itemCounts, null, 2) + '\n');
      }
      return finalItemCounts;
    } catch (err) {
      process.stderr.write("An error occurred while processing storage units: " + err + '\n');
      return {};
    }
  }

  function getStorageUnitIds() {
    let storageUnitIds = [];
    for (let item of cs2.inventory) {
      if (item.casket_contained_item_count > 0) {
        storageUnitIds.push(item.id);
      }
    }
    return storageUnitIds;
  }

  function getCasketContentsAsync(cs2, unitId) {
    return new Promise((resolve, reject) => {
      cs2.getCasketContents(unitId, (err, items) => {
        if (err) return reject(err);
        resolve(items);
      });
    });
  }

  function filterItems(items) {
    const otherItemTypes = [
      "Skins",
      "Special Items",
      "Agents",
      "Charms",
      "Patches",
      "Patch Packs",
      "Souvenirs",
      "Others",
      "Sticker Capsules",
      "Collectible Pins",
      "Collectible Capsules",
      "Music Kits",
      "Case Keys",
      "Passes",
      "Music Kit Boxes",
      "Autograph Capsules",
    ];
    let filteredItems = [];

    items.forEach((item) => {
      if (!item.item_tradable) {
        return;
      }
      if (
        (item.item_type === "Cases" && importCases) ||
        (item.item_type === "Major Sticker Capsules" &&
          importStickerCapsules) ||
        (item.item_type === "Stickers" && importStickers) ||
        (otherItemTypes.includes(item.item_type) && importOthers)
      ) {
        filteredItems.push(item);
      }
    });
    return filteredItems;
  }

  function groupAndCountItems(items) {
    let groupedItems = items.reduce((acc, item) => {
      const { item_name, item_type } = item;

      if (!acc[item_type]) {
        acc[item_type] = {};
      }

      if (!acc[item_type][item_name]) {
        acc[item_type][item_name] = 0;
      }

      acc[item_type][item_name]++;
      return acc;
    }, {});

    return groupedItems;
  }

  function mergeItemCounts(finalItemCounts, currentItemCounts) {
    for (const item_type in currentItemCounts) {
      if (!finalItemCounts[item_type]) {
        finalItemCounts[item_type] = {};
      }

      for (const item_name in currentItemCounts[item_type]) {
        if (!finalItemCounts[item_type][item_name]) {
          finalItemCounts[item_type][item_name] = 0;
        }

        finalItemCounts[item_type][item_name] +=
          currentItemCounts[item_type][item_name];
      }
    }
  }