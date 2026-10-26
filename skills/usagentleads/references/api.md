# API contract

Set `USAGENTLEADS_API_KEY` in the environment. Read requests require Growth or Pro; unlock and hosted MCP require Pro. Legacy Pro API preserves v1 and supports v2 read access.

- `GET /coverage`: public aggregate coverage and release identifier.
- `POST /search/count` and `POST /search/preview`: `{ "kind": "agents", "filters": { "state": "CA", "mustHave": ["email"] } }`.
- `GET /credits`: shared balance and plan.
- `GET /records?kind=agents&page=1&pageSize=25`: owned contacts; sizes 25, 50, 100.
- `POST /records/unlock`: kind, releaseId, maxCredits, UUID idempotencyKey, and either ordinals (1–100) or filters plus quantity (1–5000).
- `GET /exports?kind=agents&template=hubspot`: authenticated CSV with suppression and attribution.

Supported filters: state, countyFips, city (requires state), zip, mustHave (email/phone/address/license), activeLicense, organization, orgType. Never imply support for production volume or live license verification.

On 400 correct the request; on 401 replace/revoke invalid credentials; on 402 stop for insufficient credits; on 403 check the plan; on 409 re-preview if the release changed, but keep an ambiguous existing unlock request unchanged; on 429 wait at least the Retry-After interval. On a timeout or 5xx, preserve the unlock key and request exactly. Do not retry spending with a fresh key.

Full reference: https://www.usagentleads.com/docs
