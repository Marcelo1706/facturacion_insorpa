import json
from datetime import datetime

import pytz
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.exceptions.http_exceptions import UnprocessableEntityException
from ...core.utils.auth_mh import get_token
from ...core.utils.mail import send_mail
from ...core.utils.numero_control import update_numero_control
from ...core.utils.pdf_generation import generar_pdf
from ...crud.crud_dte import crud_dte
from ...crud.crud_evento import crud_evento
from ...schemas.dte import DTECreate, DTERead
from ...schemas.evento import EventoCreate


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
            documento_sin_firma["selloRecibido"] = response_data["selloRecibido"]
            enlaces = generar_pdf(
                documento=json.dumps(documento_sin_firma),
                sello_recibido=response_data["selloRecibido"],
                tipo_dte=tipoDte
            )
            dte_data: DTERead = await crud_dte.create(
                db=db,
                object=DTECreate(
                    cod_generacion=codGeneracion,
                    numero_control=documento_sin_firma["identificacion"]["numeroControl"],
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
            await update_numero_control(db=db, tipo_dte=tipoDte)

            if tipoDte == "14":
                receptor_mail = documento_sin_firma.get("sujetoExcluido", {}).get("correo", None)
                nombre_receptor = documento_sin_firma.get("sujetoExcluido", {}).get("nombre", "Cliente")
            else:
                receptor_mail = documento_sin_firma.get("receptor", {}).get("correo", None)
                nombre_receptor = documento_sin_firma.get("receptor", {}).get("nombre", "Cliente")

            if not settings.DISABLE_EMAIL:
                send_mail(
                    send_to=[receptor_mail or "facturas@facturacion-insorpa.com"],
                    subject="Documento Tributario Electrónico",
                    message=(f"Estimado(a) {nombre_receptor},\n\n"
                                "Adjunto encontrará su documento tributario electrónico:\n\n"
                                f"Código de Generación: {codGeneracion}\n"
                                f"Número de Control: {documento_sin_firma['identificacion']['numeroControl']}\n"
                                f"Sello de Recepción: {response_data['selloRecibido']}\n"
                                f"Fecha de Procesamiento: {datetime.now(pytz.timezone('America/El_Salvador'))}\n"
                                f"Estado: {response_data['estado']}\n"),
                    files=[
                        {"type": "PDF", "link": enlaces["pdfUrl"]},
                        {"type": "JSON", "link": enlaces["jsonUrl"]}
                    ]
                )
            return dte_data
        else:
            dte_data: DTERead = await crud_dte.create(
                db=db,
                object=DTECreate(
                    cod_generacion=codGeneracion,
                    numero_control=documento_sin_firma["identificacion"]["numeroControl"],
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
                numero_control=documento_sin_firma["identificacion"]["numeroControl"],
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
        await update_numero_control(db=db, tipo_dte=tipoDte)
        return dte_data


async def contingencia_dte(documento_firmado: str, documento_sin_firma: dict, db: AsyncSession):
    try:
        token = get_token()
        headers = {
            "Authorization": token,
            "Content-Type": "application/JSON",
            "User-Agent": "DTE-APP"
        }
        data = {
            "nit": settings.DTE_NIT,
            "documento": documento_firmado
        }
        response = requests.post(settings.DTE_CONTINGENCIA_URL, json=data, headers=headers)

        await crud_evento.create(
            db=db,
            object=EventoCreate(
                tipo_evento="CONTINGENCIA",
                evento=json.dumps(documento_sin_firma),
                respuesta_mh=json.dumps(response.json())
            )
        )
        return response.json()

    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        return {"message": "Error al enviar el evento de contingencia: " + str(e)}
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return {"message": "Error de conexión con el servidor de Hacienda"}


async def anulacion_dte(documento_firmado: str, documento_sin_firma: dict, db: AsyncSession):
    try:
        token = get_token()
        headers = {
            "Authorization": token,
            "Content-Type": "application/JSON",
            "User-Agent": "DTE-APP"
        }
        data = {
            "ambiente": documento_sin_firma["identificacion"]["ambiente"],
            "idEnvio": 1,
            "version": documento_sin_firma["identificacion"]["version"],
            "documento": documento_firmado
        }
        response = requests.post(settings.DTE_ANULACION_URL, json=data, headers=headers)

        await crud_evento.create(
            db=db,
            object=EventoCreate(
                tipo_evento="INVALIDACION",
                evento=json.dumps(documento_sin_firma),
                respuesta_mh=json.dumps(response.json())
            )
        )
        response_data = response.json()

        response_data["fhProcesamiento"] = datetime.strptime(response_data["fhProcesamiento"], "%d/%m/%Y %H:%M:%S")

        if response_data["estado"] == "PROCESADO":
            # Update the DTE status to "ANULADO"
            await crud_dte.update(
                db=db,
                allow_multiple=True,
                cod_generacion=documento_sin_firma["documento"]["codigoGeneracion"],
                estado="PROCESADO",
                object={
                    "estado": "ANULADO",
                }
            )


        return response_data

    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        return {"message": "Error al enviar el evento de invalidación: " + str(e)}
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return {"message": "Error de conexión con el servidor de Hacienda"}


async def consulta_dte(codigo_generacion: str, tdte: str):
    token = get_token()
    headers = {"Authorization": f"{token}"}
    data = {
        "nitEmisor": settings.DTE_NIT,
        "tdte": tdte,
        "codigoGeneracion": codigo_generacion,
    }
    response = requests.post(settings.DTE_CONSULTAS_URL, json=data, headers=headers)
    return response.json()
