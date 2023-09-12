from base64 import b64encode
from typing import Annotated

from fastapi import FastAPI
from nonebot import on_command, get_app
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.internal.params import ArgPlainText
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from api import split, to_pic
from .auto_xfb import *
from .dfjl_tool import get_record_pic_bytes
from .func import check_room, check_pay_money, check_pay_room, check_power_list, check_power, get_record_app
from .getInfo import yue
from .moneyTool import pay_money
from .payElect import pay as pay_elect
from .tool import *

power = on_command(
    "查电费",
    aliases={"查电费", "cdf"}
)

pay = on_command(
    "充电费",
    aliases={
        "充电费"
    }, permission=SUPERUSER
)

c_yue = on_command(
    "查余额", permission=SUPERUSER
)

chong_yue = on_command(
    "充余额", permission=SUPERUSER
)

power_list = on_command(
    "dfjl",
    aliases={"电费记录"}
)

power_chart = on_command(
    "dfb",
    aliases={"电费表"}
)

__plugin_name__ = "查电费"

app: FastAPI = get_app()


@app.get("/xfb/dfb/{room}")
async def get_record_pic_app(room: int) -> str:
    pic = await get_record_pic_bytes(str(room))
    if pic is None:
        return ""
    try:
        return b64encode(pic).decode()
    except:
        return ""


app.get("/xfb/cdf/{room}")(get_record_app)


@power.handle()
async def _(matcher: Matcher, args: Annotated[Message, CommandArg()]):
    if len(args) != 0:
        matcher.set_arg("room", args)


@power.got("room", prompt="请输入房间号:")
async def get_room(matcher: Matcher, args: Annotated[str, ArgPlainText("room")]):
    await check_power(matcher, args)


@power_list.handle()
async def _(matcher: Matcher, args: Annotated[Message, CommandArg()]):
    if len(args) != 0:
        matcher.set_arg("room", args)
        # await check_power(matcher, args.extract_plain_text())


@power_list.got("room", prompt="请输入房间号:")
async def get_room(matcher: Matcher, args: Annotated[str, ArgPlainText("room")]):
    await check_power_list(matcher, args)


@power_chart.handle()
async def _(matcher: Matcher, args: Annotated[Message, CommandArg()]):
    if len(args) != 0:
        matcher.set_arg("room", args)
        # await check_power(matcher, args.extract_plain_text())


@power_chart.got("room", prompt="请输入房间号:")
async def get_room(matcher: Matcher, room: Annotated[str, ArgPlainText("room")]):
    data = await get_record_pic_bytes(room)
    if data:
        await matcher.send(
            MessageSegment.image(
                data
            )
        )
    else:
        await matcher.send(f"该房间的电费记录过少:{room}", at_sender=True)


@c_yue.handle()
async def c_yue_handle():
    await c_yue.send(f'查询结果 -> \n{await yue("11451")}', at_sender=True)


@chong_yue.handle()
async def chong_yue_handle(args: Annotated[Message, CommandArg()]):
    if args.extract_plain_text() == "":
        await chong_yue.finish("未输入金额,取消", at_sender=True)

    try:
        _money = int(float(args.extract_plain_text()) * 100)
        raw_money = await yue("11451")
        _res = await pay_money(_money)
        logger.debug(_res)
        now_money = await yue("11451")
        await chong_yue.send(to_pic(
            f"充余额:{_money / 100}",
            f"原余额:\n\n{raw_money}\n\n"
            f"结果:{_res}\n\n"
            f"现余额:\n\n{now_money}"
        ))
    except Exception as e:
        await chong_yue.finish(f"余额解析失败,输入值:{args.extract_plain_text()}", at_sender=True)


@pay.handle()
async def pay_handle(matcher: Matcher, args: Annotated[Message, CommandArg()]):
    _money = 0.00
    room = ""
    args = split(args.extract_plain_text())
    for i in args:
        try:
            _money = check_pay_money(i)
            continue
        except ValueError:
            pass
        try:
            room = check_pay_room(i)
            continue
        except ValueError:
            pass

    if room == "":
        await matcher.finish(f"请输入正确的房间号,你的输入:{' '.join(args)}", at_sender=True)
        return
    if _money == 0:
        await matcher.finish(f"请输入正确的金额(大于0.01,小于50),你的输入:{' '.join(args)}", at_sender=True)
        return
    matcher.set_arg("room", Message(str(room)))
    matcher.set_arg("money", Message(str(_money)))
    await matcher.send(
        f"即将给 {room} 充值 {_money} 元电费,确定吗?\n确定回复:确定, 其余回复为取消充电费",
        at_sender=True
    )


@pay.got("confirm")
async def pay_handle(matcher: Matcher, args: Annotated[str, ArgPlainText("confirm")]):
    if args == "确定":
        room = matcher.get_arg("room").extract_plain_text()
        money = float(matcher.get_arg("money").extract_plain_text())
        try:
            await matcher.send(f"充值结果 -> {await pay_elect(room, money)}", at_sender=True)
        except Exception as e:
            await matcher.send(f"充值报错 -> {e}", at_sender=True)
            raise e
    else:
        await matcher.send("已取消", at_sender=True)
