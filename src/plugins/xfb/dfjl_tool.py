import json
from datetime import datetime
from pathlib import Path
from typing import List, Any, Optional

import jinja2
from sqlalchemy import desc

from nonebot import require

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import html_to_pic

from .tool import Power

dir_path = Path(__file__).parent
template_path = dir_path / "template"
js_path = template_path / "echarts.min.js"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def get_record_pic_bytes(room: str) -> Optional[bytes]:
    elects: List[Power] = await Power.query.where(Power.room == room).order_by(desc(Power.time)).limit(11).gino.all()
    elects = elects[::-1]
    if len(elects) < 2:
        return None
    try:
        cost: List[Any] = [
            -round(float(elects[i - 1].power) - float(elects[i].power), 2) for i in range(1, len(elects))
        ]
    except:
        cost = [0 for i in elects[:-1]]

    hour = datetime.now().hour
    info = {
        "power": json.dumps([i.power for i in elects[1:]]),
        "cost": json.dumps(cost),
        "style": json.dumps('dark' if hour > 18 or hour < 6 else None),
        "time": json.dumps([i.time.strftime("%m/%d\n%H:%M") for i in elects[1:]]),
        "room": str(room),
        "echarts": str(js_path.absolute())
    }
    template = env.get_template("show.html")
    content = await template.render_async(**info)
    return await html_to_pic(
        content, wait=0, device_scale_factor=1.5, viewport={
            "width": 750,
            "height": 415
        }
    )
