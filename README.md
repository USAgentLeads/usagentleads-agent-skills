# usagentleads-agent-skills

Official USAgentLeads developer resources. Documentation: https://www.usagentleads.com/docs.

API v3 and hosted MCP are available to Growth and Pro accounts. Never commit an API key or real contact data. Use synthetic records in examples and tests.

Count and previews spend no record credits. Search and lookup return contacts directly and spend one credit per new agent or two per new brokerage. Existing ownership is free. Reuse the same UUID request key and payload after a timeout; recover the prior outcome before starting another request.

Licensed under MIT. This license covers client code and documentation, not the licensed contact dataset.

## Install

Use your skill installer with `https://github.com/USAgentLeads/usagentleads-agent-skills` and path `skills/usagentleads`, or copy that directory into your agent's skills directory. Invoke `$usagentleads` for a targeted workflow.

The skill includes a zero-dependency Python client. Set `USAGENTLEADS_API_KEY` outside source control.
