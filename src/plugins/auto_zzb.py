from typing import Optional
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot import require, get_bot
from nonebot.adapters.onebot.v11 import Bot

from db import get_key

scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler

zzb_date = datetime(2024, 3, 19, 9, 0, 0)

groups = []


@scheduler.scheduled_job('cron', day="*", hour=8, minute=5, name="每日专本日期播报", timezone='Asia/Shanghai')
async def auto_send_zzb_time():
    bot: Bot = get_bot()
    left_time = zzb_date - datetime.now()

    if left_time.days < 0:
        return
    for i in groups:
        try:
            await bot.send_group_msg(
                group_id=i,
                message=f"{datetime.now().year}转本还剩约 {left_time.days} 天~"
            )
        except:
            pass


# @scheduler.scheduled_job("interval", hours=2, timezone='Asia/Shanghai', name="自动改转转本时间")
@scheduler.scheduled_job("cron", day="*", hour=3, timezone='Asia/Shanghai', name="自动改转转本时间")
async def auto_set_group_name_to_zzb_time():
    bot: Optional[Bot] = get_bot()
    if bot is None:
        return
    left_time = zzb_date - datetime.now()
    if left_time.days < -1:
        return

    all_groups = await bot.get_group_list()

    for group_id in all_groups:
        gid = group_id.get("group_id")
        if await get_key(f"auto_zzb_{gid}") == "on":
            try:
                await bot.set_group_card(
                    group_id=gid,
                    user_id=int(bot.self_id),
                    card=f"bot-dls {datetime.now().year % 2000}转本:{left_time.days + 1}天"
                )
            except:
                pass
