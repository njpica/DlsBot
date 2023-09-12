#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

from nonebot.log import logger, default_format

logger.add(
    "log/error.log",
    rotation="00:00",
    diagnose=False,
    level="ERROR",
    format=default_format
)

from db import link_db, close_db

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

driver.on_startup(link_db)
driver.on_shutdown(close_db)

nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("nonebot_plugin_htmlrender")
nonebot.load_plugins("src/plugins")

if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")
