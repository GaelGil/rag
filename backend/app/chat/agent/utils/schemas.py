from typing import List
from pydantic import BaseModel


class EventSearchResults(BaseModel):
    title: str
    date: str
    address: str
    description: str
    image: str
    link: str


class NewsSearchResults(BaseModel):
    title: str
    date: str
    snippet: str
    link: str
    source: str
    favicon: str
    position: str


class VectorSearchResults(BaseModel):
    title: str


class SearchResults(BaseModel):
    tool_name: str
    result: (
        List[EventSearchResults] | List[VectorSearchResults] | List[NewsSearchResults]
    )
