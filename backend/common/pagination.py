from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResult(BaseModel, Generic[T]):
    items: List[T] = Field(default_factory=list, description="List of items in current page")
    total: int = Field(default=0, description="Total count of items")
    page: int = Field(default=1, description="Current page number")
    limit: int = Field(default=20, description="Items per page limit")
    total_pages: int = Field(default=1, description="Total available pages")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
