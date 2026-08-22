from abc import ABC, abstractmethod
from typing import List

from .models import Lead


class BaseResearchService(ABC):
    """
    Contract for lead research providers.

    Every research implementation must return validated
    LEADFORGE Lead objects.
    """

    @abstractmethod
    async def research(
        self,
        industry: str,
        query: str,
    ) -> List[Lead]:
        """Discover potential leads."""
        raise NotImplementedError


class BaseEnrichmentService(ABC):
    """
    Contract for lead enrichment providers.
    """

    @abstractmethod
    async def enrich(self, lead: Lead) -> Lead:
        """Enrich an existing lead."""
        raise NotImplementedError


class BaseQualificationService(ABC):
    """
    Contract for lead qualification providers.
    """

    @abstractmethod
    async def qualify(self, lead: Lead) -> Lead:
        """Score and qualify an existing lead."""
        raise NotImplementedError


class BasePersonalizationService(ABC):
    """
    Contract for personalization providers.
    """

    @abstractmethod
    async def personalize(self, lead: Lead) -> Lead:
        """Generate personalized outreach content."""
        raise NotImplementedError


class BaseOutreachService(ABC):
    """
    Contract for outreach providers.
    """

    @abstractmethod
    async def send(self, lead: Lead) -> Lead:
        """Send or queue an outreach message."""
        raise NotImplementedError
