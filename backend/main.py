"""
SpaceToday API – DECTIFY Full Stack Assessment
"""
import traceback

try:
    import os
    import logging
    from contextlib import asynccontextmanager
    from pathlib import Path
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    from app.api.limiter import limiter
    from app.database.session import engine, Base
    from app.api import auth, nasa, favorites, health

    # ---------------------------------------------------------------------------
    # Logging
    # ---------------------------------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    logger = logging.getLogger("spacetoday")


    # ---------------------------------------------------------------------------
    # Lifespan
    # ---------------------------------------------------------------------------
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        """Create tables on startup, dispose engine on shutdown."""
        logger.info("Starting SpaceToday API …")
        if "sqlite" in str(engine.url):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables ready.")
        
        # Initialize Redis if configured
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            from app.services.cache_service import set_cache, RedisCacheProvider
            set_cache(RedisCacheProvider(redis_url))
            logger.info("Configured app to use Redis cache.")
        yield
        await engine.dispose()
        logger.info("Shutdown complete.")


    # ---------------------------------------------------------------------------
    # Application
    # ---------------------------------------------------------------------------
    app = FastAPI(
        title="SpaceToday API",
        description="NASA data aggregation API with authentication and caching – DECTIFY Assessment",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"error": {"code": "rate_limit_exceeded", "message": "Rate limit exceeded"}}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": str(exc.status_code), "message": exc.detail}}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "validation_error", "message": "Invalid request parameters."}}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}}
        )

    # CORS – allow the React dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173", 
            "http://localhost:3000",
            os.getenv("FRONTEND_URL", "http://localhost:5173")
        ],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(nasa.router, prefix="/api/space", tags=["NASA"])
    app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
    app.include_router(health.router, prefix="/api", tags=["Health"])

except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()
    error_trace = traceback.format_exc()
    print("FATAL INIT ERROR:", error_trace)
    
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
    async def catch_all(path_name: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Initialization Failed",
                "message": str(e),
                "traceback": error_trace
            }
        )
