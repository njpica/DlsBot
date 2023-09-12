from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.internal.matcher import Matcher

from api import Txt2Img, split
from .tool import getElectRecord, saveElectRecord, getElect


def check_room(room):
    if len(arg := split(room)) != 0:
        if int(arg[0]) > 99999 or int(arg[0]) < 1000:
            raise ValueError
        return str(int(arg[0]))
    else:
        raise ValueError


def check_pay_room(room):
    room = int(str(room))
    if room > 99999 or room < 1000:
        raise ValueError
    return room


def check_pay_money(money):
    money = float(str(money))
    if money < 0.01 or money > 50:
        raise ValueError
    return money


async def check_power_list(matcher: Matcher, args: str):
    try:
        room = check_room(args)
    except ValueError:
        await matcher.send("房间号错误")
        return
    to_img = Txt2Img()
    records = await getElectRecord(room)
    if records is None:
        await matcher.finish(f"没有该房间的电费记录:{room}", at_sender=True)
    pic = to_img.save(f"电费记录-{room}", records)
    await matcher.send(MessageSegment.image(pic))


async def check_power(matcher: Matcher, args: str):
    try:
        room = check_room(args)
    except ValueError:
        await matcher.send("房间号错误", at_sender=True)
        return
    elect = await getElect(room)
    if elect is None or "超时" in elect or "报错" in elect or "关闭" in elect:
        await matcher.send(f'学付宝寄了 -> {elect}', at_sender=True)
    elif len(elect.split("电量")) < 2:
        await matcher.send(f'查询结果:\n{elect}', at_sender=True)
    else:
        extra_message = ""
        if len(elect.split("电量为")) < 2:
            try:
                if float(elect.split("电量")[1][:-1]) < 10:
                    extra_message = "\n听机器人一句劝，赶紧充电费"
            except:
                pass
            await matcher.send(f'查询结果:\n房间剩余电量为{elect.split("电量")[1]}{extra_message}', at_sender=True)
            await saveElectRecord(room, elect.split("电量")[1])
        else:
            try:
                if float(elect.split("电量为")[1][:-1]) < 10:
                    extra_message = "\n听机器人一句劝，赶紧充电费"
            except:
                pass
            await matcher.send(f'查询结果:\n房间剩余电量为{elect.split("电量为")[1]}{extra_message}', at_sender=True)
            await saveElectRecord(room, elect.split("电量为")[1])


async def get_record_app(room: Union[str, int]) -> dict:
    power = 0
    try:
        room = check_room(room)
        elect = await getElect(room)
        if elect is None or "超时" in elect or "报错" in elect or "关闭" in elect:
            res = f'学付宝寄了 -> {elect}'
        elif len(elect.split("电量")) < 2:
            res = f'查询结果:\n{elect}'
        else:
            extra_message = ""
            if len(elect.split("电量为")) < 2:
                try:
                    if float(elect.split("电量")[1][:-1]) < 10:
                        extra_message = "\n听机器人一句劝，赶紧充电费"
                except:
                    pass
                power = elect.split("电量")[1]

                res = f'查询结果:\n房间剩余电量为{elect.split("电量")[1]}{extra_message}'
            else:
                try:
                    if float(elect.split("电量为")[1][:-1]) < 10:
                        extra_message = "\n听机器人一句劝，赶紧充电费"
                except:
                    pass
                power = elect.split("电量为")[1]
                res = f'查询结果:\n房间剩余电量为{elect.split("电量为")[1]}{extra_message}'
            await saveElectRecord(room, power)
    except ValueError:
        res = "房间号错误"

    return {"data": res, "power": float(power[:-1]) if isinstance(power, str) else -99999}
