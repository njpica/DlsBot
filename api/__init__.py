from datetime import datetime, timedelta
from typing import List

from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.internal.params import Depends

from .pic import Txt2Img, to_pic, to_img


def split(txt, split_by=(" ", ",")) -> List[str]:
    _temp = ""
    _res = []
    
    for _i in str(txt):
        if _i in split_by:
            if _temp == "":
                continue
            else:
                _res.append(_temp)
                _temp = ""
        else:
            _temp += _i
    if _temp != "":
        _res.append(_temp)
    return _res


def get_args(message: Message):
    return split(" ".join([str(i) for i in message if i.is_text()]))


def next_day(day: int):
    return (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d %H:%M')


def next_minutes(minutes: int):
    return (datetime.now() + timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M')


def ArgList(*args, **kwargs):
    async def _(event: MessageEvent):
        return split(str(event.message), *args, **kwargs)
    
    return Depends(_)
