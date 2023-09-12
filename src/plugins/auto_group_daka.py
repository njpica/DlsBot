from typing import Optional, Annotated

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot import require, get_bot, on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.rule import to_me

from db import get_key

scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job('cron', day="*", hour=0, minute=1, name="自动群打卡", timezone='Asia/Shanghai')
async def scheduler_sign(default_bot: Optional[Bot] = None, if_return: bool = False) -> Optional[list]:
    if default_bot is None:
        bot: Optional[Bot] = get_bot()
    else:
        bot = default_bot

    if bot is None:
        return

    success_groups = []

    groups = await bot.get_group_list()

    for group_id in groups:
        gid = group_id.get("group_id")
        if await get_key(f"auto_sign_{gid}") == "on":
            try:
                await bot.call_api("send_group_sign", group_id=gid)
                success_groups.append(gid)
            except:
                pass

    return success_groups if if_return else None


auto_group_daka = on_command("立即群打卡", permission=SUPERUSER, rule=to_me())


@auto_group_daka.handle()
async def auto_group_daka_handle(bot: Bot, cmd: Annotated[Message, CommandArg()]):
    if (group_id := cmd.extract_plain_text()).isdigit():
        try:
            await bot.send_group_sign(group_id=int(group_id))
            auto_group_daka.finish(f"打卡成功，已为群{group_id}打卡")
        except Exception as e:
            auto_group_daka.finish(f"打卡失败：{e}")
    else:
        sign_groups_data = await scheduler_sign(bot, True)
        if sign_groups_data:
            auto_group_daka.finish(f"打卡成功，已为群{','.join(sign_groups_data)}打卡")
