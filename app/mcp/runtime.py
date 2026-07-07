# Day18 — MCP 专用后台事件循环
#
# MCP stdio Client 必须在固定事件循环上 connect/call；
# sync Agent 路由通过 run_on_background 跨线程调度，避免死锁。

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any, TypeVar

T = TypeVar("T")

_loop: asyncio.AbstractEventLoop | None = None
_thread: threading.Thread | None = None
_started = threading.Event()


def _loop_thread_main(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    _started.set()
    loop.run_forever()


def get_background_loop() -> asyncio.AbstractEventLoop:
    global _loop, _thread
    if _loop and _loop.is_running():
        return _loop
    loop = asyncio.new_event_loop()
    thread = threading.Thread(
        target=_loop_thread_main,
        args=(loop,),
        name="mcp-loop",
        daemon=True,
    )
    _started.clear()
    thread.start()
    if not _started.wait(timeout=10):
        raise RuntimeError("MCP 后台事件循环启动超时")
    _loop = loop
    _thread = thread
    return loop


def run_on_background(coro: Coroutine[Any, Any, T], timeout: float = 120) -> T:
    loop = get_background_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=timeout)


def stop_background_loop() -> None:
    global _loop, _thread
    if _loop and _loop.is_running():
        _loop.call_soon_threadsafe(_loop.stop)
    if _thread:
        _thread.join(timeout=5)
    _loop = None
    _thread = None
