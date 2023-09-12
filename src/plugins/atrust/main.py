import asyncio
import json
import time
from datetime import datetime
from typing import Optional, Dict, Tuple, Union, Type

from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.internal.matcher import Matcher
from playwright.async_api import Browser, Page, BrowserContext, Error

from .bean import Url
from .browser import get_browser

client: Optional[Browser] = None


class VPN:
    def __init__(self):
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        # self._page_alive: Optional[Page] = None
        self.last_alive_time = ""

    async def logout(self) -> int:
        content = await self.get_context()
        resp = await content.request.post(Url.logout.value, headers={"Cookie": await self.get_cookie()})
        return resp.status

    async def get_context(self) -> BrowserContext:
        if not self._browser:
            self._browser = await get_browser(headless=True)
        if not self._context:
            self._context = await self._browser.new_context(storage_state='context.json')
        return self._context

    async def get_page(self) -> Page:
        return await (await self.get_context()).new_page()

    # async def get_page_alive(self) -> Page:
    #     if not self._page_alive or self._page_alive.is_closed():
    #         self._page_alive = await self.get_page()
    #     return self._page_alive

    async def save(self):
        await (await self.get_context()).storage_state(path='context.json')

    def update_time(self):
        self.last_alive_time = str(datetime.now())[:-7]

    async def keep_alive(self):
        page = await self.get_page()
        try:
            if await self.if_login():
                try:
                    await page.goto(
                        f"https://at.njpi.edu.cn/?t={int(time.time() * 1000)}"
                    )
                    await asyncio.sleep(3)
                    await page.request.get(f"http://www-baidu-com-s.atrust.njpi.edu.cn:443/")
                except Error:
                    logger.debug(f"atrust VPN保活失败")
                    return False
                logger.debug(f"atrust VPN保活成功")
                return True
            else:
                logger.debug(f"atrust VPN保活失败")
                return False
        finally:
            self.update_time()
            await page.close()
            await self.save()

    async def login(self, matcher: Union[Matcher, Type[Matcher]]):
        if await self.if_login():
            return "已登陆"
        page = await self.get_page()
        await matcher.send("请用企业微信扫码(60s内)")
        try:
            await page.goto(Url.login.value)
            img = "https:" + await page.frame_locator("#scan_qrcode_iframe") \
                .frame_locator("iframe") \
                .locator('//*[@id="wwopen.ssoPage_$"]/div/div/div[2]/div[1]/img').get_attribute("src")
            await matcher.send(MessageSegment.image(img))
            start_time = time.time()

            while time.time() - start_time <= 57:
                if Url.center.value in page.url or await self.if_login():
                    break
                await asyncio.sleep(1)
            if await self.if_login():
                await matcher.send("登录成功")
            else:
                await matcher.send("登录超时")
        finally:
            await page.close()
            await self.save()

    async def get_cookie(self) -> Optional[str]:
        if not await self.if_login():
            return None

        window: BrowserContext = await self.get_context()
        cookies = await window.cookies("https://at.njpi.edu.cn/portal/service_center.html#/app_center/home")

        try:
            for i in cookies:
                if i["name"] == "sdp_user_token" or i["name"] == "sid":
                    return f"sdp_user_token={i['value']}"
            return None
        except:
            return None

    async def get_login_info(self) -> Tuple[bool, Dict[str, str]]:
        try:
            resp = await (await self.get_context()).request.get(Url.onlineInfo.value)
            data = await resp.json()
        except Exception as e:
            logger.error(f"获取登陆信息失败:\n{e}")
            data = {}
        return data.get("code") == 0, data

    async def if_login(self) -> bool:
        try:
            resp = await (await self.get_context()).request.get(Url.onlineInfo.value)
            data = await resp.text()
        except Exception as e:
            logger.error(f"if_login[请求错误]:{e}")
            return False
        try:
            return json.loads(data)["code"] == 0
        except Exception as e:
            logger.error(f"if_login[判断错误]:{e}")
            return False
