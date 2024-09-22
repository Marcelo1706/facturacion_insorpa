import json
from datetime import datetime

import requests
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.exceptions.http_exceptions import UnprocessableEntityException
from ...core.utils.auth_mh import get_token
from ...core.utils.pdf_generation import generar_pdf
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
    try:
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
        response_data = response.json()

        if response.status_code == 200:
            enlaces = generar_pdf(
                documento=json.dumps(documento_sin_firma),
                sello_recibido=response_data["selloRecibido"],
                tipo_dte=tipoDte
            )

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
                    enlace_pdf=enlaces["pdfUrl"],
                    enlace_json=enlaces["jsonUrl"],
                    enlace_ticket=enlaces["rtfUrl"]
                )
            )
            return dte_data
        else:
            dte_data: DTERead = await crud_dte.create(
                db=db,
                object=DTECreate(
                    cod_generacion=codGeneracion,
                    sello_recibido="",
                    estado="RECHAZADO",
                    documento=json.dumps(documento_sin_firma),
                    fh_procesamiento=datetime.now(),
                    observaciones=f"{response_data.get('descripcionMsg')} {response_data.get('observaciones')}",
                    tipo_dte=tipoDte,
                    enlace_pdf="",
                    enlace_json="",
                    enlace_ticket=""
                )
            )
            return dte_data
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        raise UnprocessableEntityException(str(e))
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        enlaces = generar_pdf(
            documento=documento_sin_firma,
            sello_recibido="",
            tipo_dte=tipoDte
        )
        dte_data: DTERead = await crud_dte.create(
            db=db,
            object=DTECreate(
                cod_generacion=codGeneracion,
                sello_recibido="",
                estado="CONTINGENCIA",
                documento=json.dumps(documento_sin_firma),
                fh_procesamiento=datetime.now(),
                observaciones=json.dumps({"error": str(e)}),
                tipo_dte=tipoDte,
                enlace_pdf=enlaces["pdfUrl"],
                enlace_json=enlaces["jsonUrl"],
                enlace_ticket=enlaces["rtfUrl"]
            )
        )
        return dte_data
