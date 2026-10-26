# usagentleads-agent-skills

Official USAgentLeads developer resources. Documentation: https://www.usagentleads.com/docs.

**Release status:** API v2 and hosted MCP are implemented for the next application release. The application deployment is intentionally pending UI review. Public documentation and clients do not imply that those endpoints are already live. Existing one-time purchases and legacy v1 access continue unchanged.

Never commit an API key or real contact data. Use synthetic records in examples and tests. API access requires Growth (read) or Pro (read, unlock, MCP). Legacy Pro API retains v1 access and gains v2 read access.

Search and masked previews spend no record credits. One agent unlock costs one credit; a brokerage costs two. Unlocks share the dashboard balance. Reuse the same UUID idempotency key and identical payload after a timeout. Do not create another key until the prior outcome is resolved.

Licensed under MIT. This license covers client code and documentation, not the licensed contact dataset.

## Install

Use your skill installer with `https://github.com/USAgentLeads/usagentleads-agent-skills` and path `skills/usagentleads`, or copy that directory into your agent's skills directory. Invoke `$usagentleads` for a targeted workflow.

The skill includes a zero-dependency Python client. Set `USAGENTLEADS_API_KEY` outside source control.
