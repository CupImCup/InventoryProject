# InventoryProject

A fun, hobby project for tracking and analyzing Steam inventories.
I built this initially for personal use because I thought it was cool. Later, I refined it into a showcase of my skills in API development, database design, and frontend visualization.

## Features
- Tracks Steam inventories and logs item data over time  
- Fetches market values using proxy servers and multithreading (dramatically reduced runtime)  
- Stores all data in PostgreSQL  
- Delivers a frontend dashboard with item-level pricing, counts, and total worth over time  

## Tech Stack
- Python backend (Steam microservice)  
- PostgreSQL (schema in `SQL_Postgres`)  
- Svelte + TypeScript frontend  
- Docker (if applicable)

## Preview

**Frontend page view**  
![Frontend view](Frontend-Pageview.png)

**Single item details**  
![Item view](Frontend-Itemview-1.png)

## Next Steps
- Clean up and polish the frontend  
- Integrate fully with the existing Steam microservice  
- Add indexing for more efficient storage unit lookups
