from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class LeadStatus(str, Enum):
    DISCOVERED = "discovered"
    ENRICHED = "enriched"
    QUALIFIED = "qualified"
    PERSONALIZED = "personalized"
    APPROVED = "approved"
    SENT = "sent"
    FAILED = "failed"


class Lead(BaseModel):
    """
    Canonical representation of a business lead inside LEADFORGE.
    """

    id: str
    company_name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    location: Optional[str] = None

    qualification_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    qualification_reason: Optional[str] = None
    personalized_message: Optional[str] = None

    status: LeadStatus = LeadStatus.DISCOVERED


class LeadResearchRequest(BaseModel):
    """
    Input submitted when a user asks LEADFORGE to find leads.
    """

    industry: str = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1, max_length=500)
    max_leads: int = Field(default=10, ge=1, le=100)


class PipelineState(BaseModel):
    """
    Structured state passed through the autonomous pipeline.
    """

    request: LeadResearchRequest
    leads: List[Lead] = Field(default_factory=list)

    current_stage: str = "research"
    errors: List[str] = Field(default_factory=list)

    completed: bool = False
