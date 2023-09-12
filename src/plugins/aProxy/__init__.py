from fastapi import FastAPI
from nonebot import get_app

app: FastAPI = get_app()

keys = ["eya46_proxy_school"]


@app.post("/proxy_http")
async def get_proxy(data: dict):
    key = data.get("key")
    if not key:
        return {"success": -1, "msg": "缺少参数"}
    if key not in keys:
        return {"success": -2, "msg": "key错误"}
    # 119.91.216.131
    return {
        "success": 0,
        "data": {
            "http://": "http://eya46:eya46eya46@127.0.0.1:1145141919",
            "https://": "http://eya46:eya46eya46@127.0.0.1:1145141919"
        }
    }
