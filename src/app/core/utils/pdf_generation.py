import requests

from ...core.config import settings


def generar_pdf(documento: str, sello_recibido: str, tipo_dte: str):
    try:
        response = requests.post(
            f"{settings.PDF_GENERATOR_URL}?documento={tipo_dte}",
            json={
                "documento": documento,
                "selloRecibido": sello_recibido
            }
        )
        print(response.text)
        return response.json()
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        Exception
    ) as e:
        print(f"Error al generar PDF {str(e)}")
        return {
            "pdfUrl": "",
            "jsonUrl": "",
            "rtfUrl": "",
        }
