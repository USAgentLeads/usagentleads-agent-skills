"""Standard-library USAgentLeads API client. Never logs credentials or follows redirects."""
import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse, urlencode

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class Client:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ.get("USAGENTLEADS_API_KEY")
        self.base_url = (base_url or os.environ.get("USAGENTLEADS_BASE_URL") or "https://www.usagentleads.com").rstrip("/")
        url = urlparse(self.base_url)
        if url.username or url.password or url.query or url.fragment or url.path not in ("", "/"):
            raise ValueError("Use an origin without credentials, path, query, or fragment")
        if url.scheme != "https" and not (url.scheme == "http" and url.hostname in ("localhost", "127.0.0.1")):
            raise ValueError("HTTPS is required except for local testing")
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, path, data=None, query=None, raw=False):
        if path not in ("coverage", "search/count", "search/preview", "records/unlock", "records", "credits", "exports"):
            raise ValueError("Unknown API endpoint")
        if path != "coverage" and not self.api_key:
            raise ValueError("Set USAGENTLEADS_API_KEY")
        url = self.base_url + "/api/v2/" + path
        if query: url += "?" + urlencode(query)
        headers = {"Accept": "text/csv" if raw else "application/json"}
        if self.api_key: headers["Authorization"] = "Bearer " + self.api_key
        if data is not None: headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, headers=headers)
        with self.opener.open(req, timeout=60) as response:
            content = response.read()
            return content if raw else json.loads(content)

    def unlock(self, payload, confirmed=False):
        if confirmed is not True: raise ValueError("Confirm the selection and maximum spend before unlocking")
        if not payload.get("idempotencyKey") or not isinstance(payload.get("maxCredits"), int) or payload["maxCredits"] < 1:
            raise ValueError("Provide a UUID idempotencyKey and positive maxCredits")
        return self.request("records/unlock", data=payload)
