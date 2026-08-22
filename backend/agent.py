from typing import Any, Dict

from .contracts import (
    BaseEnrichmentService,
    BaseOutreachService,
    BasePersonalizationService,
    BaseQualificationService,
    BaseResearchService,
)
from .models import LeadResearchRequest, PipelineState


class OrchestratorAgent:
    """
    Coordinates the complete LEADFORGE lead pipeline.

    The orchestrator controls workflow order but does not know
    which external provider performs each operation.

    Pipeline:

        Research
            ↓
        Enrichment
            ↓
        Qualification
            ↓
        Personalization
            ↓
        Outreach
    """

    def __init__(
        self,
        research_service: BaseResearchService,
        enrichment_service: BaseEnrichmentService,
        qualification_service: BaseQualificationService,
        personalization_service: BasePersonalizationService,
        outreach_service: BaseOutreachService,
    ):
        self.research_service = research_service
        self.enrichment_service = enrichment_service
        self.qualification_service = qualification_service
        self.personalization_service = personalization_service
        self.outreach_service = outreach_service

    async def run_pipeline(
        self,
        target_industry: str,
        query: str,
        max_leads: int = 10,
    ) -> Dict[str, Any]:
        """
        Execute the LEADFORGE pipeline.

        The pipeline records failures in PipelineState instead of
        silently losing the execution state.
        """

        request = LeadResearchRequest(
            industry=target_industry,
            query=query,
            max_leads=max_leads,
        )

        state = PipelineState(request=request)

        try:
            # --------------------------------------------------
            # 1. RESEARCH
            # --------------------------------------------------

            state.current_stage = "research"

            state.leads = await self.research_service.research(
                industry=request.industry,
                query=request.query,
            )

            # Enforce the requested maximum.
            state.leads = state.leads[: request.max_leads]

            # --------------------------------------------------
            # 2. ENRICHMENT
            # --------------------------------------------------

            state.current_stage = "enrichment"

            enriched_leads = []

            for lead in state.leads:
                enriched_lead = await self.enrichment_service.enrich(lead)
                enriched_leads.append(enriched_lead)

            state.leads = enriched_leads

            # --------------------------------------------------
            # 3. QUALIFICATION
            # --------------------------------------------------

            state.current_stage = "qualification"

            qualified_leads = []

            for lead in state.leads:
                qualified_lead = await self.qualification_service.qualify(
                    lead
                )
                qualified_leads.append(qualified_lead)

            state.leads = qualified_leads

            # --------------------------------------------------
            # 4. PERSONALIZATION
            # --------------------------------------------------

            state.current_stage = "personalization"

            personalized_leads = []

            for lead in state.leads:
                personalized_lead = (
                    await self.personalization_service.personalize(lead)
                )
                personalized_leads.append(personalized_lead)

            state.leads = personalized_leads

            # --------------------------------------------------
            # 5. OUTREACH
            # --------------------------------------------------

            state.current_stage = "outreach"

            outreach_results = []

            for lead in state.leads:
                if not lead.personalized_message:
                    outreach_results.append(lead)
                    continue

                outreach_lead = await self.outreach_service.send(lead)
                outreach_results.append(outreach_lead)

            state.leads = outreach_results

            # --------------------------------------------------
            # COMPLETE
            # --------------------------------------------------

            state.current_stage = "completed"
            state.completed = True

        except Exception as exc:
            state.errors.append(
                f"Pipeline failed during '{state.current_stage}': {exc}"
            )

            state.completed = False

        return {
            "status": (
                "completed"
                if state.completed
                else "failed"
            ),
            "industry": request.industry,
            "query": request.query,
            "current_stage": state.current_stage,
            "leads_processed": len(state.leads),
            "leads": [
                lead.model_dump(mode="json")
                for lead in state.leads
            ],
            "errors": state.errors,
        }
