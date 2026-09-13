## Description: <br>
香港保险产品数据 API（MCP）：查询/对比储蓄险、寿险、医疗险、危疾险、年金险产品，含真实IRR、回本年、分红实现率数据。Query & compare Hong Kong insurance products (savings/life/medical/critical/annuity) with real IRR, breakeven and dividend fulfillment data via a paid MCP endpoint. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[newle](https://clawhub.ai/user/newle) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, analysts, and insurance professionals use this skill to query and compare Hong Kong insurance products, including savings, life, medical, critical illness, and annuity products. It supports product research, retirement-planning analysis, and insurance comparison workflows using a paid MCP API. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill requires an API key for a paid third-party service. <br>
Mitigation: Treat the API key as a secret, store it in an environment variable, and avoid pasting it into chats, source files, or logs. <br>
Risk: The skill sends insurance queries to a third-party MCP API. <br>
Mitigation: Review the service terms and data sensitivity before sending user, client, or portfolio information to the endpoint. <br>
Risk: The registration flow may involve email verification that an agent could access if granted email-client permissions. <br>
Mitigation: Only allow email-client access when explicitly intended, and prefer user-controlled browser verification for account setup. <br>
Risk: Insurance product data and IRR comparisons can be mistaken for personalized investment or insurance advice. <br>
Mitigation: Present results as reference data, preserve the source disclaimer, and direct users to a licensed insurance advisor for purchase decisions. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/newle/skills/hk-insurance-data) <br>
- [HK Insurance Data MCP Endpoint](https://insurance.mytreasure.ren/api/mcp/mcp) <br>
- [HK Insurance Data Website](https://insurance.mytreasure.ren) <br>
- [Developer Login](https://insurance.mytreasure.ren/dev/login) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Shell commands, Configuration, API calls, Text] <br>
**Output Format:** [Markdown with inline shell commands, JSON-RPC examples, and configuration guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Produces guidance for querying a paid third-party MCP API and may return structured insurance product data from that service.] <br>

## Skill Version(s): <br>
1.0.0 (source: release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
