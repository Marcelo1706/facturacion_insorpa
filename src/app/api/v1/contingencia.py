from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import BadRequestException
from ...core.utils.recepcion_dte import contingencia_dte
from ...core.utils.signing import firmar_documento
from ..dependencies import get_current_user

router = APIRouter(tags=["Contingencia"])


@router.post(
    "/contingencia/local",
    dependencies=[Depends(get_current_user)])
async def send_contingencia(
    request: Request,
    dte: dict[str, Any],
    db: Annotated[AsyncSession, Depends(async_get_db)]
    ) -> Any:
    documento_firmado = firmar_documento(dte)

    if not documento_firmado["status"] == "OK":
        raise BadRequestException("Error al firmar documento")

    respuesta_hacienda = await contingencia_dte(
        documento_firmado=documento_firmado["body"],
        documento_sin_firma=dte,
        db=db
    )

    return respuesta_hacienda
