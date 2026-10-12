"""数据字典 MCP 的请求对象与边界校验。"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MAX_BATCH_REQUESTS = 20
"""单次 MCP 调用允许包含的最大查询组数量。"""

MAX_LOOKUP_TERMS = 100
"""单次 MCP 调用允许包含的最大原子查询条件数量。"""

MAX_PAGE_SIZE = 200
"""单个字典类型每页允许返回的最大字典项数量。"""

DEFAULT_PAGE_SIZE = 100
"""调用方未指定分页大小时使用的默认值。"""


class DictionaryQueryRequest(BaseModel):
    """一个字典类型范围内的批量查询请求。"""

    model_config = ConfigDict(extra="forbid")

    dictionary_type: str | None = Field(
        default=None,
        description="字典类型编码、名称或别名；全局名称反查时可以为空。",
    )
    source_system: str | None = Field(
        default=None,
        description="可选的来源系统，用于消除同名字典类型歧义。",
    )
    item_codes: list[str] = Field(
        default_factory=list,
        description="需要查询含义的字典码值，始终按字符串处理。",
    )
    item_names: list[str] = Field(
        default_factory=list,
        description="需要反查码值的字典项名称或别名。",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="预留的自然语言候选检索词；首版返回未启用。",
    )
    cursor: str | None = Field(
        default=None,
        description="列举字典项时使用的分页游标。",
    )

    @field_validator("dictionary_type", "source_system", "cursor")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """规范化可选文本字段。

        Args:
            value: 调用方提交的可选文本；可以为 ``None`` 或包含首尾空格。

        Returns:
            去除首尾空格后的文本；空字符串统一转换为 ``None``。
        """

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("item_codes", "item_names", "keywords")
    @classmethod
    def normalize_text_list(cls, values: list[str]) -> list[str]:
        """规范化批量查询条件并拒绝空白元素。

        Args:
            values: MCP 调用方提交的同类查询条件列表。

        Returns:
            保持原顺序且已去除首尾空格的字符串列表。

        Raises:
            ValueError: 任一元素清理后为空字符串时抛出。
        """

        normalized = [value.strip() for value in values]
        if any(not value for value in normalized):
            raise ValueError("批量查询条件不能包含空字符串")
        return normalized

    @model_validator(mode="after")
    def require_query_condition(self) -> Self:
        """校验每个查询组至少包含一个有效条件。

        Returns:
            校验通过后的当前请求对象。

        Raises:
            ValueError: 字典类型、码值、名称和关键词全部为空时抛出。
        """

        if not (
            self.dictionary_type
            or self.item_codes
            or self.item_names
            or self.keywords
        ):
            raise ValueError("每个请求至少需要 dictionary_type 或查询条件")
        return self


class DictionaryQueryInput(BaseModel):
    """数据字典 MCP Tool 的完整批量输入。"""

    model_config = ConfigDict(extra="forbid")

    requests: list[DictionaryQueryRequest] = Field(
        min_length=1,
        max_length=MAX_BATCH_REQUESTS,
        description="按字典类型分组的批量查询请求。",
    )
    include_inactive: bool = Field(
        default=False,
        description="是否允许返回停用或失效的字典数据。",
    )
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="列举单个字典类型时每页最多返回的字典项数量。",
    )

    @model_validator(mode="after")
    def limit_total_lookup_terms(self) -> Self:
        """限制一次 MCP 调用中的原子查询总数。

        Returns:
            校验通过后的完整批量输入。

        Raises:
            ValueError: 码值、名称和关键词总数超过上限时抛出。
        """

        total = sum(
            len(request.item_codes)
            + len(request.item_names)
            + len(request.keywords)
            for request in self.requests
        )
        if total > MAX_LOOKUP_TERMS:
            raise ValueError(f"查询条件总数不能超过 {MAX_LOOKUP_TERMS}")
        return self
