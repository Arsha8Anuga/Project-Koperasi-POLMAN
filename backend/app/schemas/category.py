from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):          # kalau BE-1 sudah punya base serupa, PAKAI PUNYA DIA
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class CategoryCreate(CamelModel):
    name: str = Field(min_length=1, max_length=60)
    description: str | None = None

class CategoryUpdate(CategoryCreate):
    is_active: bool = True

class CategoryOut(CamelModel):
    id: str
    name: str
    description: str | None = None
    is_active: bool