from urllib.parse import urlparse

import asyncio
from typing import Any, Union, Awaitable, Callable, List, Optional, Type, TypeVar
from warnings import warn


class MoreException(Exception):

    def __init__(self, *args: object, exceptions: Optional[List[Exception]] = None) -> None:
        if exceptions is None:
            raise Exception("MoreException必须要有错误")
        self.list = exceptions
        self.exceptions = self.list
        super().__init__(*args)

    def __str__(self) -> str:
        return "错误如下:\n" + "\n".join([f"{index}.{i.__class__}:{i}" for index, i in enumerate(self.exceptions)])

    def __repr__(self) -> str:
        raise Exception("MoreException未实现__repr__")


def retry(func: Callable, *args, times=2, sleepFunc: Callable = None, exceptions=None, **kwargs) -> Any:
    if exceptions is None:
        exceptions = []
    if times <= 0:
        raise Exception("retry x0")

    for i in range(0, times):
        try:
            if asyncio.iscoroutinefunction(func):
                raise Exception("retry不可retry异步函数")
            else:
                return func(*args, **kwargs)
        except Exception as e:
            exceptions.append(e)
            if sleepFunc is not None:
                sleepFunc()

    raise MoreException(exceptions=exceptions)


async def retry_async(func: Callable, *args, times=2, sleepFunc: Callable = None, exceptions=None, **kwargs) -> Any:
    if exceptions is None:
        exceptions = []
    if times <= 0:
        raise Exception("retry x0")

    for i in range(0, times):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                raise Exception("retry_sync不可retry同步函数")
        except Exception as e:
            exceptions.append(e)
            if sleepFunc is not None:
                await sleepFunc()

    raise MoreException(exceptions=exceptions)


def run_async(func: Callable, *args, **kwargs):
    # 判断是否为异步函数
    if asyncio.iscoroutinefunction(func):
        return asyncio.get_event_loop_policy().get_event_loop().run_until_complete(func(*args, **kwargs))
    else:
        raise Exception("执行非异步函数")


def no_ex(func_var: Union[Callable, Any], *args1, if_warn=True, **kwargs1) -> Union[Callable, Any]:
    def _wrap(_func: Callable, *args2, **kwargs2):
        try:
            if asyncio.iscoroutinefunction(_func):
                return run_async(_func, *args2, **kwargs2)
            else:
                return _func(*args2, **kwargs2)
        except Exception as e:
            if if_warn:
                warn(RuntimeWarning(f"函数<{_func.__name__}>出错了\n{e.__class__}: {e}"))
            return None if isinstance(func_var, Callable) else func_var

    if isinstance(func_var, Callable):
        return _wrap(func_var, *args1, **kwargs1)
    else:
        return _wrap


async def no_ex_async(func_var: Union[Callable, Any], *args1, if_warn=True, **kwargs1) -> Union[Callable, Any]:
    async def _wrap(_func: Callable, *args2, **kwargs2):
        try:
            if asyncio.iscoroutinefunction(_func):
                return await _func(*args2, **kwargs2)
            else:
                raise Exception("请使用非异步no_ex")
        except Exception as e:
            if if_warn:
                warn(RuntimeWarning(f"函数<{_func.__name__}>出错了\n{e.__class__}: {e}"))
            return None if isinstance(func_var, Callable) else func_var

    if isinstance(func_var, Callable):
        return await _wrap(func_var, *args1, **kwargs1)
    else:
        return _wrap


def url_to_proxy(url: str) -> str:
    _ = urlparse(url)
    return "http://{0}{1}{2}.atrust.njpi.edu.cn:443{3}{4}".format(
        _.hostname.replace(".", "-"),
        (f"-{_.port}-p" if _.port else ""),
        ("-s" if _.scheme == "https" else ""),
        (_.path if _.path else "/"),
        (f"?{_.query}" if _.query else "")
    )
