"""数据字典 MCP 协议使用的枚举。"""

from enum import StrEnum


class ResultStatus(StrEnum):
    """单个查询结果的业务状态。"""

    FOUND = "FOUND"
    """查询条件唯一命中。"""

    NOT_FOUND = "NOT_FOUND"
    """查询条件没有命中。"""

    AMBIGUOUS = "AMBIGUOUS"
    """查询条件命中多条，需要调用方确认。"""

    INVALID = "INVALID"
    """输入组合不符合业务约束。"""

    NOT_ENABLED = "NOT_ENABLED"
    """对应能力已经预留，但当前版本尚未启用。"""

    NOT_PROVIDED = "NOT_PROVIDED"
    """当前查询没有提供可选的字典类型。"""


class InputType(StrEnum):
    """原子查询条件的类型。"""

    ITEM_CODE = "ITEM_CODE"
    """按字典码值查询。"""

    ITEM_NAME = "ITEM_NAME"
    """按字典项名称查询。"""

    KEYWORD = "KEYWORD"
    """按自然语言关键词发现候选项。"""


class MatchMethod(StrEnum):
    """字典数据的命中方式。"""

    EXACT_CODE = "EXACT_CODE"
    """字典码值精确命中。"""

    EXACT_NAME = "EXACT_NAME"
    """字典项名称精确命中。"""

    EXACT_ALIAS = "EXACT_ALIAS"
    """字典项别名精确命中。"""
