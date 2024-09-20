from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


# Base schema for DatosEmpresa
class DatosEmpresaBase(BaseModel):
    nombre: Annotated[str, Field(max_length=255)]
    nit: Annotated[str, Field(max_length=255)]
    nrc: Annotated[str, Field(max_length=255)]
    codActividad: Annotated[str, Field(max_length=255)]
    descActividad: Annotated[str, Field()]
    nombreComercial: Annotated[str, Field(max_length=255)]
    tipoEstablecimiento: Annotated[str, Field(max_length=255)]
    departamento: Annotated[str, Field(max_length=255)]
    municipio: Annotated[str, Field(max_length=255)]
    complemento: Annotated[str, Field(max_length=255)]
    telefono: Annotated[str, Field(max_length=255)]
    correo: Annotated[str, Field(max_length=255)]
    codEstableMH: Annotated[Optional[str], Field(max_length=255, default=None)]
    codEstable: Annotated[str, Field(max_length=255)]
    codPuntoVentaMH: Annotated[Optional[str], Field(max_length=255, default=None)]
    codPuntoVenta: Annotated[str, Field(max_length=255)]

# Schema for reading DatosEmpresa data (for GET operations)
class DatosEmpresaRead(DatosEmpresaBase):
    id: int

# Schema for creating new DatosEmpresa records
class DatosEmpresaCreate(DatosEmpresaBase):
    model_config = ConfigDict(extra="forbid")

# Schema for updating existing DatosEmpresa records
class DatosEmpresaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: Annotated[str, Field(max_length=255)]
    nit: Annotated[str, Field(max_length=255)]
    nrc: Annotated[str, Field(max_length=255)]
    codActividad: Annotated[str, Field(max_length=255)]
    descActividad: Annotated[str, Field()]
    nombreComercial: Annotated[str, Field(max_length=255)]
    tipoEstablecimiento: Annotated[str, Field(max_length=255)]
    departamento: Annotated[str, Field(max_length=255)]
    municipio: Annotated[str, Field(max_length=255)]
    complemento: Annotated[str, Field(max_length=255)]
    telefono: Annotated[str, Field(max_length=255)]
    correo: Annotated[str, Field(max_length=255)]
    codEstableMH: Annotated[Optional[str], Field(max_length=255, default=None)]
    codEstable: Annotated[str, Field(max_length=255)]
    codPuntoVentaMH: Annotated[Optional[str], Field(max_length=255, default=None)]
    codPuntoVenta: Annotated[str, Field(max_length=255)]

# Schema for internal updates (e.g., setting updated_at or deleted_at)
class DatosEmpresaUpdateInternal(DatosEmpresaUpdate):
    updated_at: datetime

# Schema for soft deleting a DatosEmpresa record
class DatosEmpresaDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_deleted: bool
    deleted_at: datetime

# Schema for restoring a soft-deleted DatosEmpresa record
class DatosEmpresaRestoreDeleted(BaseModel):
    is_deleted: bool
