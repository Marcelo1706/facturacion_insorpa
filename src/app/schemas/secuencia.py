from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


# Base schema for Secuencia
class SecuenciaBase(BaseModel):
    tipo_dte: Annotated[str, Field(max_length=255)]
    secuencia: int

# Schema for reading Secuencia data
class SecuenciaRead(SecuenciaBase):
    id: int

# Schema for creating new Secuencia records
class SecuenciaCreate(SecuenciaBase):
    model_config = ConfigDict(extra="forbid")

# Schema for updating existing Secuencia records
class SecuenciaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo_dte: Annotated[str, Field(max_length=255)]
    secuencia: int

# Schema for internal updates (e.g., setting updated_at or deleted_at)
class SecuenciaUpdateInternal(SecuenciaUpdate):
    updated_at: datetime

# Schema for deleting Secuencia records
class SecuenciaDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_deleted: bool
    deleted_at: datetime

# Schema for restoring deleted Secuencia records
class SecuenciaRestoreDelete(BaseModel):
    is_deleted: bool
