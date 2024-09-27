from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_secuencia import crud_secuencia
from ...schemas.secuencia import SecuenciaRead, SecuenciaUpdate

router = APIRouter(tags=["Consulta de Secuencias"])

@router.get(
    "/secuencias",
    response_model=PaginatedListResponse[SecuenciaRead],
    dependencies=[Depends(get_current_user)])
async def read_secuencias(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10
) -> dict:
    secuencia_data = await crud_secuencia.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=SecuenciaRead
    )
    return paginated_response(
        crud_data=secuencia_data,
        page=page,
        items_per_page=items_per_page
    )

@router.put(
    "/secuencias/{id}",
    dependencies=[Depends(get_current_user)])
async def update_secuencia(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    id: int,
    secuencia: SecuenciaUpdate
) -> Any:
    db_secuencia: SecuenciaRead | None = await crud_secuencia.get(
        db=db,
        schema_to_select=SecuenciaRead,
        id=id
    )
    if db_secuencia is None:
        raise NotFoundException("Secuencia not found")

    await crud_secuencia.update(
        db=db,
        object=secuencia,
        id=id
    )
    return {"message":"Secuencia updated successfully"}
