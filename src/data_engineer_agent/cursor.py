"""数据字典列表的稳定分页游标编解码。"""

from __future__ import annotations

import base64
import binascii
import json


CURSOR_ENCODING = "utf-8"


def encode_cursor(sort_order: int, item_id: int) -> str:
    """把稳定排序位置编码为对调用方不透明的 URL 安全游标。

    Args:
        sort_order: 当前页最后一个字典项的业务排序值。
        item_id: 当前页最后一个字典项的数据库主键。

    Returns:
        可由 ``decode_cursor`` 还原的 URL 安全 Base64 字符串。
    """

    payload = json.dumps([sort_order, item_id], separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode(CURSOR_ENCODING)).decode(
        CURSOR_ENCODING
    )


def decode_cursor(cursor: str | None) -> tuple[int | None, int | None]:
    """解析分页游标，并拒绝被篡改或格式错误的值。

    Args:
        cursor: 调用方原样回传的游标；首页查询传 ``None``。

    Returns:
        ``(sort_order, item_id)``；首页返回 ``(None, None)``。

    Raises:
        ValueError: 游标不是预期的 Base64 双整数数组时抛出。
    """

    if cursor is None:
        return None, None
    try:
        payload = base64.urlsafe_b64decode(cursor.encode(CURSOR_ENCODING))
        values = json.loads(payload.decode(CURSOR_ENCODING))
        if (
            not isinstance(values, list)
            or len(values) != 2
            or not all(isinstance(value, int) for value in values)
        ):
            raise ValueError
        return values[0], values[1]
    except (ValueError, TypeError, json.JSONDecodeError, binascii.Error) as error:
        raise ValueError("cursor 格式无效") from error
