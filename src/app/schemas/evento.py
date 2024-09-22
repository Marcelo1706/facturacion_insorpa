from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


# Base schema for Evento
class EventoBase(BaseModel):
    tipo_evento: Annotated[str, Field(max_length=255)]
    evento: str
    respuesta_mh: str

# Schema for reading Evento data
class EventoRead(EventoBase):
    id: int

# Schema for creating new Evento records
class EventoCreate(EventoBase):
    model_config = ConfigDict(extra="forbid")

# Schema for updating existing Evento records
class EventoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo_evento: Annotated[str, Field(max_length=255)]
    evento: str
    respuesta_mh: str

# Schema for internal updates (e.g., setting updated_at or deleted_at)
class EventoUpdateInternal(EventoUpdate):
    updated_at: datetime

# Schema for deleting Evento records
class EventoDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_deleted: bool

# Schema for restoring deleted Evento records
class EventoRestoreDelete(BaseModel):
    is_deleted: bool
