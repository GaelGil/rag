from typing import List, Optional, Literal
from pydantic import BaseModel


class ComposioSearchResult(BaseModel):
    type: Literal["organic"] = "organic"
    title: Optional[str]
    link: Optional[str]
    displayed_link: Optional[str]
    snippet: Optional[str]
    source: Optional[str]
    date: Optional[str]
    favicon: Optional[str]
    position: Optional[int]
    redirect_link: Optional[str]


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
    results: List


class UnifiedSearchResponse(BaseModel):
    search_results: SearchResults
