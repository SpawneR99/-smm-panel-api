"""A thin, dependency-light client for the common SMM panel API (v2).

Almost every SMM panel exposes the same HTTP endpoint: a single URL that
accepts an ``action`` plus your API ``key`` as form fields and replies with
JSON. This module wraps that contract so you can place and track orders from
Python instead of hand-building POST requests.
"""

from __future__ import annotations

from typing import Any, Iterable

import requests

from .exceptions import SMMPanelAPIError, SMMPanelError

#: Default endpoint. NLO SMM exposes the standard v2 API at this URL.
DEFAULT_API_URL = "https://nlosmm.com/api/v2"


class SMMPanelClient:
    """Client for an SMM panel that implements the standard v2 API.

    Args:
        api_key: Your panel API key (found in the panel's account/API page).
        api_url: The panel's API endpoint. Defaults to NLO SMM's endpoint,
            but any provider using the same ``key``/``action`` contract works.
        session: An optional pre-configured :class:`requests.Session`.
        timeout: Per-request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        api_url: str = DEFAULT_API_URL,
        *,
        session: requests.Session | None = None,
        timeout: float = 30,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    # -- transport ---------------------------------------------------------

    def _post(self, action: str, **params: Any) -> Any:
        payload = {"key": self.api_key, "action": action}
        payload.update({k: v for k, v in params.items() if v is not None})

        try:
            response = self._session.post(
                self.api_url, data=payload, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SMMPanelError(f"request to {self.api_url} failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise SMMPanelError("panel returned a non-JSON response") from exc

        if isinstance(data, dict) and data.get("error"):
            raise SMMPanelAPIError(str(data["error"]), action=action)
        return data

    # -- account -----------------------------------------------------------

    def balance(self) -> dict:
        """Return the account balance and currency."""
        return self._post("balance")

    # -- catalog -----------------------------------------------------------

    def services(self) -> list:
        """Return the full service list (id, name, type, rate, min, max)."""
        return self._post("services")

    # -- orders ------------------------------------------------------------

    def add_order(
        self,
        service: int | str,
        link: str,
        quantity: int | None = None,
        *,
        runs: int | None = None,
        interval: int | None = None,
        comments: str | None = None,
        **extra: Any,
    ) -> dict:
        """Create an order.

        ``quantity`` is required for most service types. Drip-feed orders use
        ``runs`` + ``interval``; custom-comment services use ``comments``.
        Any other service-specific field (e.g. ``username``, ``keywords``)
        can be passed via ``**extra``.
        """
        return self._post(
            "add",
            service=service,
            link=link,
            quantity=quantity,
            runs=runs,
            interval=interval,
            comments=comments,
            **extra,
        )

    def status(self, order_id: int | str) -> dict:
        """Return the status of a single order."""
        return self._post("status", order=order_id)

    def multi_status(self, order_ids: Iterable[int | str] | str) -> dict:
        """Return the status of up to 100 orders in one call."""
        return self._post("status", orders=_join_ids(order_ids))

    # -- refills -----------------------------------------------------------

    def refill(self, order_id: int | str) -> Any:
        """Request a refill for a single order."""
        return self._post("refill", order=order_id)

    def multi_refill(self, order_ids: Iterable[int | str] | str) -> Any:
        """Request refills for multiple orders at once."""
        return self._post("refill", orders=_join_ids(order_ids))

    def refill_status(self, refill_id: int | str) -> Any:
        """Return the status of a single refill."""
        return self._post("refill_status", refill=refill_id)

    def multi_refill_status(self, refill_ids: Iterable[int | str] | str) -> Any:
        """Return the status of multiple refills at once."""
        return self._post("refill_status", refills=_join_ids(refill_ids))

    # -- cancel ------------------------------------------------------------

    def cancel(self, order_ids: Iterable[int | str] | str) -> Any:
        """Request cancellation for one or more orders."""
        return self._post("cancel", orders=_join_ids(order_ids))


def _join_ids(ids: Iterable[int | str] | str) -> str:
    if isinstance(ids, str):
        return ids
    return ",".join(str(i) for i in ids)
