from datetime import datetime
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Message, PrivateMessageEvent, GroupMessageEvent, MessageSegment, \
    Bot
from nonebot.adapters.onebot.v11.helpers import HandleCancellation
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from sqlalchemy import and_

from api import split, Txt2Img
from db import get_key
from .bean import AutoPower
from ..func import check_room, get_record_app
from ..tool import getLastRecord

scheduler: AsyncIOScheduler = require("nonebot_plugin_apscheduler").scheduler

dydf_test = on_command("测试订阅电费", block=True, permission=SUPERUSER)
dydf = on_command("订阅电费")
dydf_help = on_command("订阅电费帮助", aliases={"电费订阅帮助"}, priority=10, block=True)
dydf_list = on_command("电费订阅记录")
update_dydf = on_command("更新电费订阅")
change_dydf = on_command("修改电费订阅")
del_dydf = on_command("删除电费订阅")
open_dydf = on_command("开启电费订阅")
close_dydf = on_command("关闭电费订阅")

help_pic = None


@dydf_test.handle()
@scheduler.scheduled_job("interval", seconds=30, timezone='Asia/Shanghai', name="电费订阅~~~~")
async def auto_send_power():
    if await get_key("电费订阅") == "off":
        return

    now_time = datetime.now().time()

    if now_time.hour > 22 or now_time.hour < 6:
        return

    bot: Optional[Bot]
    try:
        bot = get_bot()
    except:
        bot = None

    now_time_int = now_time.hour * 60 * 60 + now_time.minute * 60 + now_time.second

    powers: List[AutoPower] = await AutoPower.query.where(and_(
        AutoPower.time >= now_time_int - 120,
        AutoPower.time <= now_time_int + 120,
        AutoPower.status == True,
        AutoPower.last_action_time <= datetime.now().date()
    )).gino.all()

    for power in powers:
        try:
            last_record = await getLastRecord(power.room)
            res = await get_record_app(power.room)
            elect = res.get("power")
            res = res.get("data")
        except:
            continue
        try:
            if elect > power.limit:
                continue
            difference = f"距{last_record.time.strftime('%m-%d %H:%M')}" \
                         f"相差{round(elect - float(last_record.power), 2)}度\n" if last_record and last_record != -99999 else ""
            if bot:
                if power.type == "group":
                    await bot.send_group_msg(
                        group_id=int(power.from_id),
                        message=f"房间号:{power.room}\n{difference}(如要修改请发送:订阅电费帮助)\n\n{res}"
                    )
                if power.type == "private":
                    await bot.send_private_msg(
                        user_id=int(power.from_id),
                        message=f"房间号:{power.room}\n{difference}(如要修改请发送:订阅电费帮助)\n\n{res}"
                    )
        except:
            continue
        finally:
            await power.update(
                times=power.times + 1, last_action_time=datetime.now()
            ).apply()


@dydf_help.handle()
async def dydf_help_handle(matcher: Matcher):
    global help_pic
    if help_pic is None:
        to_img = Txt2Img()
        help_pic = MessageSegment.image(to_img.save(
            "电费订阅帮助",
            "-----------------------------\n"
            "订阅电费，每天定时发送房间的电费，详细功能看下方\n"
            "-----------------------------\n"
            "0.订阅电费 -> 订阅电费 房间号\n"
            "   例:订阅电费 1234\n"
            "1.电费订阅记录 -> 电费订阅记录\n"
            "2.更新电费订阅 -> 更新电费订阅\n"
            "   (修改电费订阅提醒时间，设置为发消息的时间，精度±10s)\n"
            "3.修改电费订阅 -> 修改电费订阅\n"
            "   (修改限额，当电费高于该数就不发送信息)\n"
            "4.删除电费订阅 -> 删除电费订阅\n"
            "   （字面意思，是删除不是暂停)\n"
            "5.开启电费订阅 -> 开启电费订阅\n"
            "6.关闭电费订阅 -> 关闭电费订阅"
        ))
    await matcher.send(help_pic)


@dydf_list.handle()
async def dydf_list(matcher: Matcher, event: MessageEvent):
    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    powers = await AutoPower.query.where(and_(
        AutoPower.type == _type,
        AutoPower.from_id == from_id
    )).gino.all()

    if len(powers) == 0:
        await matcher.finish("无电费订阅记录", at_sender=True)

    tool = Txt2Img()
    pic_str = tool.save("订阅表", "\n\n".join([
        f"{index + 1}.房间号:{i.room} 状态:{'开启' if i.status else '关闭'}\n"
        f"  时间: {i.time // 3600}:{(i.time % 3600) // 60}:{(i.time % 3600) % 60} 次数:{i.times} 订阅者:{i.user_id}\n"
        f"  上次检查:{i.last_action_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"  限制:{i.limit}度(电费高于这个值不会提醒)" for index, i in enumerate(powers)
    ]))

    await matcher.send(MessageSegment.image(pic_str))


@open_dydf.handle()
async def open_dydf_handle(matcher: Matcher, args: Message = CommandArg()):
    if len(args) != 0:
        try:
            check_room(args.extract_plain_text())
            matcher.set_arg("room", args)
        except:
            await matcher.finish("房间号错误")


@open_dydf.got("room", "请输入房间号:")
async def open_dydf_got_room(matcher: Matcher, event: MessageEvent, room: str = ArgPlainText("room")):
    try:
        check_room(room)
    except:
        await matcher.finish("房间号错误")
    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()
        if event.sender.role not in ["owner", "admin"]:
            await matcher.finish("群聊仅限管理员开启!", at_sender=True)

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    if len(await AutoPower.query.where(and_(
            AutoPower.type == _type,
            AutoPower.room == room,
            AutoPower.from_id == from_id
    )).gino.all()) == 0:
        await matcher.finish(f"未订阅该房间:{room}", at_sender=True)

    try:
        await AutoPower.update.values(
            status=True
        ).where(and_(
            AutoPower.room == room,
            AutoPower.from_id == from_id,
            AutoPower.type == _type
        )).gino.status()
        await matcher.send(f"开启成功:{room}", at_sender=True)
    except Exception as e:
        await matcher.send(f"开启失败:{e}", at_sender=True)


@close_dydf.handle()
async def close_dydf_handle(matcher: Matcher, args: Message = CommandArg()):
    if len(args) != 0:
        try:
            check_room(args.extract_plain_text())
            matcher.set_arg("room", args)
        except:
            await matcher.finish("房间号错误")


@close_dydf.got("room", "请输入房间号:")
async def close_dydf_got_room(matcher: Matcher, event: MessageEvent, room: str = ArgPlainText("room")):
    try:
        check_room(room)
    except:
        await matcher.finish("房间号错误")
    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()
        if event.sender.role not in ["owner", "admin"]:
            await matcher.finish("群聊仅限管理员开启!", at_sender=True)

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    if len(await AutoPower.query.where(and_(
            AutoPower.type == _type,
            AutoPower.room == room,
            AutoPower.from_id == from_id
    )).gino.all()) == 0:
        await matcher.finish(f"未订阅该房间:{room}", at_sender=True)

    try:
        await AutoPower.update.values(
            status=False
        ).where(and_(
            AutoPower.room == room,
            AutoPower.from_id == from_id,
            AutoPower.type == _type
        )).gino.status()
        await matcher.send(f"关闭成功:{room}", at_sender=True)
    except Exception as e:
        await matcher.send(f"关闭失败:{e}", at_sender=True)


@change_dydf.handle()
async def change_dydf_handle(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    try:
        if isinstance(event, PrivateMessageEvent):
            _type = "private"
            from_id = event.get_user_id()
            user_id = event.get_user_id()
            if len((powers := await AutoPower.query.where(and_(
                    AutoPower.type == _type,
                    AutoPower.from_id == from_id,
                    AutoPower.user_id == user_id
            )).gino.all())) == 1:
                matcher.set_arg("room", Message(powers[0].room))
    except:
        pass

    for i in split(args.extract_plain_text()):
        try:
            matcher.set_arg("room", Message(check_room(i)))
        except:
            if i.isdigit():
                matcher.set_arg("power", Message(i))


@change_dydf.got("room", "请输入房间号:")
async def change_dydf_got_room(
        matcher: Matcher, room: str = ArgPlainText("room"), cancel=HandleCancellation("取消成功")
):
    try:
        matcher.set_arg("room", Message(check_room(room)))
    except:
        matcher.reject_arg("room", "房间号错误,请重新输入:")


@change_dydf.got("power", "请输入电费限制，整数:")
async def change_dydf_got_power(
        matcher: Matcher, event: MessageEvent, room: str = ArgPlainText("room"),
        power: str = ArgPlainText("power"), cancel=HandleCancellation("取消成功")
):
    if power.isdigit():
        power = int(power)
    else:
        matcher.reject_arg("power", prompt="电费非整数，请重新输入:")

    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()
        if event.sender.role not in ["owner", "admin"]:
            await matcher.finish("群聊仅限管理员删除订阅!", at_sender=True)

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    try:
        await AutoPower.update.values(
            limit=power
        ).where(and_(
            AutoPower.room == room,
            AutoPower.from_id == from_id,
            AutoPower.type == _type
        )).gino.status()
        await matcher.send(f"更新成功:{room},{power}度", at_sender=True)
    except Exception as e:
        await matcher.send(f"更新成功失败:{e}", at_sender=True)


@del_dydf.handle()
async def del_dydf_handle(matcher: Matcher, args: Message = CommandArg()):
    if len(args) != 0:
        try:
            check_room(args.extract_plain_text())
            matcher.set_arg("room", args)
        except:
            await matcher.finish("房间号错误!")


@del_dydf.got("room", "请输入房间号:")
async def del_dydf_got_room(matcher: Matcher, event: MessageEvent, room: str = ArgPlainText("room")):
    try:
        check_room(room)
    except:
        await matcher.finish("房间号错误")

    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()
        if event.sender.role not in ["owner", "admin"]:
            await matcher.finish("群聊仅限管理员删除订阅!", at_sender=True)

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    try:
        length = await AutoPower.delete.where(and_(
            AutoPower.type == _type,
            AutoPower.from_id == from_id,
            AutoPower.room == room
        )).gino.status()
        if isinstance(length, int) and length > 0:
            await matcher.send("删除成功!", at_sender=True)
        else:
            await matcher.send(f"没有该房间号:{room}!", at_sender=True)
    except:
        await matcher.send("删除失败!", at_sender=True)


@update_dydf.handle()
async def update_dydf_handle(matcher: Matcher, event: MessageEvent):
    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()
        if event.sender.role not in ["owner", "admin"]:
            await matcher.finish("群聊仅限管理员更新订阅!", at_sender=True)

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    powers = await AutoPower.query.where(and_(
        AutoPower.type == _type,
        AutoPower.from_id == from_id
    )).gino.all()

    if _type == "group":
        if len(powers) == 1:
            matcher.set_arg("room", Message(powers[0].room))
        elif len(powers) > 0:
            await matcher.send("房间号超过一个，请输入要更新的房间号:", at_sender=True)
        elif len(powers) == 0:
            await matcher.finish("未订阅电费，无法更新", at_sender=True)
    else:
        if len(powers) == 0:
            await matcher.finish("无订阅电费，无法更新", at_sender=True)
        elif len(powers) > 1:
            await matcher.finish("订阅数超过一个，请先删除", at_sender=True)
        else:
            matcher.set_arg("room", Message(powers[0].room))


@update_dydf.got("room")
async def update_dydf_got_room(matcher: Matcher, event: MessageEvent, room: str = ArgPlainText("room")):
    try:
        check_room(room)
    except:
        await matcher.finish("房间号错误!")

    _type = None
    from_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)

    now_time = datetime.now().time()

    if now_time.hour > 22 or now_time.hour < 6:
        await matcher.finish(f"不允许该时间段更新订阅:{now_time.hour}", at_sender=True)

    now_time_int = now_time.hour * 60 * 60 + now_time.minute * 60 + now_time.second

    try:
        await AutoPower.update.values(
            time=now_time_int
        ).where(and_(
            AutoPower.room == room,
            AutoPower.from_id == from_id,
            AutoPower.type == _type
        )).gino.status()
        await matcher.send("更新订阅成功", at_sender=True)
    except:
        await matcher.send("更新订阅失败", at_sender=True)


@dydf.handle()
async def dydf_handle(matcher: Matcher, args: Message = CommandArg()):
    if len(args) != 0:
        try:
            check_room(args.extract_plain_text())
            matcher.set_arg("room", args)
        except:
            await matcher.finish("房间号错误")


@dydf.got("room", prompt="请输入房间号:")
async def dydf_got_room(matcher: Matcher, event: MessageEvent, room: str = ArgPlainText("room")):
    try:
        check_room(room)
    except:
        await matcher.finish("房间号错误")

    _type = None
    from_id = None
    user_id = None
    if isinstance(event, PrivateMessageEvent):
        _type = "private"
        from_id = event.get_user_id()
        user_id = event.get_user_id()
    if isinstance(event, GroupMessageEvent):
        _type = "group"
        from_id = str(event.group_id)
        user_id = event.get_user_id()
        if event.sender.role not in ["owner", "admin"]:
            await matcher.finish("群聊仅限管理员订阅!", at_sender=True)

    if not (_type and from_id and user_id):
        await matcher.finish("未知订阅来源", at_sender=True)

    if _type not in ["group", "private"]:
        await matcher.finish("不支持的订阅来源", at_sender=True)

    now_time = datetime.now().time()

    if now_time.hour > 22 or now_time.hour < 6:
        await matcher.finish(f"不允许该时间段订阅:{now_time.hour}", at_sender=True)

    now_time_int = now_time.hour * 60 * 60 + now_time.minute * 60 + now_time.second

    if len(await AutoPower.query.where(and_(
            AutoPower.type == _type,
            AutoPower.room == room,
            AutoPower.from_id == from_id
    )).gino.all()) > 0:
        await matcher.finish(f"已订阅该房间电费:{room}", at_sender=True)

    powers = await AutoPower.query.where(and_(
        AutoPower.type == _type,
        AutoPower.from_id == from_id
    )).gino.all()
    if _type == "group":
        if len(powers) >= 3:
            await matcher.finish(f"订阅房间不能超过3个:{','.join([i.room for i in powers])}", at_sender=True)
    elif _type == "private":
        if len(powers) > 0:
            await matcher.finish(f"私聊只能订阅一个宿舍", at_sender=True)

    try:
        await AutoPower.create(
            room=room, type=_type, from_id=from_id, user_id=user_id, time=now_time_int,
            last_action_time=datetime(year=1999, day=1, month=1)
        )
        await matcher.send(f"订阅成功:{room}", at_sender=True)
    except Exception as e:
        await matcher.send(f"订阅失败:{room}\n{e}", at_sender=True)


__all__ = []
