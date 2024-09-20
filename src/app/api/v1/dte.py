from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_dte import crud_dte
from ...schemas.dte import DTERead

router = APIRouter(tags=["dte"])


@router.get(
    "/dtes",
    response_model=PaginatedListResponse[DTERead],
    dependencies=[Depends(get_current_user)])
async def read_dtes(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    dte_data = await crud_dte.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=DTERead
    )

    response: dict[str, Any] = paginated_response(crud_data=dte_data, page=page, items_per_page=items_per_page)
    return response


@router.get(
    "/dtes/{codGeneracion}",
    response_model=DTERead,
    dependencies=[Depends(get_current_user)])
async def read_dte(request: Request, codGeneracion: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> DTERead:
    dte_data = await crud_dte.get(
        db=db,
        schema_to_select=DTERead,
        cod_generacion=codGeneracion
    )
    if dte_data is None:
        raise NotFoundException("DTE not found")
    return dte_data
