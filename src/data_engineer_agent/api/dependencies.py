"""FastAPI 请求依赖。"""

from typing import Annotated, cast

from fastapi import Depends, Request

from data_engineer_agent.service import DictionaryQueryService


def get_dictionary_service(request: Request) -> DictionaryQueryService:
    """取得应用启动时创建的数据字典服务。

    Args:
        request: 当前 FastAPI 请求，用于访问应用级共享状态。

    Returns:
        线程安全、可在多个只读请求间复用的数据字典查询服务。

    Raises:
        RuntimeError: 应用没有按工厂方法完成初始化时抛出。
    """

    service = getattr(request.app.state, "dictionary_service", None)
    if service is None:
        raise RuntimeError("数据字典服务尚未初始化")
    return cast(DictionaryQueryService, service)


DictionaryServiceDependency = Annotated[
    DictionaryQueryService,
    Depends(get_dictionary_service),
]
"""数据字典路由统一使用的类型化服务依赖。"""
