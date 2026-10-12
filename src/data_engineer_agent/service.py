"""数据字典批量查询业务编排。"""

from __future__ import annotations

import logging

from data_engineer_agent import result_builder
from data_engineer_agent.cursor import decode_cursor, encode_cursor
from data_engineer_agent.models import (
    DictionaryQueryInput,
    DictionaryQueryRequest,
    DictionaryQueryResponse,
    DictionaryRequestResult,
    DictionaryTypeRecord,
    InputType,
    LookupResult,
    MatchMethod,
    ResultStatus,
)
from data_engineer_agent.repository import DictionaryRepository


LOGGER = logging.getLogger(__name__)


class DictionaryQueryService:
    """把一个批量 MCP 请求拆成确定性的字典查询并汇总结果。

    本类只负责查询流程编排；SQL 执行交给仓储，响应投影交给
    ``result_builder``，从而让主流程保持可读。
    """

    def __init__(self, repository: DictionaryRepository) -> None:
        """初始化查询服务。

        Args:
            repository: 只读数据字典仓储；服务不负责其生命周期。
        """

        self._repository = repository

    def query(self, query_input: DictionaryQueryInput) -> DictionaryQueryResponse:
        """处理全部查询组，并隔离组内可预期的参数错误。

        Args:
            query_input: 已通过 Pydantic 边界校验的完整批量请求。

        Returns:
            保持输入顺序的逐组结果及状态汇总。

        Raises:
            sqlalchemy.exc.SQLAlchemyError: 数据库异常属于系统故障，不转换为业务未命中。
        """

        LOGGER.info(
            "[数据字典][批量查询开始] requestCount=%s, includeInactive=%s",
            len(query_input.requests),
            query_input.include_inactive,
        )
        results: list[DictionaryRequestResult] = []
        for request_index, request in enumerate(query_input.requests):
            try:
                result = self._process_request(request_index, request, query_input)
            except ValueError as error:
                LOGGER.warning(
                    "[数据字典][请求校验失败] requestIndex=%s, reason=%s",
                    request_index,
                    error,
                )
                result = result_builder.invalid_request(request_index, str(error))
            results.append(result)
        response = DictionaryQueryResponse(
            results=results,
            summary=result_builder.summarize(results),
        )
        LOGGER.info(
            "[数据字典][批量查询完成] requestCount=%s, succeeded=%s, "
            "notFound=%s, ambiguous=%s, invalid=%s",
            response.summary.request_count,
            response.summary.succeeded,
            response.summary.not_found,
            response.summary.ambiguous,
            response.summary.invalid,
        )
        return response

    def _process_request(
        self,
        request_index: int,
        request: DictionaryQueryRequest,
        query_input: DictionaryQueryInput,
    ) -> DictionaryRequestResult:
        """为一个查询组选择类型内查询或全局名称反查。

        Args:
            request_index: 当前查询组在原请求中的零基序号。
            request: 当前查询组的类型、码值、名称和分页条件。
            query_input: 提供跨查询组共享的状态过滤和分页大小。

        Returns:
            当前查询组的完整处理结果。
        """

        if request.dictionary_type is None:
            return self._process_global_request(
                request_index,
                request,
                query_input.include_inactive,
            )
        matched_types = self._repository.find_dictionary_types(
            request.dictionary_type,
            request.source_system,
            query_input.include_inactive,
        )
        if len(matched_types) != 1:
            return result_builder.unresolved_type_result(
                request_index,
                request,
                matched_types,
            )
        matched_type = matched_types[0]
        if not (request.item_codes or request.item_names or request.keywords):
            return self._list_items(
                request_index,
                request,
                matched_type,
                query_input,
            )
        return self._resolve_items(
            request_index,
            request,
            matched_type,
            query_input.include_inactive,
        )

    def _process_global_request(
        self,
        request_index: int,
        request: DictionaryQueryRequest,
        include_inactive: bool,
    ) -> DictionaryRequestResult:
        """处理未指定类型的查询组。

        Args:
            request_index: 当前查询组在原请求中的零基序号。
            request: 未指定字典类型的查询条件。
            include_inactive: 是否允许匹配停用或失效数据。

        Returns:
            名称全局反查结果，以及无类型码值的逐项非法状态。
        """

        records = self._repository.find_dictionary_items(
            None,
            [],
            request.item_names,
            include_inactive,
        )
        lookups = [
            LookupResult(
                input_type=InputType.ITEM_CODE,
                input_value=item_code,
                status=ResultStatus.INVALID,
                error="按码值查询时必须提供 dictionary_type",
            )
            for item_code in request.item_codes
        ]
        lookups.extend(result_builder.build_name_lookups(request.item_names, records))
        lookups.extend(result_builder.build_keyword_lookups(request.keywords))
        return DictionaryRequestResult(
            request_index=request_index,
            dictionary_type_status=ResultStatus.NOT_PROVIDED,
            lookups=lookups,
        )

    def _list_items(
        self,
        request_index: int,
        request: DictionaryQueryRequest,
        matched_type: DictionaryTypeRecord,
        query_input: DictionaryQueryInput,
    ) -> DictionaryRequestResult:
        """列举唯一字典类型下的一页数据。

        Args:
            request_index: 当前查询组在原请求中的零基序号。
            request: 包含可选分页游标的类型列举请求。
            matched_type: 已唯一确定的内部字典类型记录。
            query_input: 提供分页大小和状态过滤条件。

        Returns:
            当前页字典项，以及存在后续数据时的下一页游标。

        Raises:
            ValueError: 调用方回传的游标无法解析时抛出。
        """

        after_sort_order, after_id = decode_cursor(request.cursor)
        records = self._repository.list_dictionary_items(
            matched_type.id,
            query_input.include_inactive,
            after_sort_order,
            after_id,
            query_input.page_size + 1,
        )
        has_more = len(records) > query_input.page_size
        page_records = records[: query_input.page_size]
        next_cursor = None
        if has_more and page_records:
            last_record = page_records[-1]
            next_cursor = encode_cursor(last_record.sort_order, last_record.id)
        return DictionaryRequestResult(
            request_index=request_index,
            dictionary_type_status=ResultStatus.FOUND,
            matched_type=result_builder.to_type_match(matched_type),
            items=[
                result_builder.to_item_match(record, MatchMethod.EXACT_NAME)
                for record in page_records
            ],
            next_cursor=next_cursor,
        )

    def _resolve_items(
        self,
        request_index: int,
        request: DictionaryQueryRequest,
        matched_type: DictionaryTypeRecord,
        include_inactive: bool,
    ) -> DictionaryRequestResult:
        """在唯一字典类型内批量解析码值、名称和关键词。

        Args:
            request_index: 当前查询组在原请求中的零基序号。
            request: 当前类型内的批量原子查询条件。
            matched_type: 已唯一确定的内部字典类型记录。
            include_inactive: 是否允许匹配停用或失效数据。

        Returns:
            与码值、名称和关键词输入顺序一致的逐项结果。
        """

        records = self._repository.find_dictionary_items(
            matched_type.id,
            request.item_codes,
            request.item_names,
            include_inactive,
        )
        lookups = result_builder.build_code_lookups(request.item_codes, records)
        lookups.extend(result_builder.build_name_lookups(request.item_names, records))
        lookups.extend(result_builder.build_keyword_lookups(request.keywords))
        return DictionaryRequestResult(
            request_index=request_index,
            dictionary_type_status=ResultStatus.FOUND,
            matched_type=result_builder.to_type_match(matched_type),
            lookups=lookups,
        )
