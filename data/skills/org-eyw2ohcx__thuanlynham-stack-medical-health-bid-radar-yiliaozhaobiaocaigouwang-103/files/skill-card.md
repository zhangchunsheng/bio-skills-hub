## Description:

This skill helps agents search and analyze medical and health procurement notices, with emphasis on purchasing hospitals, winning suppliers, supplier relationships, competitors, brands, prices, and procurement trends.

This skill is ready for commercial/non-commercial use.

## Publisher:

[thuanlynham-stack](https://clawhub.ai/user/thuanlynham-stack)

### License/Terms of Use:

MIT-0

## Use Case:

External procurement, sales, and market-analysis users use this skill to search Chinese medical and health tenders, identify purchasing hospitals and winning suppliers, compare vendors, and analyze procurement trends. It can also guide account setup and quota checks for the vendor API service.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill uses a third-party vendor API service and requires a ZLBX_API_KEY or a vendor-issued trial key.

Mitigation: Prefer setting a user-managed ZLBX_API_KEY before use, and review the vendor service and account terms before relying on the skill.

Risk: If no API key is configured, the artifact can guide consent-gated trial registration that sends platform, CPU architecture, and a SHA256 hash of a MAC address for deduplication.

Mitigation: Proceed with auto-registration only after explicit user consent; decline the flow and use the manual registration link when device-feature collection is not acceptable.

Risk: An automatically issued API key may be stored locally under ~/.zlbx/config.json.

Mitigation: Treat the local config file as sensitive, restrict access to the user account, and rotate or remove the key if the workspace is shared.

Risk: Aggregated group, supplier, and company analysis can be misleading when company names are ambiguous or matched across related entities.

Mitigation: Verify company identity, matched subsidiaries, and source bid records before making business decisions from the analysis.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/thuanlynham-stack/skills/medical-health-bid-radar-yiliaozhaobiaocaigouwang)
- [Publisher profile](https://clawhub.ai/user/thuanlynham-stack)
- [Skill instructions](artifact/SKILL.md)
- [Account setup reference](artifact/references/account-setup.md)
- [Account API reference](artifact/references/api-account.md)
- [Bid search API reference](artifact/references/api-search.md)
- [Company analysis API reference](artifact/references/api-company.md)
- [Market analysis API reference](artifact/references/api-market.md)
- [Vendor API service](https://mcp-server.zhiliaobiaoxun.com/api_v2/{tool})
- [Manual account registration](https://ai.zhiliaobiaoxun.com/?ch=s36)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown summaries with JSON request examples and occasional shell commands or configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include procurement search results, company or market analysis, API request guidance, account status, quota guidance, and links to vendor pages.]

## Skill Version(s):

1.0.3 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
