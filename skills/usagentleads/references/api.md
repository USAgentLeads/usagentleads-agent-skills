# API contract

API v3 base: https://www.usagentleads.com/api/v3. Growth and Pro support direct REST v3 and MCP access.

For both agents and brokerages:
- POST /{kind}/count and /{kind}/preview: free discovery.
- POST /{kind}/search: filters, limit (1–100), optional cursor/exclude_owned/snapshot_id, max_credits. Returns available contact fields directly.
- POST /{kind}/lookup: IDs (up to 100), optional snapshot_id, max_credits. IDs may be previously unowned.

Billable calls require a saved UUID Idempotency-Key header. New agents cost one credit and brokerages two; prior ownership across dashboard/REST/MCP is free. Never change the key or payload after an ambiguous timeout. GET /requests/{key} recovers the saved result for 30 days. A replay reports the original historical charge without charging again.

GET /coverage and /locations are public. GET /account and /usage require an API key. POST /exports queues up to 5,000 records by IDs or filters; GET /exports/{id}, GET /exports/{id}/download and POST /exports/{id}/cancel manage delivery. Queued jobs hold no credits; preparation checks the balance/cap and atomically saves data and charges. Failed/cancelled jobs acquire nothing.

Filters match the dashboard: state, countyFips, city (requires state), zip, mustHave (email/phone/address/license/fullAddress), organization; activeLicense for agents and orgType for brokerages. No sales-volume, fuzzy-name or live-license enrichment is supported.

All operations are rate-limited. Authenticated REST v2/v3 and hosted MCP share 60 requests/minute/account. Growth has 10k and Pro 100k successful/in-flight requests per UTC month. On 429 respect Retry-After. Five concurrent v3 searches; five export creation requests/minute and two queued exports/account.

Suppressions apply before acquisition and again on recovery/download. Keep location_source attribution. Format checks do not guarantee reachability, deliverability, mobile status or permission to contact.

The bundled Python client remains a legacy v2 helper. For v3 use the REST examples or updated MCP bridge. Legacy v2 unlock stays Pro-only; its workflow is documented separately.
