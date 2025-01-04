import requests

from ...core.config import settings


def generar_pdf(documento: str, sello_recibido: str, tipo_dte: str):
    try:
        response = requests.post(
            f"{settings.PDF_GENERATOR_URL}?documento={tipo_dte}",
            json={
                "nit": settings.DTE_NIT,
                "documento": documento,
                "selloRecibido": sello_recibido
            }
        )
        return response.json()
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception
    ) as e:
        return {
            "pdfUrl": "",
            "jsonUrl": "",
            "rtfUrl": "",
        }
