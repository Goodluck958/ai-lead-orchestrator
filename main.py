import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import OrchestratorAgent, OpenAISynthesisService, MockResearchService

app = FastAPI(
    title="Autonomous Multi-Agent Business Intelligence Engine",
    version="1.0.0",
    description="Production API driving autonomous multi-agent lead research and workflow synthesis."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inject intermediate architecture: Mock Research + Real Synthesis Provider
agent_system = OrchestratorAgent(
    research_service=MockResearchService(),
    synthesis_service=OpenAISynthesisService()
)

class ResearchRequest(BaseModel):
    industry: str
    query: str

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "Multi-Agent Intelligence Engine",
        "architecture_stage": "Phase 3: Hybrid Mock-Research / Real-Synthesis",
        "docs": "/docs"
    }

@app.post("/api/v1/run-agent")
async def execute_agent(payload: ResearchRequest):
    if not payload.industry or not payload.query:
        raise HTTPException(status_code=400, detail="Industry and Query parameters are required.")
    
    try:
        result = await agent_system.run_pipeline(
            target_industry=payload.industry, 
            query=payload.query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
