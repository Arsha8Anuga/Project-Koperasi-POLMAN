from pydantic import Field, field_validator

from app.schemas.common import CamelModel, DocModel


def _clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


class CategoryOut(DocModel):
    name: str
    description: str | None = None
    is_active: bool


class CategoryCreate(CamelModel):
    name: str = Field(min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=200)

    _c = field_validator("name", "description", mode="before")(_clean)


class CategoryUpdate(CategoryCreate):
    is_active: bool
