from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, Bot

read = on_message(block=False, priority=99)


@read.handle()
async def read_handle(bot: Bot, message: MessageEvent):
    await bot.call_api("mark_msg_as_read", message_id=message.message_id)
