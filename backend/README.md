# SpaceToday Backend

Backend service for the DECTIFY Full Stack Engineering Assessment.

## Architecture Overview
The backend is built with FastAPI and SQLite. It serves as an aggregation layer for various NASA APIs, with built-in caching to optimize requests and avoid rate limits. It also provides authentication (JWT) and a favorites system.

## Setup Instructions
1. Ensure you have Python 3.12+ installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the `backend/app` directory or `backend` root (the application resolves `.env` from `backend/app/.env` natively, but `load_dotenv` handles overrides).

```env
DATABASE_URL=sqlite+aiosqlite:///spacetoday.db
JWT_SECRET=your_super_secret_key_here
NASA_API_KEY=DEMO_KEY  # Or your actual NASA API key
```

## Run Commands
To start the development server:
```bash
uvicorn main:app --reload --port 8000
```
The API will be available at http://localhost:8000.
Swagger UI documentation is available at http://localhost:8000/docs.

To run the tests:
```bash
pytest --cov=app app/tests
```

## Example Requests

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'
```

### Get Dashboard
```bash
curl -X GET http://localhost:8000/api/space/dashboard \
  -H "Authorization: Bearer <your_access_token>"
```

## Design Report
- **Rate Limiting**: `slowapi` is configured globally (100 req/min) and specifically on auth routes (5 req/min) to protect against brute-force attacks and abuse.
- **Caching**: NASA API responses are cached to reduce latency and avoid hitting NASA API rate limits.
- **Error Handling**: A unified error handling structure is implemented across the API (`{"error": {"code": "...", "message": "..."}}`) to simplify frontend integration.
- **Testing**: Pytest is used with `pytest-asyncio`. External NASA services are fully mocked to ensure fast, deterministic tests without making real network requests.
