from decimal import Decimal
import json
from datetime import datetime, timedelta
from typing import Annotated, Any, Optional

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


@router.get(
    "/dtes-table",
    response_model=PaginatedListResponse[dict],
    dependencies=[Depends(get_current_user)])
async def read_dtes_table(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    cod_generacion: str = None,
    numero_control: str = None,
    page: int = 1,
    items_per_page: int = 10,
    start_date: datetime = None,
    end_date: datetime = None,
    status: str = None,
    tienda: str = None,
    transaccion: str = None,
    limit: int | None = 10
) -> dict:
    pass

def format_currency(value: float | Decimal | None) -> str:
    if value is None:
        return "$0.00"
    return f"${float(value):.2f}"


def process_dte(dte: DTERead) -> dict:
    doc = json.loads(dte.documento) or {}
    resumen = doc.get("resumen", {})
    tipo_dte = dte.tipo_dte
    prepared = {
        "fh_procesamiento": dte.fh_procesamiento,
        "tipo_dte": tipo_dte,
        "enlace_pdf": dte.enlace_pdf,
        "enlace_json": dte.enlace_json,
        "enlace_ticket": dte.enlace_ticket,
        "cod_generacion": dte.cod_generacion,
        "numero_control": dte.numero_control,
        "sello_recibido": dte.sello_recibido,
        "estado": dte.estado,
        "observaciones": dte.observaciones,
        "tienda": "",
        "transaccion": "",
        "receptor": "",
        "neto": "$0.00",
        "iva": "$0.00",
        "total": "$0.00"
    }

    apendice = doc.get("apendice", [])
    if apendice:
        for item in apendice:
            if item.get("campo") == "Tienda":
                prepared["tienda"] = item.get("valor", "")
            elif item.get("campo") == "Transaccion":
                prepared["transaccion"] = item.get("valor", "")

    receptor = None
    if tipo_dte == "14":
        receptor = doc.get("sujetoExcluido")
    else:
        receptor = doc.get("receptor")

    if receptor:
        nombre = receptor.get("nombre", "")
        documento = receptor.get("nit") or receptor.get("numDocumento") or ""
        prepared["receptor"] = f"{nombre}<br>{documento}"

    # Cálculos por tipo de DTE
    match tipo_dte:
        case "01":
            total = resumen.get("totalPagar")
            prepared["neto"] = format_currency(total)
            prepared["iva"] = "$0.00"
            prepared["total"] = format_currency(total)
        case "03":
            subtotal = resumen.get("subTotalVentas")
            iva = subtotal * 0.13 if subtotal else 0
            prepared["neto"] = format_currency(subtotal)
            prepared["iva"] = format_currency(iva)
            prepared["total"] = format_currency(resumen.get("totalPagar"))
        case "04" | "05":
            subtotal = resumen.get("subTotalVentas")
            iva = subtotal * 0.13 if subtotal else 0
            prepared["neto"] = format_currency(subtotal)
            prepared["iva"] = format_currency(iva)
            prepared["total"] = format_currency(resumen.get("montoTotalOperacion"))
        case "07":
            prepared["neto"] = format_currency(resumen.get("totalSujetoRetencion"))
            prepared["iva"] = format_currency(resumen.get("totalIVAretenido"))
            prepared["total"] = format_currency(resumen.get("totalSujetoRetencion"))
        case "11":
            total = resumen.get("totalPagar")
            prepared["neto"] = format_currency(total)
            prepared["iva"] = "$0.00"
            prepared["total"] = format_currency(total)
        case "14":
            total = resumen.get("totalCompra")
            prepared["neto"] = format_currency(total)
            prepared["iva"] = "$0.00"
            prepared["total"] = format_currency(total)

    return prepared
