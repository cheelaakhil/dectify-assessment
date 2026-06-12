"""
Authentication endpoints: signup, login, refresh, logout, me.
Refresh tokens are sent/received via HttpOnly cookies.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse, MessageResponse
from app.services import auth_service
from app.api.deps import get_current_user
from app.models.user import User
from app.api.limiter import limiter

router = APIRouter()

REFRESH_COOKIE = "refresh_token"
REFRESH_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=False,       # Set True in production with HTTPS
        samesite="lax",
        max_age=REFRESH_MAX_AGE,
        path="/api/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/auth")


# ---------------------------------------------------------------------------
# POST /signup
# ---------------------------------------------------------------------------
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    body: SignupRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    existing = await auth_service.get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = await auth_service.create_user(db, body.name, body.email, body.password)

    access_token = auth_service.create_access_token(user.id, user.email)
    refresh_token = auth_service.generate_refresh_token()
    await auth_service.store_refresh_token(db, user.id, refresh_token)

    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.get_user_by_email(db, body.email)
    if not user or not auth_service.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = auth_service.create_access_token(user.id, user.email)
    refresh_token = auth_service.generate_refresh_token()
    await auth_service.store_refresh_token(db, user.id, refresh_token)

    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------
@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("5/minute")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get(REFRESH_COOKIE)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_record = await auth_service.validate_refresh_token(db, raw_token)
    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Rotate: revoke old, issue new
    await auth_service.revoke_refresh_token(db, raw_token)

    # Load user
    from sqlalchemy import select
    from app.models.user import User as UserModel
    result = await db.execute(select(UserModel).where(UserModel.id == token_record.user_id))
    user = result.scalar_one()

    new_access = auth_service.create_access_token(user.id, user.email)
    new_refresh = auth_service.generate_refresh_token()
    await auth_service.store_refresh_token(db, user.id, new_refresh)

    _set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=new_access)


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------
@router.post("/logout", response_model=MessageResponse)
@limiter.limit("5/minute")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get(REFRESH_COOKIE)
    if raw_token:
        await auth_service.revoke_refresh_token(db, raw_token)
    _clear_refresh_cookie(response)
    return MessageResponse(message="Logged out successfully")


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user
