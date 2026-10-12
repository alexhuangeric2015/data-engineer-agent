"""数据字典 MCP 对调用方公开的响应模型。"""

from pydantic import BaseModel, Field

from data_engineer_agent.models.enums import InputType, MatchMethod, ResultStatus


class DictionaryTypeMatch(BaseModel):
    """对调用方可见的字典类型信息。"""

    type_code: str = Field(description="字典类型唯一编码。")
    type_name: str = Field(description="字典类型名称。")
    source_system: str = Field(description="字典来源系统。")
    status: str = Field(description="字典类型状态。")


class DictionaryItemMatch(BaseModel):
    """对调用方可见的字典项匹配结果。"""

    type_code: str = Field(description="所属字典类型编码。")
    type_name: str = Field(description="所属字典类型名称。")
    source_system: str = Field(description="字典来源系统。")
    item_code: str = Field(description="字典码值。")
    item_name: str = Field(description="字典项名称。")
    description: str | None = Field(description="字典项业务说明；无说明时为空。")
    status: str = Field(description="字典项状态。")
    match_method: MatchMethod = Field(description="本条结果的精确命中方式。")


class LookupResult(BaseModel):
    """一个码值、名称或关键词的独立查询结果。"""

    input_type: InputType = Field(description="原始查询条件类型。")
    input_value: str = Field(description="原始查询值。")
    status: ResultStatus = Field(description="原子查询业务状态。")
    matches: list[DictionaryItemMatch] = Field(
        default_factory=list,
        description="精确命中的字典项；歧义时可能包含多条。",
    )
    error: str | None = Field(
        default=None,
        description="非法输入或能力未启用时的可读错误信息。",
    )


class DictionaryRequestResult(BaseModel):
    """一个批量分组请求的完整处理结果。"""

    request_index: int = Field(description="请求在输入 requests 中的零基序号。")
    dictionary_type_status: ResultStatus = Field(description="字典类型解析状态。")
    matched_type: DictionaryTypeMatch | None = Field(
        default=None,
        description="唯一命中的字典类型；未命中或歧义时为空。",
    )
    lookups: list[LookupResult] = Field(
        default_factory=list,
        description="码值、名称和关键词的逐项查询结果。",
    )
    items: list[DictionaryItemMatch] = Field(
        default_factory=list,
        description="仅列举字典类型时返回的字典项。",
    )
    candidates: list[DictionaryTypeMatch] = Field(
        default_factory=list,
        description="字典类型存在歧义时返回的候选类型。",
    )
    next_cursor: str | None = Field(
        default=None,
        description="下一页游标；没有更多数据时为空。",
    )
    error: str | None = Field(
        default=None,
        description="请求级错误信息；请求成功时为空。",
    )


class QuerySummary(BaseModel):
    """一次 MCP 调用的结果统计。"""

    request_count: int = Field(description="外层批量请求数量。")
    lookup_count: int = Field(description="原子查询数量，不含纯列举请求。")
    succeeded: int = Field(description="成功的原子查询或列举请求数量。")
    not_found: int = Field(description="未命中的原子查询或列举请求数量。")
    ambiguous: int = Field(description="存在歧义的原子查询或类型数量。")
    invalid: int = Field(description="输入非法的原子查询或请求数量。")
    not_enabled: int = Field(description="当前版本尚未启用的查询数量。")


class DictionaryQueryResponse(BaseModel):
    """数据字典 MCP Tool 的结构化响应。"""

    results: list[DictionaryRequestResult] = Field(description="逐请求处理结果。")
    summary: QuerySummary = Field(description="批量处理统计。")
