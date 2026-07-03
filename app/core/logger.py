# Day08 — 日志模块（项目重构时引入）
#
# 功能：统一日志格式，供 upload 等模块记录运行信息
# 逻辑：basicConfig 配置一次，导出全局 logger 实例

import logging


def setup_logger(name: str = "ai-project-assistant") -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return logging.getLogger(name)


logger = setup_logger()
