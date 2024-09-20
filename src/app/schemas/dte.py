from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


# Base schema for DTE
class DTEBase(BaseModel):
    cod_generacion: Annotated[str, Field(max_length=255)]
    sello_recibido: Annotated[str | None, Field(max_length=255)] = None
    estado: Annotated[str, Field(max_length=255)]
    documento: str
    fh_procesamiento: datetime
    observaciones: str | None = None
    tipo_dte: Annotated[str, Field(max_length=255)]
    enlace_pdf: Annotated[str | None, Field(max_length=255)] = None
    enlace_json: Annotated[str | None, Field(max_length=255)] = None
    enlace_ticket: Annotated[str | None, Field(max_length=255)] = None

# Schema for reading DTE data
class DTERead(DTEBase):
    id: int

# Schema for creating new DTE records
class DTECreate(DTEBase):
    model_config = ConfigDict(extra="forbid")

# Schema for updating existing DTE records
class DTEUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cod_generacion: Annotated[str, Field(max_length=255)]
    sello_recibido: Annotated[str | None, Field(max_length=255)] = None
    estado: Annotated[str, Field(max_length=255)]
    documento: str
    fh_procesamiento: datetime
    observaciones: str | None = None
    tipo_dte: Annotated[str, Field(max_length=255)]
    enlace_pdf: Annotated[str | None, Field(max_length=255)] = None
    enlace_json: Annotated[str | None, Field(max_length=255)] = None
    enlace_ticket: Annotated[str | None, Field(max_length=255)] = None

# Schema for internal updates (e.g., setting updated_at or deleted_at)
class DTEUpdateInternal(DTEUpdate):
    updated_at: datetime


class DTEDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_deleted: bool
    deleted_at: datetime


class DTERestoreDelete(BaseModel):
    is_deleted: bool
