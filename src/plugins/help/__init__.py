from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment

from api import Txt2Img

help_help = on_command(
    "菜单",
    aliases={
        "功能",
        "查看菜单",
        "查看功能"
    }
)

pic = None


@help_help.handle()
async def _sun_un_bind():
    global pic

    if pic is None:
        helps = [
            "订阅电费(单独的菜单，请发送:) -> 电费订阅帮助\n"
            "查电费 -> 查电费 1234\n"
            "电费记录 -> 电费记录 1234\n"
            "电费表 -> 电费表 1234\n"
            "看世界 -> 看世界(60s看世界)\n"
            "B站热搜 -> b23/b站热搜\n"
            "今日运气\n"
        ]
        pic = MessageSegment.image(Txt2Img().save(
            "菜单",
            "\n".join([f"{index + 1}.{i}" for index, i in enumerate(helps)]) +
            "\n管理员功能:\n" +
            '\n'.join([
                "key [name] [value] -> 设置key\n",
                "key [name] -> 获取key\n",
                "keys -> 获取所有key\n",
                " auto_sign_[group_id] -> 自动签到\n",
                " auto_zzb_[group_id] -> 自动改转转本时间\n",
                " fake_yunqi_[user_id] -> fake今日运气\n"
                " ban_group on/off -> 禁言群\n",
                " ban_private on/off -> 禁言私聊\n",
                " ban_type white/black -> 白名单/黑名单\n",
                " allow_group_[group_id] on/off -> 白名单群\n",
                " ban_group_[group_id] on/off -> 黑名单群\n",
            ])
        ))

    await help_help.send(pic)
