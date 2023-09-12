from random import randint

from nonebot import on_fullmatch, require
from nonebot.adapters.onebot.v11 import MessageEvent

from db import get_key

cyq = on_fullmatch(("每日运气", "今日运气"), priority=99)

scheduler = require("nonebot_plugin_apscheduler").scheduler

cyq_data = {

}


@scheduler.scheduled_job("cron", hour=0, minute=0)
async def reset_cyq_data():
    global cyq_data
    cyq_data = dict()


@cyq.handle()
async def cyq_handle(event: MessageEvent):
    global cyq_data
    if (
            (fake_yunqi := await get_key(f"fake_yunqi_{event.user_id}")) is not None and
            fake_yunqi.isdigit() and (cyq_data.get(event.user_id) is None or cyq_data[event.user_id] < int(fake_yunqi))
    ):
        cyq_data[event.user_id] = randint(int(fake_yunqi), max(100, int(fake_yunqi)))

    if event.user_id in cyq_data:
        await cyq.finish(f"今日运气已查询，运气值：{cyq_data[event.user_id]}%", at_sender=True)
    else:
        cyq_data[event.user_id] = randint(0, 100)
        await cyq.finish(f"今日运气值：{cyq_data[event.user_id]}%", at_sender=True)
