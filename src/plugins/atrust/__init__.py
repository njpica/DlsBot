from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from nonebot import on_command, require, get_app, logger
from nonebot.internal.matcher import Matcher
from nonebot.permission import SUPERUSER

from .bean import Url
from .browser import get_browser
from .main import VPN
from .tool import url_to_proxy

login_vpn = on_command("登录VPN", aliases={"登录vpn", "登陆VPN", "登陆vpn"})
vpn_status = on_command("vpn状态", aliases={"VPN状态"}, permission=SUPERUSER)
vpn_re = on_command("重置vpn", aliases={"重置VPN"}, permission=SUPERUSER)
vpn_alive_now = on_command("vpn保活", aliases={"VPN保活", "立即保活"}, permission=SUPERUSER)
app: FastAPI = get_app()
vpn = VPN()
keys = ["eya46_proxy_school"]

scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler


@vpn_alive_now.handle()
@scheduler.scheduled_job("interval", minutes=3)
async def keep_alive_3(matcher: Optional[Matcher] = None):
    if 0 <= datetime.now().hour <= 6:
        if matcher:
            await matcher.finish("学校VPN暂时关闭")
    res = await vpn.keep_alive()
    if matcher:
        await matcher.finish("保活" + "成功" if res else "失败")


@vpn_re.handle()
async def vpn_re_handle():
    global vpn
    try:
        code = await vpn.logout()
        await vpn_re.send(f"重置VPN结束:{code}")
    except Exception as e:
        await vpn_re.send(f"重置VPN失败:\n{e}")


@vpn_status.handle()
async def vpn_status_handle():
    last_alive_time = vpn.last_alive_time or '无'
    if_login, info = await vpn.get_login_info()
    logger.debug("登陆信息如下:")
    logger.debug(info)
    data = info.get("data", {})
    msg = f"状态:{'已登陆' if if_login else '未登陆'}\n" + \
          f"页面数:{len((await vpn.get_context()).pages)}\n" + \
          f'登陆时间:{data.get("loginTime", "无")}\n' + \
          f"更新时间:{last_alive_time}\n" \
          f'认证方式:{data.get("authType", "未知")}[{data.get("domain", "未知")}]'

    await vpn_status.send(msg)


@app.post("/atrust/proxy")
async def get_proxy(data: dict):
    url = data.get("url")
    key = data.get("key")
    if not url or not key:
        return {"success": -1, "msg": "缺少参数"}
    if key not in keys:
        return {"success": -2, "msg": "key错误"}
    if 0 <= datetime.now().hour <= 6:
        return {"success": -5, "msg": "太晚喽，学校VPN睡觉去了\n不像机器人我，7*24h工作QwQ~"}

    if not await vpn.if_login():
        return {"success": -3, "msg": "vpn未登陆,请发送 登录VPN"}
    try:
        cookie = await vpn.get_cookie()
    except Exception as e:
        logger.error(e)
        return {
            "success": -5,
            "msg": "获取cookie报错"
        }
    if cookie:
        if not urlparse(url).hostname.endswith('atrust.njpi.edu.cn'):  # type: ignore
            url = url_to_proxy(url)
        return {
            "success": 0,
            "url": url,
            "cookie": cookie
        }
    else:
        return {
            "success": -4,
            "msg": "获取cookie失败"
        }


@login_vpn.handle()
async def login_vpn_handle():
    if await vpn.if_login():
        await login_vpn.finish("VPN已登录")

    await vpn.login(login_vpn)
