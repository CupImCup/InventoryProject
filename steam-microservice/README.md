# Steam Inventory Microservice

A lightweight Dockerized microservice that handles **Steam login** and **inventory fetching**, built with Node.js.  
It makes use of the [`steam-user`](https://www.npmjs.com/package/steam-user) and [`globaloffensive`](https://www.npmjs.com/package/globaloffensive) modules.

## Features
- Steam authentication
- Fetches user inventories
- Exposes data via a simple microservice API
- Runs inside a Docker container for easy deployment

## Tech Stack
- Node.js
- steam-user
- globaloffensive
- Docker

## Getting Started

### Clone & Install
```bash
git clone <your-repo-url>
cd steam-inventory-microservice
npm install

Run Locally

npm start

Run with Docker

docker build -t steam-inventory-service .
docker run -p 3000:3000 steam-inventory-service
```
# TODO

    Add error handling for Steam login failures

    Expand inventory endpoints

    Add caching for frequent requests