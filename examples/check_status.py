"""Look up the status of several orders in a single batch call.

Usage:
    SMM_API_KEY=xxxx python examples/check_status.py 101 102 103
"""

import os
import sys

from smm_panel import SMMPanelClient


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: check_status.py <order_id> [<order_id> ...]")

    client = SMMPanelClient(api_key=os.environ["SMM_API_KEY"])
    result = client.multi_status(sys.argv[1:])
    for order_id, info in result.items():
        print(f"order #{order_id}: {info.get('status')} "
              f"(charge {info.get('charge')}, remains {info.get('remains')})")


if __name__ == "__main__":
    main()
