from typing import List, Optional, Literal
from pydantic import BaseModel


class OrganicResult(BaseModel):
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


class AIPreviewResult(BaseModel):
    type: Literal["ai_overview"] = "ai_overview"


class SearchResults(BaseModel):
    ai_overview: Optional[AIPreviewResult]
    organic_results: Optional[List[OrganicResult]]
    discussions_and_forums: Optional[List[ForumResult]]


class UnifiedSearchResponse(BaseModel):
    search_results: SearchResults


# === USER ANALYSIS ARTIFACTS ===


class AccountAnalysis(BaseModel):
    id: str
    name: str
    analysis: str
    error: bool
    # Additional structured fields we can extract
    balance: Optional[float] = None
    expense_count: Optional[int] = None
    deposit_count: Optional[int] = None
    account_type: Optional[str] = None


class FinancialRecommendation(BaseModel):
    category: str  # e.g., "Budgeting & Cash Flow", "Investment Strategy"
    title: str
    description: str
    priority: Literal["high", "medium", "low"] = "medium"
    action_items: List[str] = []


class UserAnalysis(BaseModel):
    id: str
    name: str
    account_analysis: List[AccountAnalysis]
    overall_analysis: str
    error: bool
    # Parsed recommendations from overall_analysis
    recommendations: Optional[List[FinancialRecommendation]] = None
    # Summary metrics
    total_balance: Optional[float] = None
    total_accounts: Optional[int] = None
    monthly_expenses: Optional[float] = None
    savings_rate: Optional[float] = None


class UserAnalysisArtifact(BaseModel):
    type: Literal["user_analysis"] = "user_analysis"
    user_analysis: UserAnalysis
