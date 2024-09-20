from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import BadRequestException
from ...core.utils.recepcion_dte import recepcion_dte
from ...core.utils.signing import firmar_documento

router = APIRouter(tags=["Emisión de Documentos"])


@router.post(
    "/factura",
    dependencies=[Depends(get_current_user)])
async def create_factura(
    request: Request,
    dte: dict[str, Any],
    db: Annotated[AsyncSession, Depends(async_get_db)]
    ) -> Any:
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
