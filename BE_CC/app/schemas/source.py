from pydantic import AnyHttpUrl, BaseModel


class SourceCreate(BaseModel):
    url: AnyHttpUrl


class SourceUpdate(BaseModel):
    guid: str
    url: AnyHttpUrl


class SourceDelete(BaseModel):
    guid: str


class SourceResponse(BaseModel):
    guid: str
    url: str

    model_config = {"from_attributes": True}
