import httpx
from httpx import AsyncClient
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment

ksj_60 = on_command("看世界", aliases={"60s看世界", "ksj"})


@ksj_60.handle()
async def _():
    try:
        async with httpx.AsyncClient() as r:
            r: AsyncClient
            try:
                await ksj_60.send(
                    MessageSegment.image(file=(await r.get("https://api.iyk0.com/60s")).json()["imageUrl"]))
                return
            except:
                pass
            await ksj_60.send(MessageSegment.image(file=(await r.get("https://api.2xb.cn/zaob")).json()["imageUrl"]))
    except:
        await ksj_60.send("获取失败")
