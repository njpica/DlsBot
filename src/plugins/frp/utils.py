from base64 import b64encode
from typing import Union

import httpx


def encode_authorization(account: str, password: str):
    return b64encode(f"{account}:{password}".encode()).decode()


def get_authorization():
    return encode_authorization("eya46", "eya46eya46")


async def call_frp_api(api: str, port: int = 6688, ip: str = "127.0.0.1") -> Union[dict, list]:
    async with httpx.AsyncClient() as r:
        return (await r.get(
            f"http://{ip}:{port}/api/{api}",
            headers={
                "Authorization": f"Basic {get_authorization()}"
            }
        )).json()
