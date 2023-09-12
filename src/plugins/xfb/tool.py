import json
import traceback
from datetime import datetime, timedelta
from typing import Union, List, Dict, Optional
from urllib.parse import urlparse

import httpx
from httpx import ReadTimeout, AsyncClient, ConnectTimeout
from nonebot import logger
from sqlalchemy import Column, String, DateTime, Integer, and_, desc

from db import db, get_key


async def get_ticket():
    return await get_key("xfb_ticket") or ""


def url_to_proxy(url: str) -> str:
    _ = urlparse(url)
    return "http://{0}{1}{2}.atrust.njpi.edu.cn:443{3}{4}".format(
        _.hostname.replace(".", "-"),
        (f"-{_.port}-p" if _.port else ""),
        ("-s" if _.scheme == "https" else ""),
        (_.path if _.path else "/"),
        (f"?{_.query}" if _.query else "")
    )


async def get_proxy(url: str, r: AsyncClient) -> Union[str, List[str]]:
    resp = await r.post("http://127.0.0.1:5750/proxy", json={"url": url, "key": "eya46_proxy_school"})
    data = resp.json()
    if data["success"] == 0:
        return [data["url"], data["cookie"]]
    else:
        return data["msg"]


async def get_proxy_http(r: Optional[AsyncClient] = None, url="https://www.baidu.com") -> Union[str, Dict[str, str]]:
    try:
        if (await get_key("proxy_type")) == "atrust":
            if r:
                resp = await r.post(
                    "http://127.0.0.1:5750/atrust/proxy", json={"url": url, "key": "eya46_proxy_school"}
                )
            else:
                async with httpx.AsyncClient() as r:
                    resp = await r.post(
                        "http://127.0.0.1:5750/atrust/proxy", json={"url": url, "key": "eya46_proxy_school"}
                    )
            data = resp.json()
            if data["success"] == 0:
                return {
                    "url": data.get("url"),
                    "cookie": data.get("cookie"),
                    "type": "atrust"
                }
            else:
                return data["msg"]
        else:
            if r:
                resp = await r.post("http://127.0.0.1:5750/proxy_http", json={"key": "eya46_proxy_school"})
            else:
                async with httpx.AsyncClient() as r:
                    resp = await r.post("http://127.0.0.1:5750/proxy_http", json={"key": "eya46_proxy_school"})
            data = resp.json()
            if data["success"] == 0:
                return {**data["data"], "type": "proxy"}
            else:
                return data["msg"]
    except Exception as e:
        logger.error(f"获取代理错误!\n{e}")
        return "获取代理失败"


class Power(db.Model):
    __tablename__ = "power"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room = Column(String)
    power = Column(String)
    time = Column(DateTime, default=datetime.now)


async def saveElectRecord(room: str, elect: str):
    # 房间号相同，小时相同，电量相同就不添加
    if len(await Power.query.where(and_(
            Power.room == room,
            Power.time >= datetime.now() - timedelta(hours=1),
            Power.power == elect[:-1]
    )).gino.all()) == 0:
        # logger.info("添加")
        await Power.create(room=room, power=elect[:-1])
    else:
        # logger.info("未添加")
        pass


async def getLastRecord(room: str) -> Optional[Power]:
    elects = await Power.query.where(Power.room == room).order_by(desc(Power.time)).limit(1).gino.all()
    try:
        return elects[0] if len(elects) > 0 else None
    except:
        return None


async def getElectRecord(room: str) -> Optional[str]:
    elects = await Power.query.where(Power.room == room).order_by(desc(Power.time)).limit(10).gino.all()

    if len(elects) == 0:
        return None

    _temp = f"电费记录:\n"

    # Power.time.strftime("%Y-%m-%d %Hh")
    for i in elects[::-1]:
        _temp += f'{i.time.strftime("%Y-%m-%d %Hh")} -> {i.power}度\n'

    return _temp[:-1] if _temp.endswith("\n") else _temp


async def getElect(room: str) -> (str, None):
    _data = {
        "funname": "synjones.onecard.query.elec.roominfo",
        "json": "true"
    }

    def cgdk():
        if len(room) == 5:
            if room[1] == "0":
                building = f"{room[0]}号楼"
                buildingid = "69"
            else:
                building = f"{room[0]}号楼"
                buildingid = room[0]
        else:
            building = f"{room[0]}号楼"
            buildingid = room[0]

        return json.dumps({'query_elec_roominfo': {
            'aid': '0030000000002501',
            'account': '33333',
            'room': {'roomid': room, 'room': room},
            'floor': {'floorid': '', 'floor': ''},
            'area': {'area': '1', 'areaname': ''},
            'building': {'buildingid': buildingid, 'building': building}
        }}, ensure_ascii=False)

    def sfdk():
        return json.dumps({'query_elec_roominfo': {
            'aid': '0030000000003801',
            'account': '33333',
            'room': {'roomid': '0' + room[1:4], 'room': room[1:4]},
            'floor': {'floorid': '00' + room[1], 'floor': '00' + room[1]},
            'area': {'area': '主校区', 'areaname': '主校区'},
            'building': {'buildingid': '00' + room[0], 'building': room[0] + '号楼'}}
        }, ensure_ascii=False)

    # 不同的电控系统
    if room[0] in ["1", "2", "3", "4", "5", "6", "10"]:
        _data["jsondata"] = cgdk()
    else:
        _data["jsondata"] = sfdk()

    try:
        url = "http://ykt.njpi.edu.cn:8988/web/Common/Tsm.html"
        proxy = await get_proxy_http(url=url)
        if type(proxy) == str:
            return proxy
        async with (
                httpx.AsyncClient(verify=False, proxies=proxy) if proxy.get("type", "proxy") == "proxy"
                else httpx.AsyncClient(verify=False)
        ) as client:
            res = await client.post(
                # "http://ykt.njpi.edu.cn:8988/web/Common/Tsm.html",
                # "http://210-28-10-180.vpn.njpi.edu.cn:8118/web/Common/Tsm.html",
                # "http://210-28-10-180-8988-p.vpn.njpi.edu.cn:8118/web/Common/Tsm.html",
                url if proxy.get("type", "proxy") == "proxy" else proxy.get("url"),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Cookie": proxy.get("cookie")
                },
                params=_data,
                timeout=3
            )
            if res.status_code == 502:
                return "学付宝无法连接"
            if res.status_code != 200:
                logger.error(f"学付宝code:{res.status_code}_{res.text}")
                return f"学付宝请求失败，code:{res.status_code}"
            if "系统异常" in res.text:
                return "学付宝暂时关闭"
            return res.json()["query_elec_roominfo"]["errmsg"]
    except httpx.ConnectError:
        return "代理无效"
    except Exception as e:
        if isinstance(e, AttributeError):
            return "连接校园网失败"
        print(e)
        logger.error(traceback.format_exc())
        logger.error(e)
        if isinstance(e, (ReadTimeout, ConnectTimeout)):
            return "超时"
        return "报错"


if __name__ == '__main__':
    import asyncio


    async def main():
        from db import link_db, close_db
        await link_db()
        print(await getElect("1145"))
        await close_db()


    print(
        asyncio.get_event_loop().run_until_complete(main())
    )
