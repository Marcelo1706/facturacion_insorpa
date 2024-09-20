from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class DatosEmpresa(Base):
    __tablename__ = 'datos_empresa'

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    nit: Mapped[str] = mapped_column(String(255), nullable=False)
    nrc: Mapped[str] = mapped_column(String(255), nullable=False)
    codActividad: Mapped[str] = mapped_column(String(255), nullable=False)
    descActividad: Mapped[str] = mapped_column(Text, nullable=False)
    nombreComercial: Mapped[str] = mapped_column(String(255), nullable=False)
    tipoEstablecimiento: Mapped[str] = mapped_column(String(255), nullable=False)
    departamento: Mapped[str] = mapped_column(String(255), nullable=False)
    municipio: Mapped[str] = mapped_column(String(255), nullable=False)
    complemento: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(255), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), nullable=False)
    codEstableMH: Mapped[str] = mapped_column(String(255), nullable=True)
    codEstable: Mapped[str] = mapped_column(String(255), nullable=False)
    codPuntoVentaMH: Mapped[str] = mapped_column(String(255), nullable=True)
    codPuntoVenta: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
