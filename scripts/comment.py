"""
小红书评论模块

基于 xiaohongshu-mcp/comment_feed.go 翻译
"""

import json
import sys
import time
import random
from typing import Optional, Dict, Any

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


class CommentAction:
    """评论动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _make_feed_url(self, feed_id: str, xsec_token: str, xsec_source: str = "pc_feed") -> str:
        """构建笔记详情 URL"""
        return f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source={xsec_source}"

    def _navigate_to_feed(self, feed_id: str, xsec_token: str):
        """导航到笔记详情页并等待加载"""
        url = self._make_feed_url(feed_id, xsec_token)
        print(f"打开笔记详情页: {url}", file=sys.stderr)
        self.client.navigate(url)
        self.client.wait_for_initial_state()
        time.sleep(2)

    def _type_and_submit(self, content: str) -> bool:
        """在评论输入框中输入文字并提交"""
        page = self.client.page

        # 点击评论输入框激活（span 占位符）
        try:
            input_trigger = page.locator('div.input-box div.content-edit span')
            input_trigger.first.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"点击评论输入框失败: {e}", file=sys.stderr)
            return False

        # 在 contenteditable 的 p 元素中输入文字
        try:
            input_el = page.locator('div.input-box div.content-edit p.content-input')
            input_el.first.click()
            time.sleep(0.3)
            page.keyboard.type(content, delay=50)
            time.sleep(0.5)
        except Exception as e:
            print(f"输入评论内容失败: {e}", file=sys.stderr)
            return False

        # 点击发送按钮
        try:
            submit_btn = page.locator('div.bottom button.submit')
            submit_btn.first.click()
            time.sleep(1.5)
        except Exception as e:
            print(f"点击发送按钮失败: {e}", file=sys.stderr)
            return False

        return True

    def post_comment(
        self,
        feed_id: str,
        xsec_token: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        发表评论

        Args:
            feed_id: 笔记 ID
            xsec_token: xsec_token
            content: 评论内容

        Returns:
            操作结果
        """
        self._navigate_to_feed(feed_id, xsec_token)

        # 滚动到评论区域
        self.client.page.evaluate("""() => {
            const comments = document.querySelector('.comments-wrap') ||
                              document.querySelector('.comment-wrapper');
            if (comments) comments.scrollIntoView();
        }""")
        time.sleep(1)

        success = self._type_and_submit(content)

        if success:
            print("评论发送成功", file=sys.stderr)
            return {
                "status": "success",
                "feed_id": feed_id,
                "content": content,
                "message": "评论发送成功",
            }
        else:
            return {
                "status": "error",
                "feed_id": feed_id,
                "content": content,
                "message": "评论发送失败",
            }

    def reply_to_comment(
        self,
        feed_id: str,
        xsec_token: str,
        comment_id: str,
        reply_user_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        回复评论

        Args:
            feed_id: 笔记 ID
            xsec_token: xsec_token
            comment_id: 目标评论 ID
            reply_user_id: 被回复用户 ID
            content: 回复内容

        Returns:
            操作结果
        """
        self._navigate_to_feed(feed_id, xsec_token)

        page = self.client.page

        # 滚动到评论区域
        page.evaluate("""() => {
            const comments = document.querySelector('.comments-wrap') ||
                              document.querySelector('.comment-wrapper');
            if (comments) comments.scrollIntoView();
        }""")
        time.sleep(1)

        # 找到目标评论并点击"回复"按钮
        try:
            # 尝试通过评论 ID 定位
            comment_el = page.locator(f'[data-comment-id="{comment_id}"]')
            if comment_el.count() == 0:
                # 回退：通过遍历评论列表查找
                comment_el = page.locator('.comment-item').filter(has_text=comment_id)

            if comment_el.count() > 0:
                # 悬停以显示回复按钮
                comment_el.first.hover()
                time.sleep(0.3)

                # 点击回复按钮
                reply_btn = comment_el.first.locator('.reply-btn, button:has-text("回复"), span:has-text("回复")')
                if reply_btn.count() > 0:
                    reply_btn.first.click()
                    time.sleep(0.5)
                else:
                    print("未找到回复按钮，尝试直接在评论框回复", file=sys.stderr)
            else:
                print(f"未找到评论 {comment_id}，尝试直接在评论框回复", file=sys.stderr)
        except Exception as e:
            print(f"定位目标评论失败: {e}", file=sys.stderr)

        # 输入回复内容并发送
        success = self._type_and_submit(content)

        if success:
            print("回复发送成功", file=sys.stderr)
            return {
                "status": "success",
                "feed_id": feed_id,
                "comment_id": comment_id,
                "reply_user_id": reply_user_id,
                "content": content,
                "message": "回复发送成功",
            }
        else:
            return {
                "status": "error",
                "feed_id": feed_id,
                "comment_id": comment_id,
                "content": content,
                "message": "回复发送失败",
            }


def post_comment(
    feed_id: str,
    xsec_token: str,
    content: str,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """
    发表评论

    Args:
        feed_id: 笔记 ID
        xsec_token: xsec_token
        content: 评论内容
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        操作结果
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = CommentAction(client)
        return action.post_comment(feed_id, xsec_token, content)
    finally:
        client.close()


def reply_to_comment(
    feed_id: str,
    xsec_token: str,
    comment_id: str,
    reply_user_id: str,
    content: str,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """
    回复评论

    Args:
        feed_id: 笔记 ID
        xsec_token: xsec_token
        comment_id: 目标评论 ID
        reply_user_id: 被回复用户 ID
        content: 回复内容
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        操作结果
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = CommentAction(client)
        return action.reply_to_comment(
            feed_id, xsec_token, comment_id, reply_user_id, content
        )
    finally:
        client.close()
