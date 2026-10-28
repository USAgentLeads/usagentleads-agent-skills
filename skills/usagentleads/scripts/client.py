"""Standard-library API v3 client with explicit spend approval and no redirects."""
import json
import os
import re
import urllib.request
from urllib.parse import urlparse, urlencode

UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}"

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

    def request(self, path, data=None, query=None, raw=False, *, idempotency_key=None, confirmed=False):
        audience = re.fullmatch(r"(agents|brokerages)/(count|preview|search|lookup)", path)
        export = re.fullmatch(r"exports/(" + UUID + r")(/download|/cancel)?", path)
        recovery = re.fullmatch(r"requests/" + UUID, path)
        if not (audience or export or recovery or path in ("coverage", "locations", "account", "usage", "exports")):
            raise ValueError("Unknown API endpoint")
        public = path in ("coverage", "locations")
        if not public and not self.api_key:
            raise ValueError("Set USAGENTLEADS_API_KEY")
        billable = path == "exports" or bool(audience and audience[2] in ("search", "lookup"))
        if billable:
            if confirmed is not True:
                raise ValueError("Confirm the selection and max_credits before spending")
            if not isinstance(idempotency_key, str) or not re.fullmatch(UUID, idempotency_key):
                raise ValueError("Provide a saved UUID idempotency_key")
            cap = data.get("max_credits") if isinstance(data, dict) else None
            if type(cap) is not int or not 0 <= cap <= (10000 if path == "exports" else 200):
                raise ValueError("Provide a valid max_credits cap")
        method = "POST" if audience or path == "exports" or (export and export[2] == "/cancel") else "GET"
        if method == "GET" and data is not None:
            raise ValueError("This endpoint does not accept a body")
        if query and (path != "locations" or set(query) - {"kind", "q", "state"}):
            raise ValueError("Only locations accepts kind, q and state query parameters")
        url = self.base_url + "/api/v3/" + path
        if query:
            url += "?" + urlencode(query)
        headers = {"Accept": "text/csv" if raw else "application/json"}
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        if billable:
            headers["Idempotency-Key"] = idempotency_key
        payload = None
        if method == "POST":
            headers["Content-Type"] = "application/json"
            payload = json.dumps(data if data is not None else {}).encode()
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        with self.opener.open(req, timeout=60) as response:
            content = response.read()
            return content if raw else json.loads(content)

    def search(self, kind, payload, *, idempotency_key, confirmed=False):
        return self.request(kind + "/search", data=payload, idempotency_key=idempotency_key, confirmed=confirmed)

    def lookup(self, kind, payload, *, idempotency_key, confirmed=False):
        return self.request(kind + "/lookup", data=payload, idempotency_key=idempotency_key, confirmed=confirmed)

    def create_export(self, payload, *, idempotency_key, confirmed=False):
        return self.request("exports", data=payload, idempotency_key=idempotency_key, confirmed=confirmed)
