from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseResearchService(ABC):
    """
    Contract for lead research providers.

    Any research implementation—mock, Tavily, or another
    provider—must satisfy this interface.
    """

    @abstractmethod
    async def research(
        self,
        industry: str,
        query: str,
    ) -> List[Dict[str, Any]]:
        """Research potential leads."""
        raise NotImplementedError


class BaseEnrichmentService(ABC):
    """
    Contract for lead enrichment providers.

    Implementations can enrich a lead with company, contact,
    website, or other publicly available business information.
    """

    @abstractmethod
    async def enrich(
        self,
        lead: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Enrich a single lead."""
        raise NotImplementedError


class BaseQualificationService(ABC):
    """
    Contract for lead qualification.

    Implementations determine how suitable a lead is for
    the client's target criteria.
    """

    @abstractmethod
    async def qualify(
        self,
        lead: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Score and qualify a lead."""
        raise NotImplementedError


class BasePersonalizationService(ABC):
    """
    Contract for AI-powered personalization.

    Implementations generate a personalized outreach message
    using the qualified lead's information.
    """

    @abstractmethod
    async def personalize(
        self,
        lead: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate personalized outreach content."""
        raise NotImplementedError


class BaseOutreachService(ABC):
    """
    Contract for outreach providers.

    Implementations can send or queue approved messages through
    an external communication provider.
    """

    @abstractmethod
    async def send(
        self,
        lead: Dict[str, Any],
        message: str,
    ) -> Dict[str, Any]:
        """Send or queue an outreach message."""
        raise NotImplementedError
