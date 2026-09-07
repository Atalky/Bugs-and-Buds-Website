from pydantic import BaseModel, ConfigDict, Field

class BlogBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class BlogCreate(BlogBase):
    pass

class BlogResponse(BlogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str