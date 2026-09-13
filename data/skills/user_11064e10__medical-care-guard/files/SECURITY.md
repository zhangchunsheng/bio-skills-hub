# Security & Data Disclosure

This skill runs locally. To return the latest policy interpretations and calculation results, it calls a cloud knowledge-base service over HTTPS.

## Data transmitted
- When you actively ask a question or run a calculation, the inputs you provide (such as city, salary, length of employment, contract text, or other case-specific details) are transmitted via HTTPS to the cloud knowledge-base service at `https://mcp.aitaxs.top`.
- No device fingerprint, hardware identifier, or local file is read or uploaded.

## Data NOT collected
- A random anonymous identifier is generated locally for service invocation and rate limiting. The `X-Client-Id` header carries a skill identifier, not your personal identity.
- Your identity is never associated with your consultation content.

## Purpose and retention
- Transmitted data is used only to return the current consultation's policy answer or calculation result.
- Data is not persistently stored on any remote server and is not used for profiling or marketing.

## Your control
- Initiating a consultation is taken as your informed consent to the transmission described above for that request.
- Fully offline use is possible via the bundled `offline_workflows` manual, which does not trigger any network call.
- You may desensitize direct identifiers (name, ID number, property address, etc.) before input; only provide the fields required for the policy calculation.

## Endpoint
- `https://mcp.aitaxs.top/api/services/<service>/mcp` — knowledge-base query service only.
