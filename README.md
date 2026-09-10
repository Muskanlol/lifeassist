# LifeAssist

A hyperlocal daily assistant for India: nearby parks, food that is open now, and a leave-by commute time that accounts for peak-hour crowding.

## Why it exists

People repeat the same three decisions every weekday — where to run, what is open nearby, whether to leave for the station now. LifeAssist turns a locality into a morning brief. There is no free live crowding API for Indian transit, so peak windows are curated and can be refined with crowd reports.

## Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js (JavaScript) + Tailwind CSS + Leaflet |
| Backend | FastAPI + SQLite |
| Geodata | Nominatim, Overpass API, OSRM (all cached) |
| Peak hours | Hand-curated rules + optional user crowd reports |

## Architecture

```
Next.js  --/api/* rewrite-->  FastAPI
                                |-- Nominatim (geocode + autocomplete)
                                |-- Overpass (parks / food / stops)
                                |-- OSRM (walking distance, with haversine fallback)
                                '-- SQLite cache, users, favorites, crowd reports
```

## Features

- Auth with saved home and office localities
- Parks, open food, gyms, groceries, hangouts, local specialty, and places to visit
- Open-now filter from OSM `opening_hours`, evaluated in IST
- Home stop, office stop, and a leave-home time against peak windows
- Crowd reports (empty / ok / packed) on a line
- Saved places
- Map and list stay in sync
- Cache-first OSM access with a 1 req/sec limiter and a proper User-Agent

## Run locally

Terminal 1 — API:

```
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

Terminal 2 — UI:

```
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Register, set home/office, then try **Bandra**, **Borivali**, or **Mira Road**.

## Tests

```
cd backend
..\.venv\Scripts\python -m pytest -q
```
