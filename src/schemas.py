from pydantic import BaseModel, Field


class Dataset(BaseModel):
    name: str = Field(max_length=150)
    node: str = Field(max_length=30)
    node_specific_identifier: str = Field(max_length=100)
    id: int | None
