from typing import Any, Dict

from .contracts import (
    BaseEnrichmentService,
    BaseOutreachService,
    BasePersonalizationService,
    BaseQualificationService,
    BaseResearchService,
)
from .exceptions import AuthenticationError, RetryableError
from .models import Lead, LeadResearchRequest, LeadStatus, PipelineState

QUALIFICATION_THRESHOLD = 60.0


class OrchestratorAgent:
    """
    Coordinates the complete LEADFORGE lead pipeline.
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

    async def _run_stage(
        self,
        leads: list[Lead],
        stage_name: str,
        operation,
        state: PipelineState,
    ) -> list[Lead]:
        """
        Runs one pipeline stage per-lead.

        - AuthenticationError propagates up and halts the whole batch
          (a dead API key affects every lead, not just one).
        - RetryableError (rate limits, timeouts) leaves the lead's
          status untouched so a later retry pass can pick it up.
        - Any other exception marks that single lead FAILED and the
          batch continues.
        """
        results: list[Lead] = []

        for lead in leads:
            if lead.status == LeadStatus.FAILED:
                results.append(lead)
                continue

            try:
                updated_lead = await operation(lead)
                results.append(updated_lead)

            except AuthenticationError:
                raise

            except RetryableError as exc:
                state.errors.append(
                    f"[{stage_name}] lead '{lead.id}' temporary failure "
                    f"(will retry later): {exc}"
                )
                results.append(lead)

            except Exception as exc:
                state.errors.append(
                    f"[{stage_name}] lead '{lead.id}' failed: {exc}"
                )
                results.append(
                    lead.model_copy(update={"status": LeadStatus.FAILED})
                )

        return results

    async def run_pipeline(
        self,
        target_industry: str,
        query: str,
        max_leads: int = 10,
    ) -> Dict[str, Any]:
        request = LeadResearchRequest(
            industry=target_industry,
            query=query,
            max_leads=max_leads,
        )

        state = PipelineState(request=request)

        try:
            # --------------------------------------------------
            # 1. RESEARCH (batch-level — no per-lead concept yet)
            # --------------------------------------------------
            state.current_stage = "research"

            state.leads = await self.research_service.research(
                industry=request.industry,
                query=request.query,
            )
            state.leads = state.leads[: request.max_leads]

            # --------------------------------------------------
            # 2. ENRICHMENT
            # --------------------------------------------------
            state.current_stage = "enrichment"
            state.leads = await self._run_stage(
                state.leads, "enrichment", self.enrichment_service.enrich, state
            )

            # --------------------------------------------------
            # 3. QUALIFICATION
            # --------------------------------------------------
            state.current_stage = "qualification"
            state.leads = await self._run_stage(
                state.leads, "qualification", self.qualification_service.qualify, state
            )

            # --------------------------------------------------
            # 4. PERSONALIZATION — gated by qualification score
            # --------------------------------------------------
            state.current_stage = "personalization"

            async def _personalize_if_qualified(lead: Lead) -> Lead:
                if (
                    lead.status == LeadStatus.QUALIFIED
                    and lead.qualification_score is not None
                    and lead.qualification_score >= QUALIFICATION_THRESHOLD
                ):
                    return await self.personalization_service.personalize(lead)
                return lead

            state.leads = await self._run_stage(
                state.leads, "personalization", _personalize_if_qualified, state
            )

            # --------------------------------------------------
            # 5. OUTREACH — only leads that actually got a message
            # --------------------------------------------------
            state.current_stage = "outreach"

            async def _send_if_personalized(lead: Lead) -> Lead:
                if lead.status == LeadStatus.PERSONALIZED and lead.personalized_message:
                    return await self.outreach_service.send(lead)
                return lead

            state.leads = await self._run_stage(
                state.leads, "outreach", _send_if_personalized, state
            )

            state.current_stage = "completed"
            state.completed = True

        except Exception as exc:
            # Catches batch-level failures — research itself throwing,
            # or an AuthenticationError re-raised out of _run_stage.
            state.errors.append(
                f"Pipeline failed during '{state.current_stage}': {exc}"
            )
            state.completed = False

        return {
            "status": "completed" if state.completed else "failed",
            "industry": request.industry,
            "query": request.query,
            "current_stage": state.current_stage,
            "leads_processed": len(state.leads),
            "leads_failed": sum(1 for l in state.leads if l.status == LeadStatus.FAILED),
            "leads": [lead.model_dump(mode="json") for lead in state.leads],
            "errors": state.errors,
        }
