from nonebot import on_command
from nonebot.permission import SUPERUSER

from .utils import call_frp_api

frp = on_command("frp", permission=SUPERUSER)


@frp.handle()
async def frp_handle():
    data = await call_frp_api("proxy/tcp")
    data = [
        f'{index}.{i["name"]}[{i["conf"]["type"]}] <- {i["conf"]["remote_port"]}'
        if i["status"] == "online" else
        f'{index}.{i["name"]} -> {i["status"]}'
        for index, i in enumerate(data["proxies"])
    ]
    msg = '\n'.join(data)
    await frp.finish(f"frp记录数:{len(data)}\n{msg}")
