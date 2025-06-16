import json
from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.utils.recepcion_dte import consulta_dte
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_dte import crud_dte
from ...crud.crud_evento import crud_evento
from ...schemas.dte import DTERead
from ...schemas.evento import EventoRead

router = APIRouter(tags=["Consulta de DTEs"])


@router.get(
    "/dtes",
    response_model=PaginatedListResponse[DTERead],
    dependencies=[Depends(get_current_user)]
)
async def read_dtes(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    cod_generacion: str = None,
    page: int = 1,
    items_per_page: int = 10,
    start_date: datetime = None,
    end_date: datetime = None
) -> dict:
    filters = {
        "offset": compute_offset(page, items_per_page),
        "limit": items_per_page,
        "schema_to_select": DTERead,
    }

    if cod_generacion:
        filters["cod_generacion"] = cod_generacion
    if start_date:
        filters["fh_procesamiento__gte"] = start_date + timedelta(hours=6)
    if end_date:
        filters["fh_procesamiento__lte"] = end_date + timedelta(hours=6)

    dte_data = await crud_dte.get_multi(db=db, **filters)

    response: dict[str, Any] = paginated_response(
        crud_data=dte_data,
        page=page,
        items_per_page=items_per_page
    )
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
        dte_data = {
            "id": 0,
            "cod_generacion": "",
            "numero_control": "",
            "sello_recibido": None,
            "estado": "NO PROCESADO",
            "documento": "",
            "fh_procesamiento": datetime.now(),
            "observaciones": "No registrado en Octopus",
            "tipo_dte": "01",
            "enlace_pdf": None,
            "enlace_json": None,
            "enlace_ticket": None
        }

    dte_data["respuesta_mh"] = await consulta_dte(codGeneracion, dte_data["tipo_dte"]) or {"message": "Sin Respuesta"}

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
            return_as_model=True,
            limit=None
        )
    elif end_date and not start_date:
        end_date += timedelta(hours=6)
        dtes = await crud_dte.get_multi(
            db=db,
            fh_procesamiento__lte=end_date,
            schema_to_select=DTERead,
            return_as_model=True,
            limit=None
        )
    elif start_date and end_date:
        start_date += timedelta(hours=6)
        end_date += timedelta(hours=6)
        dtes = await crud_dte.get_multi(
            db=db,
            fh_procesamiento__gte=start_date,
            fh_procesamiento__lte=end_date,
            schema_to_select=DTERead,
            return_as_model=True,
            limit=None
        )
    else:
        min_date = datetime(2024, 11, 1, 0, 0, 0)
        max_date = datetime.now()
        dtes = await crud_dte.get_multi(
            db=db,
            fh_procesamiento__gte=min_date,
            fh_procesamiento__lte=max_date,
            schema_to_select=DTERead,
            return_as_model=True,
            limit=None
        )

    return {
        "total": len(dtes["data"]),
        "approved": len([dte for dte in dtes["data"] if dte.estado == "PROCESADO"]),
        "rejected": len([dte for dte in dtes["data"] if dte.estado == "RECHAZADO"]),
        "contingencia": len([dte for dte in dtes["data"] if dte.estado == "CONTINGENCIA"]),
        "anulado": len([dte for dte in dtes["data"] if dte.estado == "ANULADO"])
    }


@router.get(
    "/reconciliar_anulados",
    response_model=dict,
    dependencies=[Depends(get_current_user)])
async def reconciliar_anulados(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict:
    """
    Endpoint to reconcile annulled DTEs.
    This endpoint will check for annulled DTEs and update their status accordingly.
    """
    eventos = await crud_evento.get_multi(
        db=db,
        tipo_evento="INVALIDACION",
        schema_to_select=EventoRead,
        return_as_model=True,
        limit=None
    )
    reconciliados = 0
    anulados = 0
    for evento in eventos["data"]:
        json_evento = json.loads(evento.evento)
        json_respuesta = json.loads(evento.respuesta_mh)
        if json_respuesta.get("estado") == "PROCESADO":
            anulados += 1
            await crud_dte.update(
                db=db,
                allow_multiple=True,
                cod_generacion=json_evento["documento"]["codigoGeneracion"],
                estado="PROCESADO",
                object={
                    "estado": "ANULADO",
                }
            )
    return {
        "message": f"{anulados} DTEs anulados.",
        "anulados": anulados
    }
