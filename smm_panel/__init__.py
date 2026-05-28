"""Python client for the standard SMM panel HTTP API (API v2)."""

from .client import DEFAULT_API_URL, SMMPanelClient
from .exceptions import SMMPanelAPIError, SMMPanelError

__all__ = [
    "SMMPanelClient",
    "DEFAULT_API_URL",
    "SMMPanelError",
    "SMMPanelAPIError",
]

__version__ = "0.1.0"
