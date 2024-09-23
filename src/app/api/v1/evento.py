from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...crud.crud_evento import crud_evento
from ...schemas.evento import EventoRead

router = APIRouter(tags=["Consulta de eventos de Contingencia/Invalidación"])


@router.get(
    "/eventos",
    response_model=PaginatedListResponse[EventoRead],
    dependencies=[Depends(get_current_user)])
async def read_eventos(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
    start_date: datetime = None,
    end_date: datetime = None
) -> dict:
    if start_date and not end_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            created_at__gte=start_date,
            schema_to_select=EventoRead
        )
    elif end_date and not start_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            created_at__lte=end_date,
            schema_to_select=EventoRead
        )
    elif start_date and end_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            created_at__gte=start_date,
            created_at__lte=end_date,
            schema_to_select=EventoRead
        )
    else:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            schema_to_select=EventoRead
        )

    response: dict[str, Any] = paginated_response(crud_data=evento_data, page=page, items_per_page=items_per_page)
    return response


@router.get(
    "/eventos/contingencia",
    response_model=PaginatedListResponse[EventoRead],
    dependencies=[Depends(get_current_user)])
async def read_eventos_contingencia(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
    start_date: datetime = None,
    end_date: datetime = None
) -> dict:
    if start_date and not end_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="CONTINGENCIA",
            created_at__gte=start_date,
            schema_to_select=EventoRead
        )
    elif end_date and not start_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="CONTINGENCIA",
            created_at__lte=end_date,
            schema_to_select=EventoRead
        )
    elif start_date and end_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="CONTINGENCIA",
            created_at__gte=start_date,
            created_at__lte=end_date,
            schema_to_select=EventoRead
        )
    else:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            tipo_evento="CONTINGENCIA",
            limit=items_per_page,
            schema_to_select=EventoRead
        )

    response: dict[str, Any] = paginated_response(crud_data=evento_data, page=page, items_per_page=items_per_page)
    return response


@router.get(
    "/eventos/invalidacion",
    response_model=PaginatedListResponse[EventoRead],
    dependencies=[Depends(get_current_user)])
async def read_eventos_invalidacion(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
    start_date: datetime = None,
    end_date: datetime = None
) -> dict:
    if start_date and not end_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="INVALIDACION",
            created_at__gte=start_date,
            schema_to_select=EventoRead
        )
    elif end_date and not start_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="INVALIDACION",
            created_at__lte=end_date,
            schema_to_select=EventoRead
        )
    elif start_date and end_date:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="INVALIDACION",
            created_at__gte=start_date,
            created_at__lte=end_date,
            schema_to_select=EventoRead
        )
    else:
        evento_data = await crud_evento.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            tipo_evento="INVALIDACION",
            schema_to_select=EventoRead
        )

    response: dict[str, Any] = paginated_response(crud_data=evento_data, page=page, items_per_page=items_per_page)
    return response
