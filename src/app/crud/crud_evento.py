from fastcrud import FastCRUD

from ..models.evento import Evento
from ..schemas.evento import EventoCreate, EventoDelete, EventoUpdate, EventoUpdateInternal

CRUDEvento = FastCRUD[
    Evento,
    EventoCreate,
    EventoUpdate,
    EventoUpdateInternal,
    EventoDelete
]
crud_evento = CRUDEvento(Evento)
