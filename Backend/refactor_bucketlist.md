# Refactor Bucketlist for Steam Inventory Project

## 1. Database Schema Sanity Check
- [ ] Deprecate old `items` table gradually (keep read-only for debugging).
- [ ] Make **`jsonitem`** the canonical item definition (`id SERIAL, name UNIQUE, category`).
- [ ] Change `daily_inventory.item_id` → foreign key into `jsonitem.id`.
- [ ] Ensure uniqueness: `jsonitem.name` must be `UNIQUE` (`Steam won’t reuse names` is a safe assumption).
- [ ] Add `ON CONFLICT DO NOTHING` for inserting new `jsonitem` rows.

## 2. Enum Safety
- [ ] Fix `get_category`: it should return a `Category`, not a string.  
  ```python
  def get_category(category_str: str) -> Category:
      key = category_str.upper().replace(" ", "_")
      try:
          return Category[key]
      except KeyError:
          return Category.OTHERS
  ```
- [ ] Decide if `PATCHES` and `PATCH_PACKS` are truly distinct. If not, drop one.

## 3. Data Flow Refactor
- [ ] Inventory fetch (`fetch_inventory`) should:
  - Normalize raw Steam data → `Item` dataclass.  
  - Convert into `JSONItem` (lookup category + name).  
  - Insert missing entries into `jsonitem` table.  
  - Return a clean dict `{name → JSONItem}`.  
- [ ] Kill off usage of `classid` as a primary identifier. Use `name` instead everywhere downstream.  

## 4. Persistence Refactor
- [ ] `daily_inventory` inserts should reference `jsonitem.id` by looking up `name`.  
  ```sql
  INSERT INTO daily_inventory (item_id, user_id, date, amount, price_low_eur, price_median_eur, total_worth_eur)
  VALUES ((SELECT id FROM jsonitem WHERE name = %s), %s, %s, %s, %s, %s, %s)
  ```
- [ ] Remove “random generated IDs” hack (only fallback if Steam breaks contract, but keep code commented).

## 5. Separation of Concerns
- [ ] Split into modules:
  - `db.py` → connection, queries, inserts  
  - `steam.py` → inventory fetching, price fetching  
  - `models.py` → dataclasses + enums  
  - `main.py` → orchestration  
- [ ] Makes testing and mental load way smaller.

## 6. Threaded Fetch Safety
- [ ] Thread worker should **not** mutate shared list (`dictList.remove(item)` is a race hazard). Instead, filter before threading.  
- [ ] Collect results in thread-safe queue or return values, then bulk-insert.

## 7. Logging & Debug
- [ ] Replace all `print()` with `logging` (levels: DEBUG, INFO, WARNING).  
- [ ] Save failed items into DB or JSON file for retry instead of just `listOfFailedItems`.

## 8. Future-Proofing
- [ ] Create migration script that replays old `items` into `jsonitem`.  
- [ ] Add `last_seen` / `first_seen` fields if you ever care about historical item availability.  
- [ ] Build small test harness for `fetch_inventory` with mocked JSON so you don’t need Steam calls every run.

---

## 🎯 Suggested First Steps
1. Fix `get_category` so you’re always holding a **real `Category` enum**.  
2. Add `UNIQUE(name)` constraint to `jsonitem` and update `daily_inventory` to foreign key into it.  
3. Write one helper: `get_or_create_jsonitem(name, category)` that does the DB insert if missing.  
4. Rip out `classid` as soon as the above works.
