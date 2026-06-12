"""
Favorite model – stores user-saved NASA items with flexible JSON payload.
"""
import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)  # apod, mars, asteroid, eonet
    item_payload: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of the item data
    saved_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship
    user = relationship("User", back_populates="favorites")
