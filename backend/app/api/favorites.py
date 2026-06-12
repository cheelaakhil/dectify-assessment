"""
Favorites CRUD endpoints.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.favorites import FavoriteCreate, FavoriteResponse, FavoriteDeleteResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# GET / – list all favorites for the current user
# ---------------------------------------------------------------------------
@router.get("/", response_model=list[FavoriteResponse])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.saved_at.desc())
    )
    favorites = result.scalars().all()
    return [
        FavoriteResponse(
            id=f.id,
            item_type=f.item_type,
            item_payload=json.loads(f.item_payload),
            saved_at=f.saved_at,
        )
        for f in favorites
    ]


# ---------------------------------------------------------------------------
# POST / – save a new favorite
# ---------------------------------------------------------------------------
@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    body: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fav = Favorite(
        user_id=current_user.id,
        item_type=body.item_type,
        item_payload=json.dumps(body.item_payload),
    )
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return FavoriteResponse(
        id=fav.id,
        item_type=fav.item_type,
        item_payload=json.loads(fav.item_payload),
        saved_at=fav.saved_at,
    )


# ---------------------------------------------------------------------------
# DELETE /{id} – remove a favorite
# ---------------------------------------------------------------------------
@router.delete("/{favorite_id}", response_model=FavoriteDeleteResponse)
async def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.id == favorite_id,
            Favorite.user_id == current_user.id,
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.commit()
    return {"message": "Favorite removed"}
