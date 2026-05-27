"""
小红书公共工具函数

提取各模块中重复使用的辅助逻辑。
"""

from typing import Any


def is_element_blocked(page, elem):
    """检测元素是否被其他元素遮挡

    Go 参考: publish.go:187-203 isElementBlocked
    通过 JS getBoundingClientRect + elementFromPoint 判断元素中心点
    是否被其他 DOM 节点遮挡。
    """
    result = elem.evaluate("""(el) => {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return true;
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        const target = document.elementFromPoint(x, y);
        return !(target === el || el.contains(target));
    }""")
    return result


def make_feed_url(feed_id: str, xsec_token: str, xsec_source: str = "pc_feed") -> str:
    """构建笔记详情 URL

    在 comment.py, feed.py, interact.py 中原本各自定义，现统一到此。
    """
    return f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source={xsec_source}"


def unwrap_value(obj: Any) -> Any:
    """解包 Vue ref 代理对象

    处理 Playwright 返回的 JavaScript 对象被包装成 {value: ...} 或 {_value: ...} 的情况。
    同时兼容 json.loads 产生的 dict 和 Playwright 返回的属性访问对象。

    原逻辑在 search.py, feed.py, explore.py, interact.py, user.py 的 JS 代码中重复出现，
    现提供 Python 侧统一解包函数供相关模块使用。
    """
    if isinstance(obj, dict):
        if obj.get('value') is not None:
            return obj['value']
        if obj.get('_value') is not None:
            return obj['_value']
    else:
        if hasattr(obj, 'value') and obj.value is not None:
            return obj.value
        if hasattr(obj, '_value') and obj._value is not None:
            return obj._value
    return obj
