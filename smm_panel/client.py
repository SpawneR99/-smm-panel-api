"""A thin, dependency-light client for the NLO SMM panel API (v2).

It follows the official specification published at https://nlosmm.com/api:
a single HTTP endpoint that accepts your API ``key`` plus an ``action`` as
POST form fields and replies with JSON. The same contract is shared by most
SMM panels, so this client works against any v2-compatible provider.

You need an account and an API key first — register at
https://nlosmm.com/signup and copy the key from your account's API page.
"""

from __future__ import annotations

from typing import Any, Iterable

import requests

from .exceptions import SMMPanelAPIError, SMMPanelError

#: Official NLO SMM API endpoint (see https://nlosmm.com/api).
DEFAULT_API_URL = "https://nlosmm.com/api/v2"


class SMMPanelClient:
    """Client for the NLO SMM panel API v2 (https://nlosmm.com/api).

    Args:
        api_key: Your API key. Register at https://nlosmm.com/signup, then
            copy it from your account's API page.
        api_url: The panel's API endpoint. Defaults to NLO SMM's endpoint;
            any provider using the same ``key``/``action`` contract works.
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
            raise ValueError(
                "api_key is required — register at https://nlosmm.com/signup "
                "and copy your key from the account API page"
            )
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
        """Return the account ``balance`` and ``currency`` (action ``balance``)."""
        return self._post("balance")

    # -- catalog -----------------------------------------------------------

    def services(self) -> list:
        """Return the service list (action ``services``).

        Each item exposes ``service``, ``name``, ``type``, ``category``,
        ``rate``, ``min``, ``max`` and ``refill``.
        """
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
        answer_number: str | None = None,
        username: str | None = None,
        min: int | None = None,
        max: int | None = None,
        posts: int | None = None,
        delay: int | None = None,
        expiry: str | None = None,
        **extra: Any,
    ) -> dict:
        """Create an order (action ``add``). Returns ``{"order": <id>}``.

        The required fields depend on the service ``type`` (see
        https://nlosmm.com/api):

        - **Default**: ``service``, ``link``, ``quantity``.
        - **Drip-feed**: add ``runs`` and ``interval`` (minutes between runs).
        - **Custom Comments**: pass ``comments`` separated by ``\\n``.
        - **Poll**: pass ``answer_number``.
        - **Subscriptions**: pass ``username``, ``min``, ``max``, ``posts``,
          ``delay`` (0/5/10/15/30/60/90) and optionally ``expiry`` (``d/m/Y``).

        Any other service-specific field can be supplied via ``**extra``.
        """
        return self._post(
            "add",
            service=service,
            link=link,
            quantity=quantity,
            runs=runs,
            interval=interval,
            comments=comments,
            answer_number=answer_number,
            username=username,
            min=min,
            max=max,
            posts=posts,
            delay=delay,
            expiry=expiry,
            **extra,
        )

    def status(self, order_id: int | str) -> dict:
        """Return the status of a single order (action ``status``).

        Response includes ``charge``, ``start_count``, ``status``,
        ``remains`` and ``currency``.
        """
        return self._post("status", order=order_id)

    def multi_status(self, order_ids: Iterable[int | str] | str) -> dict:
        """Return the status of multiple orders in one call (action ``status``).

        Accepts an iterable of IDs or a comma-separated string and returns a
        mapping of order id -> status object.
        """
        return self._post("status", orders=_join_ids(order_ids))

    # -- refills -----------------------------------------------------------

    def refill(self, order_id: int | str) -> dict:
        """Request a refill for an order (action ``refill``).

        Returns ``{"refill": <id>}``. Only works on refillable services.
        """
        return self._post("refill", order=order_id)

    def refill_status(self, refill_id: int | str) -> dict:
        """Return the status of a refill (action ``refill_status``)."""
        return self._post("refill_status", refill=refill_id)


def _join_ids(ids: Iterable[int | str] | str) -> str:
    if isinstance(ids, str):
        return ids
    return ",".join(str(i) for i in ids)
