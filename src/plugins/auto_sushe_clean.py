# from nonebot import require, get_bot, on_command
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
#
# from datetime import datetime
#
# from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, MessageEvent
# from nonebot.internal.matcher import Matcher
#
# from db import get_key
#
# have_clean = on_command("打扫了", aliases={"打扫过了", "已经打扫", "扫了", "已打扫"})
#
# scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler
#
# member = {
#     0: 114514,
#     1: 114514,
#     2: 114514,
#     3: 114514,
#     4: 114514,
#     5: 114514,
#     6: 114514
# }
#
# today_clean = False
#
#
# @have_clean.handle()
# async def have_clean_handle(matcher: Matcher, event: MessageEvent):
#     if isinstance(event, GroupMessageEvent):
#         if event.group_id != 114514:
#             return
#     global today_clean
#     now = datetime.now()
#     if event.user_id != member[now.weekday()]:
#         if isinstance(event, GroupMessageEvent):
#             await matcher.finish("今天好像不是你打扫, 应该是：" + MessageSegment.at(member[now.weekday()]))
#         else:
#             await matcher.finish("今天好像不是你打扫, 应该是：" + str(member[now.weekday()]))
#     today_clean = True
#     await matcher.finish("已标记打扫，今天不再推送", at_sender=True)
#
#
# @scheduler.scheduled_job('cron', day="*", hour=1, timezone='Asia/Shanghai')
# @scheduler.scheduled_job('cron', day="*", hour=23, timezone='Asia/Shanghai')
# async def _1():
#     global today_clean
#     today_clean = False
#
#
# @scheduler.scheduled_job('cron', day="*", hour=17, minute=1, name="宿舍打扫17", timezone='Asia/Shanghai')
# @scheduler.scheduled_job('cron', day="*", hour=20, minute=1, name="宿舍打扫20", timezone='Asia/Shanghai')
# @scheduler.scheduled_job('cron', day="*", hour=22, minute=1, name="宿舍打扫22", timezone='Asia/Shanghai')
# async def su_she_clean():
#     now = datetime.now()
#     if_auto_su_she_clean = await get_key("宿舍打扫")
#     if today_clean or if_auto_su_she_clean == "0" or if_auto_su_she_clean is None:
#         return
#
#     bot: Bot = get_bot()
#
#     if bot is None:
#         return
#
#     msg = Message()
#     msg.append(f"今天星期{now.weekday() + 1}\n")
#     msg.append(MessageSegment.at(member[now.weekday()]))
#     msg.append(
#         f"今天打扫了吗?\n"
#         f"打扫了可发送:打扫过了\n"
#         f"发送后今天不会推送"
#     )
#     await bot.send_group_msg(group_id=114514, message=msg)
