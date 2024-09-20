from typing import Any

import requests

from app.core.config import settings


def firmar_documento(documento: dict) -> Any:
    """
    Firmar un documento con el servicio de firma digital
    """
    data = {
        "contentType": "application/JSON",
        "nit": settings.DTE_NIT,
        "activo": True,
        "passwordPri": settings.DTE_SIGNATURE_PASSWORD,
        "dteJson": documento,
    }
    response = requests.post(settings.DTE_SIGNATURE_URL, json=data)
    return response.json()
