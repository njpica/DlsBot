import json

import httpx
from httpx import AsyncClient
from nonebot import logger

from .tool import get_proxy_http, get_ticket

Pay_Url = "http://ykt.njpi.edu.cn/User/Account_Pay"
Pay_Url_Referer = "http://ykt.njpi.edu.cn/PPage/ComePage?flowID=13"


# test
def pay_test(money: int):
    return httpx.post(
        "http://ykt.njpi.edu.cn/User/Account_Pay",
        headers={
            "Cookie": f"hallticket=114514;sourcetypeticket=114514",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://ykt.njpi.edu.cn/PPage/ComePage?flowID=13"
        },
        data={
            "account": "114514",
            "acctype": "###",
            "tranamt": str(money),
            "objtype": "own",
            "paytype": "###",
            "qpwd": "加密的密码",
            "client_type": "wap",
            "paymethod": "",
            "iacctype": "acc",
            "spbill_create_ip": "",
            "json": "true"
        },
        proxies={'http://': 'http://114514', 'https://': 'http://114514'}
    )


async def pay_money(money: int):
    url = Pay_Url
    proxy = await get_proxy_http(url=url)
    if type(proxy) == str:
        return proxy
    async with (
            httpx.AsyncClient(verify=False, proxies=proxy) if proxy.get("type", "proxy") == "proxy"
            else httpx.AsyncClient(verify=False)
    ) as r:
        r: AsyncClient
        tk = await get_ticket()
        res = await r.post(
            url if proxy.get("type", "proxy") == "proxy" else proxy.get("url"),
            headers={
                "Cookie": f"hallticket={tk}; sourcetypeticket={tk}; {proxy.get('cookie')}",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": Pay_Url_Referer
            },
            data={
                "account": "11451",
                "acctype": "###",
                "tranamt": str(money),
                "objtype": "own",
                "paytype": "###",
                "qpwd": "加密的密码",
                "client_type": "wap",
                "paymethod": "",
                "iacctype": "acc",
                "spbill_create_ip": "",
                "json": "true"
            }
        )
        try:
            _ = res.json()["Msg"]
            return json.loads(res.json()["Msg"])["transfer"]["errmsg"]
        except KeyError:
            logger.error(res.text)
            return "解析失败"


if __name__ == '__main__':
    import asyncio

    print(asyncio.get_event_loop().run_until_complete(
        pay_money(1)
    ))
