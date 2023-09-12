from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor

from db import get_key

supers = get_driver().config.superusers


@event_preprocessor
async def check_ban(evnet: MessageEvent):
    global supers
    if str(evnet.user_id) in supers:
        return

    if isinstance(evnet, GroupMessageEvent):
        if await get_key(f"ban_group") == "on":
            raise IgnoredException("群聊禁用阶段")

        ban_type = await get_key("ban_type")
        if ban_type == "white":
            if await get_key(f"allow_group_{evnet.group_id}") != "on":
                raise IgnoredException(f"白名单禁用阶段,非白名单群:{evnet.group_id}")

        if ban_type == "black":
            if await get_key(f"ban_group_{evnet.group_id}") == "on":
                raise IgnoredException(f"黑名单禁用阶段,黑名单群:{evnet.group_id}")

    if isinstance(evnet, PrivateMessageEvent):
        if await get_key(f"ban_private") == "on":
            raise IgnoredException("私聊禁用阶段")
