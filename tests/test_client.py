import json
import unittest
from unittest.mock import MagicMock

from smm_panel import SMMPanelAPIError, SMMPanelClient, SMMPanelError


def _response(payload, status_code=200, json_ok=True):
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    if json_ok:
        resp.json.return_value = payload
    else:
        resp.json.side_effect = ValueError("no json")
    return resp


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.client = SMMPanelClient(
            api_key="KEY", api_url="https://example.com/api/v2", session=self.session
        )

    def _last_call_data(self):
        return self.session.post.call_args.kwargs["data"]

    def test_requires_api_key(self):
        with self.assertRaises(ValueError):
            SMMPanelClient(api_key="")

    def test_balance_sends_key_and_action(self):
        self.session.post.return_value = _response({"balance": "100.5", "currency": "USD"})
        result = self.client.balance()
        self.assertEqual(result["balance"], "100.5")
        data = self._last_call_data()
        self.assertEqual(data["key"], "KEY")
        self.assertEqual(data["action"], "balance")

    def test_add_order_omits_none_params(self):
        self.session.post.return_value = _response({"order": 99})
        order = self.client.add_order(service=1, link="http://x", quantity=500)
        self.assertEqual(order["order"], 99)
        data = self._last_call_data()
        self.assertEqual(data["action"], "add")
        self.assertEqual(data["service"], 1)
        self.assertEqual(data["quantity"], 500)
        self.assertNotIn("runs", data)
        self.assertNotIn("comments", data)

    def test_add_order_passes_extra_fields(self):
        self.session.post.return_value = _response({"order": 1})
        self.client.add_order(service=1, link="http://x", quantity=10, username="me")
        self.assertEqual(self._last_call_data()["username"], "me")

    def test_multi_status_joins_ids(self):
        self.session.post.return_value = _response({})
        self.client.multi_status([101, 102, 103])
        self.assertEqual(self._last_call_data()["orders"], "101,102,103")

    def test_multi_status_accepts_string(self):
        self.session.post.return_value = _response({})
        self.client.multi_status("1,2")
        self.assertEqual(self._last_call_data()["orders"], "1,2")

    def test_api_error_payload_raises(self):
        self.session.post.return_value = _response({"error": "Incorrect request"})
        with self.assertRaises(SMMPanelAPIError) as ctx:
            self.client.services()
        self.assertEqual(ctx.exception.action, "services")

    def test_non_json_raises(self):
        self.session.post.return_value = _response(None, json_ok=False)
        with self.assertRaises(SMMPanelError):
            self.client.balance()


if __name__ == "__main__":
    unittest.main()
