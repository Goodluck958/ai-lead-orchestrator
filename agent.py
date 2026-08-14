import os
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

# ------------------------------------------------------------------
# 1. State Contract (FROZEN)
# ------------------------------------------------------------------
class AgentState(BaseModel):
    target_industry: str
    query: str
    raw_findings: List[str] = []
    final_summary: str = ""

# ------------------------------------------------------------------
# 2. Abstract Interfaces (Contracts)
# ------------------------------------------------------------------
class BaseResearchService(ABC):
    @abstractmethod
    async def execute(self, industry: str, query: str) -> List[str]:
        pass

class BaseSynthesisService(ABC):
    @abstractmethod
    async def execute(self, industry: str, query: str, raw_findings: List[str]) -> str:
        pass

# ------------------------------------------------------------------
# 3. Implementations: Research Layer
# ------------------------------------------------------------------
class MockResearchService(BaseResearchService):
    """Deterministic Research Service for testing & development."""
    async def execute(self, industry: str, query: str) -> List[str]:
        await asyncio.sleep(1.5)  # Simulated latency
        return [
            f"Identified top growth pain points in {industry}.",
            f"Extracted key executive outreach targets for query: '{query}'.",
            "Discovered high-intent automation opportunities across workflow logs."
        ]

# ------------------------------------------------------------------
# 4. Implementations: Synthesis Layer
# ------------------------------------------------------------------
class MockSynthesisService(BaseSynthesisService):
    """Deterministic Synthesis Service for testing & fallback."""
    async def execute(self, industry: str, query: str, raw_findings: List[str]) -> str:
        await asyncio.sleep(1.0)
        findings_text = "\n- ".join(raw_findings)
        return (
            f"### Business Intelligence Brief for {industry.upper()}\n"
            f"**Target Focus:** {query}\n\n"
            f"**Key Automated Insights (MOCK):**\n- {findings_text}\n\n"
            f"**Recommended Action Plan:** Deploy custom automated API workflows to target leads immediately."
        )

class OpenAISynthesisService(BaseSynthesisService):
    """Production Synthesis Service powered by OpenAI & LangChain."""
    def __init__(self, api_key: str = None, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model_name = model_name

    async def execute(self, industry: str, query: str, raw_findings: List[str]) -> str:
        # Graceful fallback if no API key is set
        if not self.api_key:
            return await MockSynthesisService().execute(industry, query, raw_findings)
        
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatOpenAI(api_key=self.api_key, model=self.model_name, temperature=0.2)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an elite Business Intelligence & Strategy Agent. Synthesize raw research findings into a crisp, highly actionable executive intelligence brief."),
            ("user", "Target Industry: {industry}\nSearch Query: {query}\n\nRaw Research Findings:\n{findings}\n\nProvide a structured summary with Key Insights and an Actionable Strategy.")
        ])
        
        chain = prompt | llm
        response = await chain.ainvoke({
            "industry": industry,
            "query": query,
            "findings": "\n- ".join(raw_findings)
        })
        return str(response.content)

# ------------------------------------------------------------------
# 5. Orchestrator (Dependency Injection)
# ------------------------------------------------------------------
class OrchestratorAgent:
    def __init__(
        self, 
        research_service: BaseResearchService = None, 
        synthesis_service: BaseSynthesisService = None
    ):
        # Defaulting to Mock Research + Hybrid/Real Synthesis
        self.research_service = research_service or MockResearchService()
        self.synthesis_service = synthesis_service or OpenAISynthesisService()

    async def run_pipeline(self, target_industry: str, query: str) -> Dict[str, Any]:
        """Executes non-blocking workflow through injected abstractions."""
        state = AgentState(target_industry=target_industry, query=query)
        
        # Step 1: Research
        state.raw_findings = await self.research_service.execute(
            state.target_industry, 
            state.query
        )
        
        # Step 2: Synthesis
        state.final_summary = await self.synthesis_service.execute(
            state.target_industry, 
            state.query, 
            state.raw_findings
        )
        
        # Contract-preserved response schema
        return {
            "status": "completed",
            "industry": state.target_industry,
            "brief": state.final_summary,
            "data_points_collected": len(state.raw_findings)
    }
    
