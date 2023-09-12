# import os
# from datetime import date, datetime
#
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from nonebot import require, get_bot, on_command
# from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, MessageEvent
# from nonebot.internal.matcher import Matcher
# from nonebot.permission import SUPERUSER
#
# from db import get_key
#
# local = os.path.dirname(__file__)
#
# test = on_command("核酸测试", permission=SUPERUSER)
#
#
# # 获取当前目录下的文件地址
# def get_file_path(name: str) -> str:
#     return os.path.join(local, name)
#
#
# # ppp = on_command("pic")
# #
# # @ppp.handle()
# # async def ____(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
# #
# #     await matcher.send(get_file_path(f"{args.extract_plain_text()}.png"))
# #     await matcher.send(MessageSegment.image(file="file:///"+get_file_path(f"{args.extract_plain_text()}.png")))
# #     print(get_file_path(f"{args.extract_plain_text()}.png"))
# #
# scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler
#
# pic_split_num = 3
#
#
# @scheduler.scheduled_job('cron', day="*", hour=16, minute=40, name="明天核酸提醒", timezone='Asia/Shanghai')
# async def _16():
#     bot: Bot = get_bot()
#     _date, pic = (await get_key("hesuan")).split("/")
#     _date = date(*map(int, _date.split("-")))
#     pic = int(pic)
#
#     today = pic_split_num if (_t := (((datetime.now().date() - _date).days + pic) % pic_split_num)) == 0 else _t
#
#     tomorrow = (today + 1) % pic_split_num
#
#     tomorrow = pic_split_num if tomorrow==0 else tomorrow
#
#
#     group = int(await get_key("hesuan_group"))
#
#     # if tomorrow == 0:
#     #     pass
#     #     # await bot.send_group_msg(
#     #     #     group_id=group,
#     #     #     message=Message("掐指一算，明天好像没有要做核酸的...")
#     #     # )
#     # else:
#     await bot.send_group_msg(
#         group_id=group,
#         message=Message(
#             MessageSegment.image(file="file:///" + get_file_path(f"{tomorrow}.png")) +
#             MessageSegment.text("以上同学明天做核酸!")
#         )
#     )
#
#
# @scheduler.scheduled_job('cron', day="*", hour=12, minute=5, name="核酸截图提醒", timezone='Asia/Shanghai')
# async def _12():
#     bot: Bot = get_bot()
#     _date, pic = (await get_key("hesuan")).split("/")
#     _date = date(*map(int, _date.split("-")))
#     pic = int(pic)
#
#     today = pic_split_num if (_t := (((datetime.now().date() - _date).days + pic) % pic_split_num)) == 0 else _t
#
#     show_he_suan = today - 1
#
#     show_he_suan = pic_split_num if show_he_suan == 0 else show_he_suan
#
#     group = int(await get_key("hesuan_group"))
#
#     # if show_he_suan == 0:
#     #     pass
#     #     # await bot.send_group_msg(
#     #     #     group_id=group,
#     #     #     message=Message("掐指一算，今天好像没有要交核酸截图的..")
#     #     # )
#     # else:
#     await bot.send_group_msg(
#         group_id=group,
#         message=Message(
#             MessageSegment.image(file="file:///" + get_file_path(f"{show_he_suan}.png")) +
#             MessageSegment.text("以上同学请把核酸截图交给***")
#         )
#     )
#
#
# @scheduler.scheduled_job('cron', day="*", hour=8, minute=5, name="今天核酸提醒", timezone='Asia/Shanghai')
# async def _8():
#     bot: Bot = get_bot()
#     _date, pic = (await get_key("hesuan")).split("/")
#     _date = date(*map(int, _date.split("-")))
#     pic = int(pic)
#
#     today = pic_split_num if (_t := (((datetime.now().date() - _date).days + pic) % pic_split_num)) == 0 else _t
#
#     group = int(await get_key("hesuan_group"))
#
#     # if today == 0:
#     #     pass
#     #     # await bot.send_group_msg(
#     #     #     group_id=group,
#     #     #     message=Message("掐指一算，今天好像没有要交做核酸的..")
#     #     # )
#     # else:
#     await bot.send_group_msg(
#         group_id=group,
#         message=Message(
#             MessageSegment.image(file="file:///" + get_file_path(f"{today}.png")) +
#             MessageSegment.text("以上同学今天不要忘记做核酸")
#         )
#     )
#
#
# @test.handle()
# async def test_handle(matcher: Matcher, event: MessageEvent):
#     await _8()
#     await _12()
#     await _16()
#
#
# if __name__ == '__main__':
#     print(get_file_path(f"{2}.png"))
