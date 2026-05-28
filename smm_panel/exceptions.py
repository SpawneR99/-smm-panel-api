"""Exceptions raised by the SMM panel client."""


class SMMPanelError(Exception):
    """Base error for transport, decoding, or usage problems."""


class SMMPanelAPIError(SMMPanelError):
    """Raised when the panel responds with an ``{"error": ...}`` payload."""

    def __init__(self, message: str, *, action: str | None = None):
        super().__init__(message)
        self.action = action
