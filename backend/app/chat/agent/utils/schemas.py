from typing import List, Optional, Literal
from pydantic import BaseModel


class PriceMovement(BaseModel):
    movement: Optional[Literal["Up", "Down", "Neutral"]]
    percentage: Optional[float]
    value: Optional[float]


class MarketResult(BaseModel):
    type: Literal["market"] = "market"
    name: Optional[str]
    link: Optional[str]
    stock: Optional[str]
    price: Optional[float]
    price_movement: Optional[PriceMovement]
    serpapi_link: Optional[str]
    region: Optional[str] = None  # for flattened use


class EventSearchResults(BaseModel):
    title: str
    date: str
    address: str
    description: str
    image: str
    link: str


class ForumAnswer(BaseModel):
    link: Optional[str]
    snippet: Optional[str]
    extensions: Optional[List[str]] = None


class ForumResult(BaseModel):
    type: Literal["forum"] = "forum"
    title: Optional[str]
    link: Optional[str]
    source: Optional[str]
    date: Optional[str]
    extensions: List[str]
    answers: List[ForumAnswer]


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
    results: (
        List[EventSearchResults] | List[VectorSearchResults] | List[NewsSearchResults]
    )


class UnifiedSearchResponse(BaseModel):
    search_results: SearchResults
