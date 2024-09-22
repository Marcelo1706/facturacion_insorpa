import time

import requests

from app.core.config import settings
from app.core.exceptions.http_exceptions import UnprocessableEntityException

token_storage = {
    "token": None,
    "expires_at": 0,
}


def obtain_new_token():
    data = {
        "user": settings.DTE_NIT,
        "pwd": settings.DTE_AUTH_PASSWORD
    }
    payload = "&".join([f"{key}={value}" for key, value in data.items()])
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.post(settings.DTE_AUTH_URL, data=payload, headers=headers)
    try:
        if response.status_code == 200:
            response_data = response.json()
            token_storage["token"] = response_data["body"]["token"]
            token_storage["expires_at"] = time.time() + 24 * 3600
            return token_storage["token"]
        else:
            return None
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException, Exception) as e:
        raise UnprocessableEntityException(str(e))
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise UnprocessableEntityException("No se pudo obtener el token")

def get_token():
    if token_storage["token"] is None or token_storage["expires_at"] < time.time():
        return obtain_new_token()
    return token_storage["token"]
