import time

import requests

from app.core.config import settings

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
    if response.status_code == 200:
        response_data = response.json()
        token_storage["token"] = response_data["body"]["token"]
        token_storage["expires_at"] = time.time() + 24 * 3600
        return token_storage["token"]
    else:
        return None


def get_token():
    if token_storage["token"] is None or token_storage["expires_at"] < time.time():
        return obtain_new_token()
    return token_storage["token"]