import os
from typing import List

import httpx

from ..contracts import BaseResearchService
from ..exceptions import AuthenticationError, RateLimitError, ResearchError
from ..models import Lead, LeadStatus

TAVILY_API_URL = "https://api.tavily.com/search"


class TavilyResearchService(BaseResearchService):
    """
    Real research provider backed by Tavily search.

    Tavily doesn't return structured "leads" natively — it returns
    web search results. This service turns those results into
    Lead objects with best-effort field extraction. Enrichment
    (later stage) is expected to fill in gaps.
    """

    def __init__(self, api_key: str | None = None, timeout: float = 15.0):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise AuthenticationError("TAVILY_API_KEY is not set.")
        self.timeout = timeout

    async def research(self, industry: str, query: str) -> List[Lead]:
        search_query = f"{query} {industry} company"

        payload = {
            "api_key": self.api_key,
            "query": search_query,
            "search_depth": "basic",
            "max_results": 20,
            "include_answer": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(TAVILY_API_URL, json=payload)
        except httpx.TimeoutException as exc:
            raise ResearchError(f"Tavily request timed out: {exc}") from exc
        except httpx.RequestError as exc:
            raise ResearchError(f"Tavily request failed: {exc}") from exc

        if response.status_code == 401:
            raise AuthenticationError("Tavily rejected the API key.")
        if response.status_code == 429:
            raise RateLimitError("Tavily rate limit hit.")
        if response.status_code >= 400:
            raise ResearchError(
                f"Tavily returned {response.status_code}: {response.text}"
            )

        data = response.json()
        results = data.get("results", [])

        leads: List[Lead] = []
        for idx, result in enumerate(results):
            title = result.get("title", "Unknown Company")
            url = result.get("url")

            leads.append(
                Lead(
                    id=f"tavily-{idx}-{hash(url) & 0xffffff:06x}",
                    company_name=title,
                    website=url,
                    industry=industry,
                    status=LeadStatus.DISCOVERED,
                )
            )

        return leads
