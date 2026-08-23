"""
小红书登录模块

基于 xiaohongshu-mcp/login.go 翻译
支持生成微信登录二维码，保存供主模型发送
"""

import base64
import os
import sys
import time
from typing import Any, Dict, Optional, Tuple

from .client import DEFAULT_COOKIE_PATH, XiaohongshuClient
from .profiles import env_profile, profile_paths
from .selectors import (
    LOGIN_CREATOR_READY_CONTRACT,
    LOGIN_PROFILE_LINK_CONTRACT,
    LOGIN_QRCODE_CONTRACT,
)

# QRCode 图片保存目录 - 放在 skill 文件夹内
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QRCODE_DIR = os.path.join(SKILL_DIR, "data")
QRCODE_PATH = os.path.join(QRCODE_DIR, "qrcode.png")

# Creator Center login and publish detection.
CREATOR_PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish?source=official"
CREATOR_AUTH_URL_MARKERS = ("/login", "/captcha", "verify")
MAIN_PROFILE_SELECTOR = LOGIN_PROFILE_LINK_CONTRACT.primary


class LoginAction:
    """登录动作"""

    QRCODE_SELECTOR = LOGIN_QRCODE_CONTRACT.primary
    PROFILE_LINK_SELECTOR = LOGIN_PROFILE_LINK_CONTRACT.primary
    CREATOR_READY_SELECTORS = LOGIN_CREATOR_READY_CONTRACT.selectors

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def check_login_status(self, navigate: bool = True) -> Tuple[bool, Optional[str]]:
        """Return whether the account is logged in from live page state."""
        page = self.client.page

        if navigate:
            self.client.navigate("https://www.xiaohongshu.com/explore")
            time.sleep(3)

        # QR modal visible -> logged out
        qr = page.locator(self.QRCODE_SELECTOR)
        if qr.count() > 0 and qr.first.is_visible():
            return False, None

        # Sidebar profile link visible -> logged in
        profile_link = page.locator(self.PROFILE_LINK_SELECTOR)
        if profile_link.count() > 0 and profile_link.first.is_visible():
            return True, "已登录用户"

        return False, None

    def check_creator_login_status(self, navigate: bool = True) -> bool:
        """Return whether the Creator Center shows an authenticated page."""
        if navigate:
            self.client.navigate(CREATOR_PUBLISH_URL)
            time.sleep(3)

        if self._is_creator_auth_page():
            return False

        if self._any_creator_ready_visible():
            return True

        url = (self.client.page.url or "").lower()
        return url.startswith("https://creator.xiaohongshu.com")

    def _is_creator_auth_page(self) -> bool:
        """Return True when still on the Creator Center login or captcha page."""
        url = (self.client.page.url or "").lower()
        return any(marker in url for marker in CREATOR_AUTH_URL_MARKERS)

    def _any_creator_ready_visible(self) -> bool:
        """Return True when any Creator Center ready candidate is visible."""
        page = self.client.page
        for selector in self.CREATOR_READY_SELECTORS:
            try:
                loc = page.locator(selector)
                if loc.count() > 0 and loc.first.is_visible():
                    return True
            except Exception:
                continue
        return False

    def wait_for_creator_login(self, timeout: int = 240) -> bool:
        """Wait for the user to complete Creator Center login in a browser."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.check_creator_login_status(navigate=False):
                self.client._save_cookies()
                return True
            time.sleep(2)
        return False

    def get_wechat_qrcode(self) -> Tuple[Optional[str], bool]:
        """
        获取微信登录二维码

        流程：
        1. 访问小红书首页触发登录弹窗
        2. 获取弹窗中的微信二维码图片
        3. 保存到文件

        Returns:
            (二维码文件路径, 是否已登录)
        """
        client = self.client
        page = client.page

        # 访问首页触发登录弹窗
        client.navigate("https://www.xiaohongshu.com/explore")
        time.sleep(4)  # 给弹窗足够时间渲染

        # 先检查是否已登录（不要重新 navigate）
        is_logged_in, _ = self.check_login_status(navigate=False)
        if is_logged_in:
            return None, True

        # 尝试获取二维码 base64 图片
        qrcode_src = None
        for attempt in range(5):
            try:
                qr = page.locator(self.QRCODE_SELECTOR)
                if qr.count() > 0:
                    src = qr.first.get_attribute('src')
                    if src and len(src) > 200:  # 有效 base64 至少上百字符
                        qrcode_src = src
                        break
            except Exception:
                pass
            time.sleep(1)

        if qrcode_src:
            # 去掉 data:image/png;base64, 前缀
            if ',' in qrcode_src:
                qrcode_src = qrcode_src.split(',', 1)[1]

            # 保存二维码图片
            img_data = base64.b64decode(qrcode_src)
            os.makedirs(QRCODE_DIR, exist_ok=True)
            with open(QRCODE_PATH, 'wb') as f:
                f.write(img_data)

            print(f"二维码已保存到: {QRCODE_PATH}", file=sys.stderr)
            return QRCODE_PATH, False

        # 后备：整页截屏
        print("未找到有效的二维码图片，截屏保存...", file=sys.stderr)
        os.makedirs(QRCODE_DIR, exist_ok=True)
        page.screenshot(path=QRCODE_PATH)
        return QRCODE_PATH, False

    def wait_for_login(self, timeout: int = 120, min_wait: int = 30) -> bool:
        """
        在 **当前页面** 上等待用户扫码登录。
        不会重新 navigate，以免刷新掉二维码弹窗。

        会强制等待至少 min_wait 秒再开始检测，
        给用户足够时间在手机上确认登录。

        Args:
            timeout: 总超时时间（秒）
            min_wait: 最少等待秒数（默认 30）

        Returns:
            是否登录成功
        """
        start = time.time()

        # ---- 阶段 1: 强制等待 min_wait 秒 ----
        print(f"请在手机上扫码并确认登录（至少等待 {min_wait} 秒）...", file=sys.stderr)
        while time.time() - start < min_wait:
            elapsed = int(time.time() - start)
            remaining = min_wait - elapsed
            if remaining > 0 and remaining % 10 == 0:
                print(f"  等待中... 还剩 {remaining} 秒", file=sys.stderr)
            time.sleep(2)

        # ---- 阶段 2: 开始轮询页面认证状态 ----
        print("开始检测登录状态...", file=sys.stderr)
        while time.time() - start < timeout:
            is_logged_in, _ = self.check_login_status(navigate=False)
            if is_logged_in:
                print("检测到主站已登录！", file=sys.stderr)
                time.sleep(5)
                self.client._save_cookies()
                return True

            elapsed = int(time.time() - start)
            remaining = timeout - elapsed
            if remaining > 0 and remaining % 15 == 0:
                print(f"  仍在等待登录... 剩余 {remaining} 秒", file=sys.stderr)
            time.sleep(3)

        print("登录超时", file=sys.stderr)
        return False


# ====== 顶层便捷函数 ======

def check_login(
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Tuple[bool, Optional[str]]:
    """检查登录状态"""
    client = XiaohongshuClient(headless=True, cookie_path=cookie_path)
    try:
        client.start()
        action = LoginAction(client)
        return action.check_login_status(navigate=True)
    finally:
        client.close()


def check_creator_login(
    cookie_path: str = DEFAULT_COOKIE_PATH,
    headless: bool = True,
) -> bool:
    """Return whether the Creator Center is logged in."""
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        return LoginAction(client).check_creator_login_status(navigate=True)
    finally:
        client.close()


def creator_login(
    headless: bool = False,
    cookie_path: str = DEFAULT_COOKIE_PATH,
    timeout: int = 240,
) -> Dict[str, Any]:
    """Open the Creator Center and wait for phone-number login."""
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = LoginAction(client)
        if action.check_creator_login_status(navigate=True):
            return {"status": "logged_in", "message": "创作者中心已登录"}
        if headless:
            return {"status": "login_required", "message": "创作者中心需要可见浏览器登录，请使用 --headless=false"}
        if action.wait_for_creator_login(timeout=timeout):
            return {"status": "logged_in", "message": "创作者中心登录成功"}
        return {"status": "timeout", "message": "创作者中心登录超时"}
    finally:
        client.close()


def login(
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    登录小红书（生成二维码 + 等待扫码）

    Returns:
        登录结果字典
    """
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = LoginAction(client)

        # 获取二维码
        qrcode_path, is_logged_in = action.get_wechat_qrcode()
        if is_logged_in:
            return {
                "status": "logged_in",
                "qrcode_path": None,
                "username": "已登录用户",
                "message": "已登录",
            }

        if qrcode_path:
            # 等待扫码
            success = action.wait_for_login(timeout=timeout)
            if success:
                return {
                    "status": "logged_in",
                    "qrcode_path": None,
                    "username": "已登录用户",
                    "message": "扫码登录成功",
                }
            return {
                "status": "timeout",
                "qrcode_path": qrcode_path,
                "username": None,
                "message": "扫码超时",
            }

        return {
            "status": "error",
            "qrcode_path": None,
            "username": None,
            "message": "获取二维码失败",
        }
    finally:
        client.close()


def logout(cookie_path=None, user_data_dir=None):
    """删除浏览器持久化数据和 Cookie 文件，重置登录状态"""
    import shutil
    # 1. 删除持久化浏览器数据目录
    paths = profile_paths(env_profile())
    data_dir = user_data_dir or str(paths.user_data_dir)
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    # 2. 删除 cookie JSON
    path = cookie_path or DEFAULT_COOKIE_PATH
    if os.path.exists(path):
        os.remove(path)
    # 3. 删除策略文件
    strategy_file = os.path.join(os.path.expanduser("~"), ".xiaohongshu", "strategy.json")
    if os.path.exists(strategy_file):
        os.remove(strategy_file)
    return {"status": "ok", "message": "登录状态已清除"}
