"""把仓储记录投影为稳定 MCP 响应的纯函数。"""

from __future__ import annotations

from collections import defaultdict

from data_engineer_agent.models import (
    DictionaryItemMatch,
    DictionaryItemRecord,
    DictionaryQueryRequest,
    DictionaryRequestResult,
    DictionaryTypeMatch,
    DictionaryTypeRecord,
    InputType,
    LookupResult,
    MatchMethod,
    QuerySummary,
    ResultStatus,
)


def unresolved_type_result(
    request_index: int,
    request: DictionaryQueryRequest,
    matched_types: list[DictionaryTypeRecord],
) -> DictionaryRequestResult:
    """构造字典类型未命中或存在歧义时的结果。

    Args:
        request_index: 当前查询组在原请求中的零基序号。
        request: 需要标记状态的原始查询组。
        matched_types: 类型仓储返回的零条或多条候选记录。

    Returns:
        带候选类型和逐项状态的请求结果。
    """

    status = ResultStatus.NOT_FOUND if not matched_types else ResultStatus.AMBIGUOUS
    error = "未找到字典类型" if not matched_types else "字典类型存在多个候选项"
    lookups = [
        LookupResult(input_type=input_type, input_value=value, status=status)
        for input_type, values in (
            (InputType.ITEM_CODE, request.item_codes),
            (InputType.ITEM_NAME, request.item_names),
            (InputType.KEYWORD, request.keywords),
        )
        for value in values
    ]
    return DictionaryRequestResult(
        request_index=request_index,
        dictionary_type_status=status,
        lookups=lookups,
        candidates=[to_type_match(record) for record in matched_types],
        error=error,
    )


def build_code_lookups(
    item_codes: list[str],
    records: list[DictionaryItemRecord],
) -> list[LookupResult]:
    """按照原始码值顺序组装精确查询结果。

    Args:
        item_codes: 调用方提交的码值列表。
        records: 仓储一次性返回的全部匹配记录。

    Returns:
        数量和顺序均与 ``item_codes`` 一致的查询结果。
    """

    records_by_code: dict[str, list[DictionaryItemRecord]] = defaultdict(list)
    for record in records:
        records_by_code[record.item_code].append(record)
    return [
        _build_lookup(
            InputType.ITEM_CODE,
            item_code,
            records_by_code[item_code],
            MatchMethod.EXACT_CODE,
        )
        for item_code in item_codes
    ]


def build_name_lookups(
    item_names: list[str],
    records: list[DictionaryItemRecord],
) -> list[LookupResult]:
    """按照原始名称顺序组装名称或别名精确查询结果。

    Args:
        item_names: 调用方提交的字典项名称或别名列表。
        records: 仓储一次性返回的全部匹配记录。

    Returns:
        优先使用正式名称匹配、其次使用别名匹配的逐项结果。
    """

    lookups: list[LookupResult] = []
    for item_name in item_names:
        normalized_name = item_name.casefold()
        exact_records = [
            record for record in records if record.item_name.casefold() == normalized_name
        ]
        alias_records = [
            record
            for record in records
            if record not in exact_records
            and normalized_name in {alias.casefold() for alias in record.aliases}
        ]
        match_method = (
            MatchMethod.EXACT_NAME if exact_records else MatchMethod.EXACT_ALIAS
        )
        lookups.append(
            _build_lookup(
                InputType.ITEM_NAME,
                item_name,
                exact_records or alias_records,
                match_method,
            )
        )
    return lookups


def build_keyword_lookups(keywords: list[str]) -> list[LookupResult]:
    """构造尚未启用的向量候选查询结果。

    Args:
        keywords: 调用方提交的自然语言候选检索词。

    Returns:
        每个关键词对应一个 ``NOT_ENABLED`` 结果，不执行数据库查询。
    """

    return [
        LookupResult(
            input_type=InputType.KEYWORD,
            input_value=keyword,
            status=ResultStatus.NOT_ENABLED,
            error="向量候选检索将在后续版本启用",
        )
        for keyword in keywords
    ]


def to_type_match(record: DictionaryTypeRecord) -> DictionaryTypeMatch:
    """把内部字典类型记录转换为稳定输出模型。

    Args:
        record: 包含数据库主键和内部字段的仓储记录。

    Returns:
        不暴露数据库主键的 MCP 字典类型对象。
    """

    return DictionaryTypeMatch(
        type_code=record.type_code,
        type_name=record.type_name,
        source_system=record.source_system,
        status=record.status,
    )


def to_item_match(
    record: DictionaryItemRecord,
    match_method: MatchMethod,
) -> DictionaryItemMatch:
    """把内部字典项记录转换为稳定输出模型。

    Args:
        record: 包含数据库主键和所属类型信息的仓储记录。
        match_method: 当前查询条件命中该记录的方式。

    Returns:
        不暴露数据库主键的 MCP 字典项对象。
    """

    return DictionaryItemMatch(
        type_code=record.type_code,
        type_name=record.type_name,
        source_system=record.source_system,
        item_code=record.item_code,
        item_name=record.item_name,
        description=record.description,
        status=record.status,
        match_method=match_method,
    )


def invalid_request(request_index: int, error: str) -> DictionaryRequestResult:
    """构造请求级非法结果。

    Args:
        request_index: 非法查询组在原请求中的零基序号。
        error: 可安全返回给调用方的校验错误说明。

    Returns:
        不包含匹配数据的 ``INVALID`` 请求结果。
    """

    return DictionaryRequestResult(
        request_index=request_index,
        dictionary_type_status=ResultStatus.INVALID,
        error=error,
    )


def summarize(results: list[DictionaryRequestResult]) -> QuerySummary:
    """统计批量响应中的业务状态。

    Args:
        results: 已按输入顺序完成处理的所有查询组结果。

    Returns:
        原子查询数量及各状态计数；纯列举请求按一个结果计算。
    """

    statuses: list[ResultStatus] = []
    lookup_count = 0
    for result in results:
        if result.lookups:
            lookup_count += len(result.lookups)
            statuses.extend(lookup.status for lookup in result.lookups)
        else:
            statuses.append(result.dictionary_type_status)
    return QuerySummary(
        request_count=len(results),
        lookup_count=lookup_count,
        succeeded=statuses.count(ResultStatus.FOUND),
        not_found=statuses.count(ResultStatus.NOT_FOUND),
        ambiguous=statuses.count(ResultStatus.AMBIGUOUS),
        invalid=statuses.count(ResultStatus.INVALID),
        not_enabled=statuses.count(ResultStatus.NOT_ENABLED),
    )


def _build_lookup(
    input_type: InputType,
    input_value: str,
    records: list[DictionaryItemRecord],
    match_method: MatchMethod,
) -> LookupResult:
    """根据匹配数量构造原子查询状态。

    Args:
        input_type: 原始查询条件类型。
        input_value: 原始查询值，用于结果回显。
        records: 该查询值对应的零条、一条或多条记录。
        match_method: 记录采用的精确命中方式。

    Returns:
        状态为未命中、唯一命中或歧义的原子查询结果。
    """

    if not records:
        status = ResultStatus.NOT_FOUND
    elif len(records) == 1:
        status = ResultStatus.FOUND
    else:
        status = ResultStatus.AMBIGUOUS
    return LookupResult(
        input_type=input_type,
        input_value=input_value,
        status=status,
        matches=[to_item_match(record, match_method) for record in records],
    )
