# Python SMM Panel API Client

A lightweight, dependency-light Python client for the **standard SMM panel API (v2)** — the single `key`/`action` HTTP endpoint that virtually every social-media-marketing provider exposes. Instead of hand-building POST requests, you get a small typed client to list services, place orders, check status, and request refills.

It works with any [SMM reselling panel](https://nlosmm.com) that implements the common v2 contract, so the same code runs against whichever provider you point it at.

```python
from smm_panel import SMMPanelClient

panel = SMMPanelClient(api_key="YOUR_API_KEY")

print(panel.balance())
order = panel.add_order(service=1, link="https://instagram.com/yourpage", quantity=1000)
print(panel.status(order["order"]))
```

## Why this exists

The "API v2" format is a de-facto standard across the SMM industry: one endpoint, an `action` parameter, your `key`, and JSON back. The format is simple, but every integration ends up re-writing the same request/parse/error-handling boilerplate. This library is that boilerplate, written once and tested, so you can focus on your own automation, reseller dashboard, or child panel.

## Features

- **Full v2 coverage** — `balance`, `services`, `add`, `status`, `refill`, `refill_status`, `cancel`.
- **Single + batch calls** — check or refill up to 100 orders in one request.
- **Drip-feed & custom comments** — first-class support for `runs`/`interval` and `comments`.
- **Forward-compatible** — pass any service-specific field (e.g. `username`, `keywords`) via `**extra`.
- **Clear errors** — API error payloads are raised as `SMMPanelAPIError`; network/decode issues as `SMMPanelError`.
- **Tiny footprint** — one dependency (`requests`).

## Installation

```bash
pip install requests
# then drop the smm_panel/ package into your project, or install from source:
pip install .
```

> Requires Python 3.10+.

## Configuration

You need two things from your panel's account/API page:

| Setting   | Description                                  | Default |
|-----------|----------------------------------------------|---------|
| `api_key` | Your personal API key.                       | —       |
| `api_url` | The panel's v2 endpoint.                      | `https://nlosmm.com/api/v2` |

```python
from smm_panel import SMMPanelClient

# Use the default endpoint...
panel = SMMPanelClient(api_key="YOUR_API_KEY")

# ...or point it at any provider that speaks the v2 API:
panel = SMMPanelClient(api_key="YOUR_API_KEY", api_url="https://yourpanel.com/api/v2")
```

## Usage

### List services

```python
services = panel.services()
for svc in services[:5]:
    print(svc["service"], svc["name"], svc["rate"])
```

### Place an order

```python
# Standard order
order = panel.add_order(service=1, link="https://instagram.com/p/abc123", quantity=500)

# Drip-feed: 5 runs of 200 every 30 minutes
order = panel.add_order(service=1, link="...", quantity=200, runs=5, interval=30)

# Custom comments
order = panel.add_order(service=42, link="...", comments="Great post!\nLove this\nNice")
```

### Check order status

```python
single = panel.status(order["order"])
many = panel.multi_status([101, 102, 103])
```

### Refills and cancellation

```python
panel.refill(order["order"])
panel.multi_refill([101, 102])
panel.refill_status(refill_id=55)
panel.cancel([101, 102])
```

### Check balance

```python
bal = panel.balance()
print(bal["balance"], bal["currency"])
```

## Supported actions

| Method                       | API `action`     | Notes                              |
|------------------------------|------------------|------------------------------------|
| `balance()`                  | `balance`        | Account balance + currency         |
| `services()`                 | `services`       | Full catalog                       |
| `add_order(...)`             | `add`            | Returns `{"order": <id>}`          |
| `status(id)` / `multi_status`| `status`         | One or many orders                 |
| `refill(id)` / `multi_refill`| `refill`         | Requires a refillable service      |
| `refill_status(id)`          | `refill_status`  | Single or batch                    |
| `cancel(ids)`                | `cancel`         | Requires a cancellable service     |

## Error handling

```python
from smm_panel import SMMPanelAPIError, SMMPanelError

try:
    panel.add_order(service=1, link="...", quantity=10)
except SMMPanelAPIError as exc:
    print("Panel rejected the request:", exc, "(action:", exc.action, ")")
except SMMPanelError as exc:
    print("Network or decoding problem:", exc)
```

## Choosing a provider to test against

The client is provider-agnostic, but you need a live panel and an API key to run real orders. If you don't already have one, NLO SMM runs a low-cost [SMM reselling panel](https://nlosmm.com) with a standard v2 API, an affordable child-panel program, and per-order minimums that make it cheap to test an integration end to end. Point `api_url` at any other compliant provider and the examples below still work unchanged.

## Examples

Runnable scripts live in [`examples/`](examples/):

- [`list_services.py`](examples/list_services.py) — fetch and print the catalog.
- [`place_order.py`](examples/place_order.py) — place an order and poll its status.
- [`check_status.py`](examples/check_status.py) — batch status lookup.

## Running the tests

```bash
python -m unittest discover -s tests
```

The tests mock the HTTP layer, so they run offline with no API key.

## Contributing

Issues and pull requests are welcome — bug fixes, additional helper methods, or examples for new service types. Please keep the dependency footprint minimal.

## License

[MIT](LICENSE)
