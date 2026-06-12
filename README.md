# DECTIFY Assessment: SpaceToday

A comprehensive full-stack application for aggregating and exploring NASA API data, built for the DECTIFY engineering assessment.

## Project Overview

SpaceToday is a modern web application that provides users with a daily space intelligence briefing. It aggregates data from multiple NASA APIs, allowing authenticated users to explore Astronomy Pictures of the Day, Mars Rover photos, Near-Earth Asteroids, and Earth Observatory Natural Event Tracker (EONET) events. Users can also save items to their personal favorites.

### Architecture
```text
+-------------------+        +--------------------+        +--------------------+
|                   |        |                    |        |                    |
|   React/Vite UI   | <----> |  FastAPI Backend   | <----> |   SQLite / Redis   |
|   (TypeScript)    |        |   (Python 3.12)    |        | (Data & Caching)   |
|                   |        |                    |        |                    |
+-------------------+        +--------------------+        +--------------------+
                                      |
                                      v
                             +--------------------+
                             |     NASA APIs      |
                             | (APOD, Mars, etc)  |
                             +--------------------+
```

## Setup Instructions

### Environment Variables
Before running the application, set up the backend environment variables.
Copy the example file to create your `.env`:
```bash
cp backend/.env.example backend/.env
```
Ensure `NASA_API_KEY` is set (or use the default `DEMO_KEY`).

### Option 1: Docker Compose (Recommended)
The easiest way to run the application is using Docker Compose, which will spin up the Frontend, Backend, and Redis cache automatically.
```bash
docker compose up --build
```
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Option 2: Local Development
**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints Overview
The backend provides the following core endpoints (see `/docs` for full OpenAPI spec):

- **Auth:** `POST /api/auth/signup`, `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET /api/auth/me`
- **Space Feeds:** `GET /api/space/apod`, `GET /api/space/asteroids`, `GET /api/space/mars-photos`, `GET /api/space/earth-events`
- **Dashboard Aggregation:** `GET /api/space/dashboard`
- **Favorites:** `POST /api/favorites/`, `GET /api/favorites/`, `DELETE /api/favorites/{id}`
- **System:** `GET /api/health`

## Testing & Coverage

The backend test suite uses `pytest` and `pytest-asyncio` to comprehensively test the auth logic, dashboard partial-failure, cache abstraction, and API boundaries. 

To run tests and view coverage:
```bash
cd backend
pytest app/tests/ -v
pytest app/tests/ --cov=app --cov-report=term-missing
```
*Current Backend Coverage is 82%, featuring 46 passing tests.*

## Technical Highlights

### 1. Authentication Strategy
Uses a dual-token approach. Short-lived JWT Access Tokens are stored in memory/React state, while long-lived Refresh Tokens are set as `HttpOnly`, `Secure` cookies. This mitigates XSS attacks while allowing seamless background token rotation.

### 2. Cache Strategy
A Strategy Pattern was used to create an abstract `CacheProvider`. By default, it uses a zero-dependency `MemoryCacheProvider`. When `REDIS_URL` is detected in the environment (such as when running via Docker), it seamlessly swaps to a `RedisCacheProvider` to support distributed caching.

### 3. Partial-Failure Handling
The `/api/space/dashboard` endpoint aggregates four distinct NASA APIs using `asyncio.gather(..., return_exceptions=True)`. If an upstream API (e.g., APOD) returns a 503 error, the backend gracefully catches it and passes an error state to the frontend, ensuring the other feeds still render perfectly without crashing the dashboard.

## Design Report
Please see [DESIGN_REPORT.md](./DESIGN_REPORT.md) for an in-depth, 500-word explanation of technical decisions, database architecture, and future improvements.
