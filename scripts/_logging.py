"""
日志工具模块

为 CLI 工具提供统一的日志接口。默认 WARNING 级别，
通过 --verbose 提升到 DEBUG，--quiet 降低到 ERROR。
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    获取命名的 logger 实例。

    首次调用时自动配置 handler：输出到 stderr，
    格式为 "[LEVEL] name: message"，默认级别 WARNING。
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            '[%(levelname)s] %(name)s: %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)  # 默认 WARNING，--verbose 改 DEBUG
    return logger
