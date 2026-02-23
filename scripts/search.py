"""
小红书搜索模块

基于 xiaohongshu-mcp/search.go 翻译
"""

import json
import sys
import time
import urllib.parse
from typing import Optional, List, Dict, Any

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


# 筛选选项映射表（来自 Go 源码）
FILTER_OPTIONS_MAP = {
    1: [  # 排序依据
        {"index": 1, "text": "综合"},
        {"index": 2, "text": "最新"},
        {"index": 3, "text": "最多点赞"},
        {"index": 4, "text": "最多评论"},
        {"index": 5, "text": "最多收藏"},
    ],
    2: [  # 笔记类型
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "视频"},
        {"index": 3, "text": "图文"},
    ],
    3: [  # 发布时间
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "一天内"},
        {"index": 3, "text": "一周内"},
        {"index": 4, "text": "半年内"},
    ],
    4: [  # 搜索范围
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "已看过"},
        {"index": 3, "text": "未看过"},
        {"index": 4, "text": "已关注"},
    ],
    5: [  # 位置距离
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "同城"},
        {"index": 3, "text": "附近"},
    ],
}


class SearchAction:
    """搜索动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _make_search_url(self, keyword: str) -> str:
        """构建搜索 URL"""
        params = urllib.parse.urlencode({
            "keyword": keyword,
            "source": "web_explore_feed",
        })
        return f"https://www.xiaohongshu.com/search_result?{params}"

    def _apply_filters(
        self,
        sort_by: Optional[str] = None,
        note_type: Optional[str] = None,
        publish_time: Optional[str] = None,
        search_scope: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """应用筛选条件"""
        page = self.client.page

        # 检查是否有筛选条件
        has_filters = any([sort_by, note_type, publish_time, search_scope, location])
        if not has_filters:
            return

        # 悬停在筛选按钮上
        try:
            filter_btn = page.locator('div.filter')
            filter_btn.hover()
            time.sleep(0.5)

            # 等待筛选面板出现
            page.wait_for_selector('div.filter-panel', timeout=5000)
        except Exception as e:
            print(f"打开筛选面板失败: {e}", file=sys.stderr)
            return

        # 映射筛选选项到文本
        filter_texts = []

        if sort_by:
            text = self._find_filter_text(1, sort_by)
            if text:
                filter_texts.append(text)

        if note_type:
            text = self._find_filter_text(2, note_type)
            if text:
                filter_texts.append(text)

        if publish_time:
            text = self._find_filter_text(3, publish_time)
            if text:
                filter_texts.append(text)

        if search_scope:
            text = self._find_filter_text(4, search_scope)
            if text:
                filter_texts.append(text)

        if location:
            text = self._find_filter_text(5, location)
            if text:
                filter_texts.append(text)

        # 应用筛选：使用文本定位器，避免依赖 DOM 顺序
        filter_panel = page.locator('div.filter-panel')
        for tag_text in filter_texts:
            try:
                filter_panel.get_by_text(tag_text, exact=True).click()
                time.sleep(0.3)
            except Exception as e:
                print(f"点击筛选选项失败: {e}", file=sys.stderr)

        # 等待页面更新
        time.sleep(1)

    def _find_filter_text(self, filters_group: int, text: str) -> Optional[str]:
        """查找筛选选项的显示文本（用于文本定位器）"""
        options = FILTER_OPTIONS_MAP.get(filters_group, [])
        for opt in options:
            if opt["text"] == text:
                return opt["text"]
        return None

    def _dismiss_login_popup(self, search_url: Optional[str] = None):
        """关闭登录弹窗（如果存在），并处理可能的重定向"""
        page = self.client.page
        try:
            close_btn = page.locator('.login-container .close-button, .login-container .close, .close-circle')
            if close_btn.count() > 0:
                close_btn.first.click()
                time.sleep(1)
            else:
                overlay = page.locator('.login-container')
                if overlay.count() > 0 and overlay.first.is_visible():
                    page.keyboard.press("Escape")
                    time.sleep(1)
                else:
                    return  # 无弹窗，无需处理
        except Exception:
            return

        # 关闭弹窗后，小红书可能将未登录用户重定向到首页推荐流
        # 检测是否被重定向离开搜索页，若是则重新导航回搜索页
        if search_url and 'search_result' not in page.url:
            print("登录弹窗关闭后被重定向，重新导航到搜索页...", file=sys.stderr)
            self.client.navigate(search_url)
            time.sleep(2)

    def _extract_from_state(self, limit: int) -> List[Dict[str, Any]]:
        """从 __INITIAL_STATE__ 提取搜索结果（SSR 路径）"""
        page = self.client.page
        result = page.evaluate("""() => {
            const feeds = window.__INITIAL_STATE__?.search?.feeds;
            const data = feeds?.value || feeds?._value;
            if (!data || !Array.isArray(data) || data.length === 0) return '';

            return JSON.stringify(data.slice(0, 50).map(item => {
                const nc = item.noteCard || {};
                const user = nc.user || {};
                const info = nc.interactInfo || {};
                const cover = nc.cover || {};
                return {
                    id: item.id || '',
                    xsec_token: item.xsecToken || '',
                    title: nc.displayTitle || '',
                    type: nc.type || '',
                    user: user.nickname || user.nickName || '',
                    user_id: user.userId || '',
                    user_avatar: user.avatar || '',
                    liked_count: info.likedCount || '0',
                    collected_count: info.collectedCount || '0',
                    comment_count: info.commentCount || '0',
                    shared_count: info.sharedCount || '0',
                    cover_url: cover.urlDefault || cover.urlPre || '',
                };
            }));
        }""")
        if not result:
            return []
        try:
            feeds = json.loads(result)
            return feeds[:limit] if limit > 0 else feeds
        except json.JSONDecodeError:
            return []

    def _extract_from_dom(self, limit: int) -> List[Dict[str, Any]]:
        """从 DOM 提取搜索结果（客户端渲染路径）"""
        page = self.client.page
        result = page.evaluate("""(limit) => {
            const items = document.querySelectorAll('section.note-item');
            if (!items || items.length === 0) return '';

            const results = [];
            for (let i = 0; i < Math.min(items.length, limit); i++) {
                const item = items[i];
                const entry = {};

                // 提取 ID 和 xsec_token（从带 xsec_token 的链接）
                const coverLink = item.querySelector('a.cover[href*="/explore/"]');
                if (coverLink) {
                    const href = coverLink.getAttribute('href') || '';
                    const idMatch = href.match(/\\/explore\\/([a-f0-9]+)/);
                    entry.id = idMatch ? idMatch[1] : '';
                    const tokenMatch = href.match(/xsec_token=([^&]+)/);
                    entry.xsec_token = tokenMatch ? decodeURIComponent(tokenMatch[1]) : '';
                } else {
                    const anyLink = item.querySelector('a[href*="/explore/"]');
                    if (anyLink) {
                        const href = anyLink.getAttribute('href') || '';
                        const idMatch = href.match(/\\/explore\\/([a-f0-9]+)/);
                        entry.id = idMatch ? idMatch[1] : '';
                        const tokenMatch = href.match(/xsec_token=([^&]+)/);
                        entry.xsec_token = tokenMatch ? decodeURIComponent(tokenMatch[1]) : '';
                    } else {
                        entry.id = '';
                        entry.xsec_token = '';
                    }
                }

                // 标题
                const titleEl = item.querySelector('.title span, .title, a.title');
                entry.title = titleEl ? titleEl.textContent.trim() : '';

                // 封面图
                const coverImg = item.querySelector('img');
                entry.cover_url = coverImg ? (coverImg.getAttribute('src') || '') : '';

                // 判断类型（视频/图文）
                const videoIcon = item.querySelector('.play-icon, [class*="video"], svg.play');
                entry.type = videoIcon ? 'video' : 'normal';

                // 作者信息
                const authorEl = item.querySelector('.author-wrapper .name, .author .name, [class*="author"] .name, .nickname');
                entry.user = authorEl ? authorEl.textContent.trim() : '';

                const authorLink = item.querySelector('a[href*="/user/profile/"]');
                if (authorLink) {
                    const href = authorLink.getAttribute('href') || '';
                    const uidMatch = href.match(/\\/user\\/profile\\/([a-f0-9]+)/);
                    entry.user_id = uidMatch ? uidMatch[1] : '';
                } else {
                    entry.user_id = '';
                }

                const avatarImg = item.querySelector('.author-wrapper img, .author img');
                entry.user_avatar = avatarImg ? (avatarImg.getAttribute('src') || '') : '';

                // 互动数据
                const likeEl = item.querySelector('.like-wrapper .count, [class*="like"] .count, .like-count');
                entry.liked_count = likeEl ? likeEl.textContent.trim() : '0';

                // 搜索结果页一般只显示点赞数
                entry.collected_count = '0';
                entry.comment_count = '0';
                entry.shared_count = '0';

                results.push(entry);
            }
            return JSON.stringify(results);
        }""", limit if limit > 0 else 50)

        if not result:
            return []
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []

    def search(
        self,
        keyword: str,
        sort_by: Optional[str] = None,
        note_type: Optional[str] = None,
        publish_time: Optional[str] = None,
        search_scope: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        搜索小红书内容

        Args:
            keyword: 搜索关键词
            sort_by: 排序方式：综合 最新 最多点赞 最多评论 最多收藏
            note_type: 笔记类型：不限 视频 图文
            publish_time: 发布时间：不限 一天内 一周内 半年内
            search_scope: 搜索范围：不限 已看过 未看过 已关注
            location: 位置距离：不限 同城 附近
            limit: 返回数量限制

        Returns:
            搜索结果列表
        """
        client = self.client
        page = client.page

        # 导航到搜索页面
        search_url = self._make_search_url(keyword)
        client.navigate(search_url)

        # 关闭登录弹窗（如果存在），传入搜索URL以便重定向后能回来
        self._dismiss_login_popup(search_url=search_url)

        # 等待页面加载
        client.wait_for_initial_state()
        time.sleep(3)

        # 滚动页面触发加载更多内容
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(0.5)

        # 应用筛选条件
        self._apply_filters(
            sort_by=sort_by,
            note_type=note_type,
            publish_time=publish_time,
            search_scope=search_scope,
            location=location,
        )

        # 等待搜索结果 DOM 渲染
        try:
            page.wait_for_selector('section.note-item', timeout=10000)
        except Exception:
            print("等待搜索结果 DOM 超时", file=sys.stderr)

        # 优先从 __INITIAL_STATE__ 提取（数据更完整）
        feeds = self._extract_from_state(limit)
        if feeds:
            return feeds

        # 回退到 DOM 提取（客户端渲染场景）
        print("__INITIAL_STATE__ 无数据，从 DOM 提取搜索结果", file=sys.stderr)
        feeds = self._extract_from_dom(limit)
        if not feeds:
            print("未获取到搜索结果", file=sys.stderr)
        return feeds


def search(
    keyword: str,
    sort_by: Optional[str] = None,
    note_type: Optional[str] = None,
    publish_time: Optional[str] = None,
    search_scope: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 10,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> List[Dict[str, Any]]:
    """
    搜索小红书内容

    Args:
        keyword: 搜索关键词
        sort_by: 排序方式
        note_type: 笔记类型
        publish_time: 发布时间
        search_scope: 搜索范围
        location: 位置距离
        limit: 返回数量限制
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        搜索结果列表
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = SearchAction(client)
        return action.search(
            keyword=keyword,
            sort_by=sort_by,
            note_type=note_type,
            publish_time=publish_time,
            search_scope=search_scope,
            location=location,
            limit=limit,
        )
    finally:
        client.close()
