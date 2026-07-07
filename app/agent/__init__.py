# Day15 — Agent 包入口

__all__ = ["run_agent"]


def __getattr__(name: str):
    if name == "run_agent":
        from app.agent.executor import run_agent

        return run_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
