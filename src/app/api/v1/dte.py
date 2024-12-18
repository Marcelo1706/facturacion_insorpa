from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_dte import crud_dte
from ...schemas.dte import DTERead

router = APIRouter(tags=["Consulta de DTEs"])


@router.get(
    "/dtes",
    response_model=PaginatedListResponse[DTERead],
    dependencies=[Depends(get_current_user)])
async def read_dtes(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
    start_date: datetime = None,
    end_date: datetime = None
) -> dict:
    if start_date and not end_date:
        start_date += timedelta(hours=6)
        dte_data = await crud_dte.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            fh_procesamiento__gte=start_date,
            schema_to_select=DTERead
        )
    elif end_date and not start_date:
        end_date += timedelta(hours=6)
        dte_data = await crud_dte.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            fh_procesamiento__lte=end_date,
            schema_to_select=DTERead
        )
    elif start_date and end_date:
        start_date += timedelta(hours=6)
        end_date += timedelta(hours=6)
        dte_data = await crud_dte.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            fh_procesamiento__gte=start_date,
            fh_procesamiento__lte=end_date,
            schema_to_select=DTERead
        )
    else:
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


@router.get(
    "/dtes_numero_control/{numeroControl}",
    response_model=DTERead,
    dependencies=[Depends(get_current_user)])
async def read_dte_by_numero_control(
    request: Request,
    numeroControl: str,
    db: Annotated[AsyncSession, Depends(async_get_db)]) -> DTERead:
    dte_data = await crud_dte.get(
        db=db,
        schema_to_select=DTERead,
        numero_control=numeroControl
    )
    if dte_data is None:
        raise NotFoundException("DTE not found")
    return dte_data


@router.get(
    "/dtes_statistics",
    response_model=dict,
    dependencies=[Depends(get_current_user)])
async def get_dtes_statistics(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    start_date: datetime = None,
    end_date: datetime = None) -> dict:

    if start_date and not end_date:
        start_date += timedelta(hours=6)
        dtes = await crud_dte.get_multi(
            db=db,
            fh_procesamiento__gte=start_date,
            schema_to_select=DTERead,
            return_as_model=True
        )
    elif end_date and not start_date:
        end_date += timedelta(hours=6)
        dtes = await crud_dte.get_multi(
            db=db,
            fh_procesamiento__lte=end_date,
            schema_to_select=DTERead,
            return_as_model=True
        )
    elif start_date and end_date:
        start_date += timedelta(hours=6)
        end_date += timedelta(hours=6)
        dtes = await crud_dte.get_multi(
            db=db,
            fh_procesamiento__gte=start_date,
            fh_procesamiento__lte=end_date,
            schema_to_select=DTERead,
            return_as_model=True
        )
    else:
        dtes = await crud_dte.get_multi(
            db=db,
            schema_to_select=DTERead,
            return_as_model=True
        )

    return {
        "total": len(dtes["data"]),
        "approved": len([dte for dte in dtes["data"] if dte.estado == "PROCESADO"]),
        "rejected": len([dte for dte in dtes["data"] if dte.estado == "RECHAZADO"]),
        "contingencia": len([dte for dte in dtes["data"] if dte.estado == "CONTINGENCIA"]),
        "anulado": len([dte for dte in dtes["data"] if dte.estado == "ANULADO"])
    }
