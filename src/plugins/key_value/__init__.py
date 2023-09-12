from typing import Annotated

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from api import split
from db import set_key, get_key, all_keys

key_set = on_command(
    "key", permission=SUPERUSER
)

key_all = on_command(
    "所有key",
    aliases={
        "all_key",
        "allkey",
        "keys"
    },
    permission=SUPERUSER
)


@key_all.handle()
async def _2():
    await key_all.finish("字段表:\n" + "\n".join(await all_keys()))


@key_set.handle()
async def _1(args: Annotated[Message, CommandArg()]):
    args = split(args.extract_plain_text().strip())
    if len(args) == 2:
        await key_set.finish(
            f"设定{'成功' if await set_key(args[0], args[1]) else '失败'}\nkey:{args[0]}\nvalue:{args[1]}"
        )
    if len(args) == 1:
        value = await get_key(args[0])
        if value:
            await key_set.finish(f"key:{args[0]}\nvalue:{value}")
        else:
            await key_set.finish(f"获取失败\nkey:{args[0]}")
