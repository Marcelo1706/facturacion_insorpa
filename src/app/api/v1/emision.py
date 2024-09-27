from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import BadRequestException
from ...core.utils.numero_control import generar_numero_control
from ...core.utils.recepcion_dte import recepcion_dte
from ...core.utils.signing import firmar_documento
from ...crud.crud_secuencia import crud_secuencia
from ...schemas.secuencia import SecuenciaRead
from ..dependencies import get_current_user

router = APIRouter(tags=["Emisión de Documentos Tributarios Electrónicos"])


@router.post(
    "/dte",
    dependencies=[Depends(get_current_user)])
async def send_dte(
    request: Request,
    dte: dict[str, Any],
    db: Annotated[AsyncSession, Depends(async_get_db)]
    ) -> Any:

    correlativo = await crud_secuencia.get(
        db=db,
        schema_to_select=SecuenciaRead,
        tipo_dte=dte["identificacion"]["tipoDte"]
    )
    if not correlativo:
        raise BadRequestException("Error al obtener correlativo")

    dte["identificacion"]["numeroControl"] = generar_numero_control(
        correlativo=correlativo["secuencia"],
        sucursal=dte["emisor"].get("codEstable", "0001"),
        punto_venta=dte["emisor"].get("codPuntoVenta", "01"),
        tipo_dte=dte["identificacion"]["tipoDte"]
    )

    documento_firmado = firmar_documento(dte)
    if not documento_firmado["status"] == "OK":
        raise BadRequestException("Error al firmar documento")

    respuesta_hacienda = await recepcion_dte(
        codGeneracion=dte["identificacion"]["codigoGeneracion"],
        ambiente=dte["identificacion"]["ambiente"],
        idEnvio=1,
        version=dte["identificacion"]["version"],
        tipoDte=dte["identificacion"]["tipoDte"],
        documento_firmado=documento_firmado["body"],
        documento_sin_firma=dte,
        db=db
    )

    return respuesta_hacienda
