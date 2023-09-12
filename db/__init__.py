from typing import Optional, List

from gino import Gino
from nonebot import logger
from sqlalchemy import Column, String

db = Gino()


class Key(db.Model):
    __tablename__ = "keys"

    key: str = Column(String, primary_key=True)
    value: str = Column(String)

    def __str__(self) -> str:
        return f"{self.key}:{self.value}"


async def get_key(key: str) -> Optional[str]:
    _key: Optional[Key] = await Key.get(key)
    if _key is None:
        return None
    else:
        return _key.value


async def all_keys() -> List[str]:
    keys = await Key.query.gino.all()
    return [i.key for i in keys]


async def set_key(key: str, value: str) -> bool:
    try:
        _key: Optional[Key] = await Key.get(key)
        if _key is None:
            await Key.create(key=key, value=value)
            return True
        else:
            await _key.update(value=value).apply()
            return True
    except Exception as e:
        logger.error(e)
        return False


async def link_db():
    logger.info("连接数据库")
    await db.set_bind("postgres://114514")
    await db.gino.create_all()


async def close_db():
    logger.info("断开数据库")
    await db.gino.create_all()
    await db.pop_bind().close()


if __name__ == '__main__':
    import asyncio


    async def test():
        await link_db()
        print(await get_key("宿舍打扫"))

        await close_db()


    loop = asyncio.run(test())
