class LeadPipelineError(Exception):
    """Base class for all pipeline stage errors."""


class RetryableError(LeadPipelineError):
    """
    Signals a temporary failure — rate limits, timeouts, transient
    network issues. The lead should be retried later, not marked
    permanently FAILED.
    """


class RateLimitError(RetryableError):
    """Provider rate limit hit."""


class TimeoutError_(RetryableError):
    """Provider request timed out."""


class PermanentError(LeadPipelineError):
    """
    Signals a failure that will not resolve on retry — bad input,
    invalid data, business-rule violation. The lead should be
    marked FAILED.
    """


class AuthenticationError(PermanentError):
    """API key invalid/expired. Not lead-specific — should probably
    halt the batch rather than just failing one lead."""


class ValidationError(PermanentError):
    """Provider returned data that doesn't fit our contract."""


class ResearchError(LeadPipelineError):
    """Wrap-all for research stage failures."""


class EnrichmentError(LeadPipelineError):
    """Wrap-all for enrichment stage failures."""


class QualificationError(LeadPipelineError):
    """Wrap-all for qualification stage failures."""


class PersonalizationError(LeadPipelineError):
    """Wrap-all for personalization stage failures."""


class OutreachError(LeadPipelineError):
    """Wrap-all for outreach stage failures."""
