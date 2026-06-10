class PaperResearchError(Exception):
    """Base error for the paper-research-agent package."""


class ProviderError(PaperResearchError):
    """A paper provider failed to fetch results."""

    def __init__(self, provider: str, message: str) -> None:
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class RateLimitError(ProviderError):
    """A provider rejected the request due to rate limiting."""
