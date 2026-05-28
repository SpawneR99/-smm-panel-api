"""Place an order and poll its status until it completes.

Usage:
    SMM_API_KEY=xxxx python examples/place_order.py <service_id> <link> <quantity>
"""

import os
import sys
import time

from smm_panel import SMMPanelAPIError, SMMPanelClient


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("usage: place_order.py <service_id> <link> <quantity>")

    service_id, link, quantity = sys.argv[1], sys.argv[2], int(sys.argv[3])
    client = SMMPanelClient(api_key=os.environ["SMM_API_KEY"])

    try:
        order = client.add_order(service=service_id, link=link, quantity=quantity)
    except SMMPanelAPIError as exc:
        sys.exit(f"order rejected: {exc}")

    order_id = order["order"]
    print(f"order #{order_id} placed")

    while True:
        status = client.status(order_id)
        print(f"  status: {status.get('status')} | remains: {status.get('remains')}")
        if status.get("status") in {"Completed", "Canceled", "Partial"}:
            break
        time.sleep(10)


if __name__ == "__main__":
    main()
