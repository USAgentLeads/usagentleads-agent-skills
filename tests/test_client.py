import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock

spec = importlib.util.spec_from_file_location("client", Path(__file__).parents[1] / "skills/usagentleads/scripts/client.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
KEY = "aa80a81a-f7c1-4c45-8b70-64c25e7143d2"

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = module.Client(api_key="synthetic-key")
        self.client.opener = MagicMock()
        self.client.opener.open.return_value.__enter__.return_value.read.return_value = b'{"records":[]}'

    def test_search_requires_approval_and_valid_budget_before_network(self):
        for kwargs in ({}, {"confirmed": True, "idempotency_key": "invalid"},
                       {"confirmed": True, "idempotency_key": KEY}):
            with self.assertRaises(ValueError):
                self.client.request("agents/search", data={"max_credits": True}, **kwargs)
        self.client.opener.open.assert_not_called()

    def test_lookup_uses_saved_header_and_zero_budget(self):
        payload = {"ids": ["synthetic-record"], "max_credits": 0}
        self.client.lookup("brokerages", payload, idempotency_key=KEY, confirmed=True)
        request = self.client.opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://www.usagentleads.com/api/v3/brokerages/lookup")
        self.assertEqual(request.get_header("Idempotency-key"), KEY)
        self.assertEqual(json.loads(request.data), payload)
        self.assertNotIn("synthetic-key", request.full_url)

    def test_rejects_removed_paths_and_path_injection(self):
        for path in ("records/unlock", "records", "credits", "search/count", "exports/../account"):
            with self.assertRaises(ValueError):
                self.client.request(path)
        self.client.opener.open.assert_not_called()

    def test_discovery_recovery_and_cancellation_methods(self):
        for path, method in (("agents/count", "POST"), ("requests/" + KEY, "GET"), ("exports/" + KEY + "/cancel", "POST")):
            self.client.request(path)
            self.assertEqual(self.client.opener.open.call_args.args[0].method, method)

    def test_export_also_requires_explicit_approval(self):
        with self.assertRaises(ValueError):
            self.client.create_export({"kind": "agents", "max_credits": 0}, idempotency_key=KEY)
        self.client.opener.open.assert_not_called()

    def test_rejects_credentials_in_query_and_redirects(self):
        with self.assertRaises(ValueError):
            self.client.request("locations", query={"key": "synthetic-key"})
        self.assertIsNone(module.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.test"))
        self.client.opener.open.assert_not_called()

if __name__ == "__main__":
    unittest.main()
