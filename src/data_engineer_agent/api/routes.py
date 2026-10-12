"""数据字典 HTTP 路由。"""

from fastapi import APIRouter

from data_engineer_agent.api.dependencies import DictionaryServiceDependency
from data_engineer_agent.models import DictionaryQueryInput, DictionaryQueryResponse


router = APIRouter(prefix="/api/v1/data-dictionaries", tags=["数据字典"])


@router.post(
    "/query",
    response_model=DictionaryQueryResponse,
    operation_id="query_data_dictionary",
    summary="批量查询数据字典",
    description="批量列举字典项，或按码值、名称精确查询字典项。",
)
def query_data_dictionary(
    query_input: DictionaryQueryInput,
    service: DictionaryServiceDependency,
) -> DictionaryQueryResponse:
    """执行一次支持部分成功的批量数据字典查询。

    Args:
        query_input: 已由 Pydantic 完成字段、数量和组合约束校验的请求。
        service: FastAPI 从应用状态注入的数据字典应用服务。

    Returns:
        与输入顺序一致的逐项查询结果和状态汇总。
    """

    return service.query(query_input)
