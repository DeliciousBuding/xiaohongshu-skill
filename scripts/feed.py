"""
小红书笔记详情模块

基于 xiaohongshu-mcp/feed_detail.go 翻译
"""

import json
import sys
import time
import random
from typing import Optional, Dict, Any, Tuple

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH
from ._utils import make_feed_url


class FeedDetailAction:
    """笔记详情动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _make_feed_detail_url(self, feed_id: str, xsec_token: str, xsec_source: str = "pc_feed") -> str:
        """构建笔记详情 URL（委托给 _utils.make_feed_url）"""
        return make_feed_url(feed_id, xsec_token, xsec_source)

    def _scroll_to_comments(self):
        """滚动到评论区域"""
        self.client.page.evaluate("""() => {
            const comments = document.querySelector('.comments-wrap');
            if (comments) {
                comments.scrollIntoView();
            }
        }""")
        time.sleep(0.5)

    def _check_page_accessible(self):
        """检查页面是否可访问（笔记是否被删/私密/违规）"""
        page = self.client.page
        keywords = [
            "当前笔记暂时无法浏览", "该内容因违规已被删除", "该笔记已被删除",
            "内容不存在", "笔记不存在", "已失效", "私密笔记", "仅作者可见",
            "因用户设置你无法查看", "因违规无法查看"
        ]
        for kw in keywords:
            if page.locator(f"text={kw}").count() > 0:
                raise Exception(f"笔记不可访问: {kw}")
        # Also check selectors
        for sel in [".access-wrapper", ".error-wrapper", ".not-found-wrapper", ".blocked-wrapper"]:
            if page.locator(sel).count() > 0:
                raise Exception(f"笔记不可访问（检测到 {sel}）")

    def _human_scroll(self, speed="normal", direction="down"):
        """模拟人类滚动（从 Go feed_detail.go:469-517 移植）"""
        page = self.client.page
        viewport = page.evaluate("() => window.innerHeight")
        ratios = {"slow": 0.5, "normal": 0.7, "fast": 0.9}
        ratio = ratios.get(speed, 0.7)
        jitter = random.randint(-50, 50)
        delta = int(viewport * ratio * (0.7 + random.random() * 0.2)) + jitter
        if direction == "up":
            delta = -delta
        page.evaluate(f"window.scrollBy({{top: {delta}, behavior: 'smooth'}})")

    def _smart_scroll(self):
        """smartScroll：调度 WheelEvent 到 .note-scroller（从 Go feed_detail.go:553-569 移植）"""
        self.client.page.evaluate("""() => {
            const scroller = document.querySelector('.note-scroller');
            if (scroller) {
                scroller.dispatchEvent(new WheelEvent('wheel', {
                    deltaY: 200, deltaMode: 0, bubbles: true, cancelable: true
                }));
            }
        }""")

    def _load_comments(self, max_items: int = 0):
        """
        加载评论（滚动 + 点击加载更多）

        Args:
            max_items: 最大评论数量，0 表示全部
        """
        page = self.client.page

        # 滚动到评论区域
        self._scroll_to_comments()

        # 随机延迟，模拟人类行为
        def human_delay():
            time.sleep(random.uniform(0.3, 0.7))

        max_attempts = 50 if max_items == 0 else max_items * 3
        last_count = 0
        stagnant = 0

        for attempt in range(max_attempts):
            # 检查是否有"加载更多"按钮
            try:
                more_btn = page.locator('.more-comments')
                if more_btn.is_visible():
                    more_btn.click()
                    human_delay()
            except Exception:
                pass

            # 滚动：先 smartScroll（WheelEvent），再 humanScroll
            self._smart_scroll()
            human_delay()
            self._human_scroll()
            human_delay()

            # 获取当前评论数量
            try:
                comments = page.locator('.comment-item')
                current_count = comments.count()
            except Exception:
                current_count = 0

            if current_count == last_count:
                stagnant += 1
                if stagnant >= 5:
                    break
            else:
                stagnant = 0

            last_count = current_count

            # 检查是否达到目标数量
            if max_items > 0 and current_count >= max_items:
                break

    def _extract_feed_detail(self, feed_id: str) -> Optional[Dict[str, Any]]:
        """提取笔记详情数据"""
        page = self.client.page

        # 检查页面是否可访问
        self._check_page_accessible()

        # 传入 feed_id，只提取对应条目，避免序列化整个 Vue Reactive 代理
        result = page.evaluate("""(fid) => {
            var s = window.__INITIAL_STATE__;
            if (!s || !s.note || !s.note.noteDetailMap) return '';

            var ndm = s.note.noteDetailMap;
            var map = ndm;
            if (ndm.value !== undefined) map = ndm.value;
            else if (ndm._value !== undefined) map = ndm._value;

            var detail = map[fid];
            if (!detail) return '';

            return JSON.stringify(detail);
        }""", feed_id)

        if not result:
            return None

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return None

    def get_feed_detail(
        self,
        feed_id: str,
        xsec_token: str,
        load_comments: bool = False,
        max_comments: int = 0,
        xsec_source: str = "pc_feed",
    ) -> Optional[Dict[str, Any]]:
        """
        获取笔记详情

        Args:
            feed_id: 笔记 ID
            xsec_token: xsec_token 参数
            load_comments: 是否加载评论
            max_comments: 最大评论数量，0 表示全部
            xsec_source: 来源标识（pc_feed/pc_note/pc_search）

        Returns:
            笔记详情数据
        """
        client = self.client

        # 构建 URL 并导航
        url = self._make_feed_detail_url(feed_id, xsec_token, xsec_source)
        print(f"打开笔记详情页: {url}", file=sys.stderr)
        client.navigate(url)

        # 等待页面加载
        client.wait_for_initial_state()
        time.sleep(2)

        # 重试提取：noteDetailMap 可能需要额外时间填充
        detail = None
        for attempt in range(3):
            detail = self._extract_feed_detail(feed_id)
            if detail:
                break
            if attempt < 2:
                print(f"noteDetailMap 未就绪，等待重试 ({attempt + 1}/3)...", file=sys.stderr)
                time.sleep(2)

        # 加载评论
        if detail and load_comments:
            print("加载评论中...", file=sys.stderr)
            self._load_comments(max_comments)
            # 重新提取以包含评论数据
            detail = self._extract_feed_detail(feed_id) or detail

        if not detail:
            print("未获取到笔记详情", file=sys.stderr)
            return None

        return detail


def feed_detail(
    feed_id: str,
    xsec_token: str,
    load_comments: bool = False,
    max_comments: int = 0,
    xsec_source: str = "pc_feed",
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Optional[Dict[str, Any]]:
    """
    获取笔记详情

    Args:
        feed_id: 笔记 ID
        xsec_token: xsec_token 参数
        load_comments: 是否加载评论
        max_comments: 最大评论数量
        xsec_source: 来源标识
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        笔记详情数据
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = FeedDetailAction(client)
        return action.get_feed_detail(
            feed_id=feed_id,
            xsec_token=xsec_token,
            load_comments=load_comments,
            max_comments=max_comments,
            xsec_source=xsec_source,
        )
    finally:
        client.close()
