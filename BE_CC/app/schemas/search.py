from pydantic import BaseModel


class SearchResult(BaseModel):
    guid: str
    text: str
