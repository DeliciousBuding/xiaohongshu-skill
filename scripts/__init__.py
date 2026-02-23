"""
xiaohongshu-skill

基于 xiaohongshu-mcp Go 源码翻译的 Python Playwright 实现
"""

from .client import XiaohongshuClient, create_client, DEFAULT_COOKIE_PATH
from . import login
from . import search
from . import feed
from . import user

__version__ = "1.0.0"
__all__ = [
    "XiaohongshuClient",
    "create_client",
    "DEFAULT_COOKIE_PATH",
    "login",
    "search",
    "feed",
    "user",
]
