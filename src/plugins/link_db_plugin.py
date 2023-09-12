from nonebot import on_command
from nonebot.permission import SUPERUSER

from db import link_db

link_db_command = on_command("连接数据库", permission=SUPERUSER)


@link_db_command.handle()
async def link_db_handler():
    await link_db()
    await link_db_command.finish("连接数据库成功")
