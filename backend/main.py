from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import OrchestratorAgent
from .models import LeadResearchRequest


app = FastAPI(
    title="LEADFORGE",
    version="1.0.0",
    description=(
        "AI-powered autonomous lead research, qualification, "
        "personalization, and outreach orchestration API."
    ),
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Temporary deterministic service implementations
# ---------------------------------------------------------

from typing import List

from .contracts import (
    BaseEnrichmentService,
    BaseOutreachService,
    BasePersonalizationService,
    BaseQualificationService,
    BaseResearchService,
)
from .models import Lead, LeadStatus


class MockResearchService(BaseResearchService):
    async def research(
        self,
        industry: str,
        query: str,
    ) -> List[Lead]:
        return [
            Lead(
                id="lead-001",
                company_name="Example Business",
                contact_name="Demo Contact",
                contact_email="demo@example.com",
                website="https://example.com",
                industry=industry,
                location="Demo Location",
            )
        ]


class MockEnrichmentService(BaseEnrichmentService):
    async def enrich(self, lead: Lead) -> Lead:
        return lead.model_copy(
            update={
                "status": LeadStatus.ENRICHED,
            }
        )


class MockQualificationService(BaseQualificationService):
    async def qualify(self, lead: Lead) -> Lead:
        return lead.model_copy(
            update={
                "qualification_score": 85,
                "qualification_reason": (
                    "Strong potential fit based on the target industry "
                    "and research criteria."
                ),
                "status": LeadStatus.QUALIFIED,
            }
        )


class MockPersonalizationService(BasePersonalizationService):
    async def personalize(self, lead: Lead) -> Lead:
        return lead.model_copy(
            update={
                "personalized_message": (
                    f"Hello {lead.contact_name or 'there'}, "
                    f"I noticed {lead.company_name} operates in "
                    f"{lead.industry or 'your industry'}. "
                    "I believe there may be an opportunity to "
                    "automate part of your workflow."
                ),
                "status": LeadStatus.PERSONALIZED,
            }
        )


class MockOutreachService(BaseOutreachService):
    async def send(self, lead: Lead) -> Lead:
        # Human approval will be enforced before real sending.
        return lead.model_copy(
            update={
                "status": LeadStatus.APPROVED,
            }
        )


# ---------------------------------------------------------
# Composition Root
# ---------------------------------------------------------

agent_system = OrchestratorAgent(
    research_service=MockResearchService(),
    enrichment_service=MockEnrichmentService(),
    qualification_service=MockQualificationService(),
    personalization_service=MockPersonalizationService(),
    outreach_service=MockOutreachService(),
)


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "LEADFORGE",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.post("/api/v1/run-agent")
async def execute_agent(payload: LeadResearchRequest):
    try:
        result = await agent_system.run_pipeline(
            target_industry=payload.industry,
            query=payload.query,
            max_leads=payload.max_leads,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="LEADFORGE pipeline execution failed.",
        ) from exc
