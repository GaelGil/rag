from typing import List, Optional
from pydantic import BaseModel


class AvailableOn(BaseModel):
    link: Optional[str]
    name: Optional[str]
    price: Optional[str]
    thumbnail: Optional[str]


class CastMember(BaseModel):
    name: Optional[str]
    role: Optional[str]


class Review(BaseModel):
    rating: Optional[int]
    title: Optional[str]
    link: Optional[str]


class PopularMovie(BaseModel):
    img: Optional[str]
    link: Optional[str]
    name: Optional[str]
    general_info: Optional[List[str]]


class PopularMovies(BaseModel):
    popular_movies: List[PopularMovie]


class Headlines(BaseModel):
    link: Optional[str]
    source: Optional[str]
    snippet: Optional[str]


class MovieInfo(BaseModel):
    available_on: List[AvailableOn]
    cast: List[CastMember]
    director: Optional[str]
    description: Optional[str]
    reviews: List[Review]
    headlines: List[Headlines]


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
