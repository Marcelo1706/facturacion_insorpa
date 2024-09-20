import json
from datetime import datetime

import requests
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.utils.auth_mh import get_token
from ...crud.crud_dte import crud_dte
from ...schemas.dte import DTECreate, DTERead


async def recepcion_dte(
    codGeneracion: str,
    ambiente: str,
    idEnvio: str,
    version: int,
    tipoDte: str,
    documento_firmado: str,
    documento_sin_firma: str,
    db: AsyncSession
) -> DTERead:
    token = get_token()
    headers = {"Authorization": token}
    data = {
        "ambiente": ambiente,
        "idEnvio": idEnvio,
        "version": version,
        "tipoDte": tipoDte,
        "documento": documento_firmado
    }
    response = requests.post(settings.DTE_RECEPTION_URL, json=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        dte_data: DTERead = await crud_dte.create(
            db=db,
            object=DTECreate(
                cod_generacion=codGeneracion,
                sello_recibido=response_data["selloRecibido"],
                estado=response_data["estado"],
                documento=json.dumps(documento_sin_firma),
                fh_procesamiento=datetime.now(),
                observaciones=json.dumps(response_data["observaciones"]),
                tipo_dte=tipoDte,
                enlace_pdf="",
                enlace_json="",
                enlace_ticket=""
            )
        )
        return dte_data
    else:
        return {"status": response.status_code, "message": response.text}
