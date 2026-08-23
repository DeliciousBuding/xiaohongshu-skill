"""Python package for the Xiaohongshu Agent Skill."""

from importlib.metadata import PackageNotFoundError, version

from . import (
    comment,
    explore,
    feed,
    interact,
    login,
    publish,
    search,
    sop,
    strategy,
    templates,
    user,
)
from .client import DEFAULT_COOKIE_PATH, XiaohongshuClient, create_client

try:
    __version__ = version("xiaohongshu-skill")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "DEFAULT_COOKIE_PATH",
    "XiaohongshuClient",
    "comment",
    "create_client",
    "explore",
    "feed",
    "interact",
    "login",
    "publish",
    "search",
    "sop",
    "strategy",
    "templates",
    "user",
]
