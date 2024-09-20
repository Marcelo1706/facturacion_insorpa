from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class DTE(Base):
    __tablename__ = 'dte_generados'

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    cod_generacion: Mapped[str] = mapped_column(String(255), nullable=False)
    sello_recibido: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(String(255), nullable=False)
    documento: Mapped[str] = mapped_column(Text, nullable=False)
    fh_procesamiento: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_dte: Mapped[str] = mapped_column(String(255), nullable=False)
    enlace_pdf: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enlace_json: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enlace_ticket: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
