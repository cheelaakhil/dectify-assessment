# DECTIFY Assessment: Design Report

## 1. Authentication Strategy

The authentication system is built around a secure, two-token architecture using JSON Web Tokens (JWT) for access and cryptographically hashed refresh tokens stored in the database.

- **Access Tokens:** Short-lived JWTs (typically 15-30 minutes) are issued upon successful login. These contain the user ID (`sub`), email, and an expiration timestamp (`exp`). The frontend includes this token in the `Authorization` header of API requests.
- **Refresh Tokens:** Long-lived tokens (e.g., 7 days) are issued alongside the access token. However, to mitigate XSS attacks, refresh tokens are **never** returned in the JSON response body. Instead, they are set as `HttpOnly`, `Secure` cookies by the backend.
- **Token Rotation & Revocation:** When the frontend silently hits the `/auth/refresh` endpoint using the `HttpOnly` cookie, the backend issues a brand-new access token and a brand-new refresh token (rotating the old one). Refresh tokens are stored as bcrypt hashes in the database. If a user logs out, the hash is deleted from the database, instantly revoking their ability to refresh access, ensuring high security.

## 2. Cache Design

A robust cache layer was implemented using the Strategy Pattern to abstract the caching mechanism from the business logic.

- **`CacheProvider` Interface:** An abstract base class defines the contract for caching operations (`get`, `set`, `delete`, `clear`, `health_check`).
- **`MemoryCacheProvider`:** Used by default. It leverages a Python dictionary with a TTL (Time-To-Live) tracking mechanism to serve data quickly from memory without relying on external dependencies.
- **`RedisCacheProvider` (Bonus):** Implemented for production readiness. If a `REDIS_URL` is detected in the environment variables during startup, the application seamlessly swaps the `MemoryCacheProvider` for the `RedisCacheProvider`. This allows the application to scale across multiple instances while maintaining a centralized cache.

## 3. NASA API Integration & Partial Failure

The core functionality of the dashboard requires fetching data from four distinct NASA APIs: APOD, Mars Rovers, Near-Earth Asteroids, and EONET Earth Events.

To ensure performance, these requests are executed concurrently rather than sequentially.
- **`asyncio.gather`:** The `nasa_service.py` uses `asyncio.gather(*tasks, return_exceptions=True)` to execute all outgoing HTTP requests in parallel. This reduces the dashboard load time to the duration of the single slowest API call, rather than the sum of all four.
- **Partial Failure Handling:** Because `return_exceptions=True` is used, if one NASA API is down (e.g., APOD returns a 503), the other three futures still resolve successfully. The backend intercepts the exception, logs a warning, and returns a graceful `{"error": "Service unavailable"}` object for the failing feed while returning the actual payload for the successful feeds. The frontend detects this error state and renders a localized alert, ensuring the dashboard remains usable despite upstream instability.

## 4. Database Design

The database uses SQLAlchemy 2.0 with asynchronous drivers (`aiosqlite`) to prevent blocking the FastAPI event loop during I/O operations.

- **Users:** Stores user credentials with securely hashed passwords using `passlib` (bcrypt).
- **Tokens:** A one-to-many relationship with Users to store hashed refresh tokens. This allows a user to be logged in on multiple devices simultaneously, and to log out of individual sessions.
- **Favorites:** A one-to-many relationship mapping a user ID to a JSON payload representing a favorited space item (APOD, Mars Photo, etc.). Data access is strictly isolated; API queries filter by `user_id` so users cannot read or delete each other's data.

Migrations are managed via **Alembic**, ensuring the schema can evolve safely over time.

## 5. Future Improvements

Given more time, the following improvements would be prioritized:
1. **Frontend Testing:** While backend coverage is high (82%), adding E2E tests using Playwright and component tests using Vitest/React Testing Library would solidify frontend reliability.
2. **PostgreSQL Migration:** The architecture is currently running on SQLite. Migrating to PostgreSQL would improve concurrent write performance in a highly-scaled production environment.
3. **Storybook Integration:** Implementing Storybook for the React components would isolate component development and build a living design system document.
4. **Rate Limiting via Redis:** The `slowapi` rate limiter currently uses memory; linking it to the Redis backend would ensure rate limits are enforced across multiple load-balanced instances.
