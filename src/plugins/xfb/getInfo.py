import json
from typing import Union, List

import httpx
from httpx import AsyncClient

from nonebot import logger

from .tool import get_proxy_http, get_ticket


# test
def get_info(proxy, acc="11451"):
    resp = httpx.post(
        "http://ykt.njpi.edu.cn/User/GetCardInfoByAccount",
        data={"acc": str(acc), "json": "true"},
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "hallticket=11451;"
        }, proxies=proxy
    )
    if resp.status_code != 200:
        return None
    info = json.loads(resp.json()["Msg"])['query_card']["card"][0]
    return info


async def get_xfb_info(acc: Union[str, int]):
    url = "http://ykt.njpi.edu.cn/User/GetCardInfoByAccount"
    proxy = await get_proxy_http(url=url)
    if type(proxy) == str:
        return proxy
    async with (
            httpx.AsyncClient(verify=False, proxies=proxy) if proxy.get("type", "proxy") == "proxy"
            else httpx.AsyncClient(verify=False)
    ) as r:
        r: AsyncClient
        web = await r.post(
            url if proxy.get("type", "proxy") == "proxy" else proxy.get("url"),
            data={"acc": str(acc), "json": "true"},
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Cookie": f"hallticket={await get_ticket()}; {proxy.get('cookie')}"
            }
        )
        if web.status_code != 200:
            return None

    try:
        info = json.loads(web.json()["Msg"])['query_card']
        if len(info["card"]) <= 0:
            return info["errmsg"]
        else:
            return info["card"][0]
    except:
        logger.debug(web.text)
        return "查询解析失败!"


async def yue(acc: Union[str, int]):
    res = await get_xfb_info(acc)
    if res is None:
        return "查询失败"
    if isinstance(res, str):
        return res
    if isinstance(res, dict):
        return f'过渡余额:{int(res["unsettle_amount"]) / 100}\n' \
               f'余额:{int(res["db_balance"]) / 100}\n' \
               f'总余额:{(int(res["unsettle_amount"]) + int(res["db_balance"])) / 100}'
    return "解析失败"


if __name__ == '__main__':
    import asyncio

    asyncio.get_event_loop().run_until_complete(get_xfb_info("11451"))
