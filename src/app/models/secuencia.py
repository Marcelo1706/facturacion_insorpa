from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Secuencia(Base):
    __tablename__ = "secuencias"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    tipo_dte: Mapped[str] = mapped_column(String(255), nullable=False)
    secuencia: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
