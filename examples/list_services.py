"""Fetch and print the first services from the panel catalog.

Usage:
    SMM_API_KEY=xxxx python examples/list_services.py
"""

import os

from smm_panel import SMMPanelClient


def main() -> None:
    client = SMMPanelClient(api_key=os.environ["SMM_API_KEY"])
    services = client.services()
    print(f"{len(services)} services available\n")
    for svc in services[:10]:
        print(f"[{svc['service']}] {svc['name']} — rate {svc['rate']} "
              f"(min {svc['min']}, max {svc['max']})")


if __name__ == "__main__":
    main()
