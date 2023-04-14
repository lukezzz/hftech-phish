# 自定义分页入参和返回，配合前段使用

from typing import TypeVar, Generic, Sequence

from pydantic import conint, BaseModel
from fastapi import Query

from fastapi_pagination.bases import BasePage, AbstractParams, RawParams

T = TypeVar("T")
C = TypeVar("C")


class Params(BaseModel, AbstractParams):
    current: int = Query(1, ge=1, description="Page number")
    pageSize: int = Query(50, ge=1, le=100, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.pageSize,
            offset=self.pageSize * (self.current - 1),
        )


class Page(BasePage[T], Generic[T]):
    current: conint(ge=1)  # type: ignore
    pageSize: conint(ge=1)  # type: ignore

    __params_type__ = Params

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ):
        if not isinstance(params, Params):
            raise ValueError("Page should be used with Params")

        return cls(
            total=total,
            items=items,
            current=params.current,
            pageSize=params.pageSize,
        )
