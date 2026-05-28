# Python SMM Panel API Client

A lightweight, dependency-light Python client for the **NLO SMM panel API (v2)**, built to the official specification at **[nlosmm.com/api](https://nlosmm.com/api)**. It wraps the single `key`/`action` HTTP endpoint so you can list services, place orders, check status, and request refills from Python instead of hand-building POST requests.

The same v2 contract is used by most providers, so this client works with any [SMM reselling panel](https://nlosmm.com) that follows it — just point `api_url` at your provider.

## Getting an API key

The API requires an account. To use this client you must:

1. **Register at [nlosmm.com/signup](https://nlosmm.com/signup).**
2. Add funds to your balance (per-order minimums are low).
3. Open your account's **API** page and copy your **API key**.

Keep that key secret — anyone with it can spend your balance.

```python
from smm_panel import SMMPanelClient

panel = SMMPanelClient(api_key="YOUR_API_KEY")  # key from nlosmm.com

print(panel.balance())
order = panel.add_order(service=1, link="https://instagram.com/yourpage", quantity=1000)
print(panel.status(order["order"]))
```

## Why this exists

The "API v2" format is a de-facto standard across the SMM industry: one endpoint, an `action` parameter, your `key`, and JSON back. The format is simple, but every integration ends up re-writing the same request/parse/error-handling boilerplate. This library is that boilerplate, written once and tested, so you can focus on your own automation, reseller dashboard, or child panel.

## Features

- **Matches the official spec** at [nlosmm.com/api](https://nlosmm.com/api): `balance`, `services`, `add`, `status`, `refill`, `refill_status`.
- **All order types** — Default, Drip-feed (`runs`/`interval`), Custom Comments, Polls (`answer_number`), Subscriptions (`username`/`min`/`max`/`posts`/`delay`).
- **Single + batch status** — check up to 100 orders in one request.
- **Forward-compatible** — pass any extra service-specific field via `**extra`.
- **Clear errors** — API error payloads raise `SMMPanelAPIError`; network/decode issues raise `SMMPanelError`.
- **Tiny footprint** — one dependency (`requests`).

## Installation

```bash
pip install requests
# then drop the smm_panel/ package into your project, or install from source:
pip install .
```

> Requires Python 3.10+.

## Configuration

Two settings, both from your panel account:

| Setting   | Description                                  | Default |
|-----------|----------------------------------------------|---------|
| `api_key` | Your API key (from nlosmm.com → API page).   | —       |
| `api_url` | The panel's v2 endpoint.                      | `https://nlosmm.com/api/v2` |

```python
from smm_panel import SMMPanelClient

# Use the default NLO SMM endpoint...
panel = SMMPanelClient(api_key="YOUR_API_KEY")

# ...or point it at any provider that speaks the v2 API:
panel = SMMPanelClient(api_key="YOUR_API_KEY", api_url="https://yourpanel.com/api/v2")
```

## Usage

### List services

```python
services = panel.services()
for svc in services[:5]:
    print(svc["service"], svc["name"], svc["type"], svc["rate"], svc["refill"])
# {"service": 1, "name": "Followers", "type": "Default", "category": "...",
#  "rate": "0.90", "min": "50", "max": "10000", "refill": true}
```

### Place an order

```python
# Default order
order = panel.add_order(service=1, link="https://instagram.com/p/abc123", quantity=500)

# Drip-feed: 5 runs of 200 with 30 minutes between runs
order = panel.add_order(service=1, link="...", quantity=200, runs=5, interval=30)

# Custom comments (one per line)
order = panel.add_order(service=42, link="...", comments="Great post!\nLove this\nNice")

# Poll
order = panel.add_order(service=70, link="...", answer_number="1")

# Subscriptions
order = panel.add_order(service=80, link="...", username="target",
                        min=100, max=200, posts=5, delay=30)

print(order)  # {"order": 23501}
```

### Check order status

```python
single = panel.status(order["order"])
# {"charge": "0.27819", "start_count": "3572", "status": "Partial",
#  "remains": "157", "currency": "USD"}

many = panel.multi_status([101, 102, 103])
```

### Refills

```python
ref = panel.refill(order["order"])     # {"refill": "1"}
panel.refill_status(ref["refill"])     # {"status": "Completed"}
```

### Check balance

```python
bal = panel.balance()
print(bal["balance"], bal["currency"])  # 100.84292 USD
```

## Supported actions

| Method                         | API `action`     | Notes                              |
|--------------------------------|------------------|------------------------------------|
| `balance()`                    | `balance`        | Account balance + currency         |
| `services()`                   | `services`       | Full catalog                       |
| `add_order(...)`               | `add`            | Returns `{"order": <id>}`          |
| `status(id)` / `multi_status`  | `status`         | One or many orders                 |
| `refill(id)`                   | `refill`         | Refillable services only           |
| `refill_status(id)`            | `refill_status`  | Refill progress                    |

These mirror the actions documented at [nlosmm.com/api](https://nlosmm.com/api).

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

## About NLO SMM

This client targets NLO SMM, a low-cost [SMM reselling panel](https://nlosmm.com) with 3000+ services across Instagram, TikTok, YouTube, and more, a white-label child-panel program, and the standard v2 API documented above. Create your account and grab an API key at [nlosmm.com/signup](https://nlosmm.com/signup), then point this client at it.

## Examples

Runnable scripts live in [`examples/`](examples/):

- [`list_services.py`](examples/list_services.py) — fetch and print the catalog.
- [`place_order.py`](examples/place_order.py) — place an order and poll its status.
- [`check_status.py`](examples/check_status.py) — batch status lookup.

All read the key from the `SMM_API_KEY` environment variable:

```bash
SMM_API_KEY=your_key_here python examples/list_services.py
```

## Running the tests

```bash
python -m unittest discover -s tests
```

The tests mock the HTTP layer, so they run offline with no API key.

## Contributing

Issues and pull requests are welcome — bug fixes, additional helper methods, or examples for new service types. Please keep the dependency footprint minimal.

## License

[MIT](LICENSE)
