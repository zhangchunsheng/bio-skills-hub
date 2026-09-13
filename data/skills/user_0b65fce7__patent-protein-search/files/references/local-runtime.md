# Agent-local runtime

The Skill runs as a normal CLI process inside Codex or another agent. It does not expose an HTTP
port and does not require a backend service, database server, container, or web page. Python
3.11+ and outbound HTTPS access to EMBL-EBI are sufficient.

## Configuration

```text
EBI_CONTACT_EMAIL=<optional user-provided contact email>
PATENT_SEQUENCE_AUTO_EMAIL_DOMAIN=<optional fallback domain, default github.com>
PATENT_SEQUENCE_STATE_DIR=~/.cache/patent-sequence-local   # optional
```

The contact address is resolved in priority order: `EBI_CONTACT_EMAIL` (user-set) >
persisted auto address (`contact-email.json` in the state directory, generated once on
first external submission as `patent-seq-<hex>@<domain>`) > newly generated. EMBL-EBI
rejects addresses whose domain has no MX record, so the fallback domain must be
routable; `PATENT_SEQUENCE_AUTO_EMAIL_DOMAIN` may point at a domain the user controls.
Planning, capability checks, local cache reads, and result interpretation do not submit
anything. The address is read for provider submission only and is never written into
plan, search, cache, or HTML files (the dedicated `contact-email.json` config aside).
If a submission fails with `error_code: "INVALID_CONTACT_EMAIL"`, ask the user for a
real `EBI_CONTACT_EMAIL` and retry with a NEW idempotency key. The core sequence client
does not read PatSeek credentials or any self-hosted backend URL/key. Only the
separately invoked optional `patseek_enrichment.py` helper reads the current user's
`PATSEEK_API_KEY`.

## Local state

The state directory contains:

```text
plans/       Local plans with query length/digest and criteria
searches/    External job IDs, status, coverage, and normalized results
cache/       Normalized public provider results keyed by digest/database/criteria
enrichment-plans/  Zero-call plans containing only normalized public patent identifiers
enrichments/       Optional normalized public PatSeek detail results and actual credit metadata
contact-email.json Resolved contact address config (email + source + created_at)
```

Default search scope is ALL six patent databases (epo/jpo/kipo/uspto/nrpl1/nrpl2);
`plan --database <db>` narrows it.

Raw query sequences are processed in memory and are never written to these files. Alignment
output deliberately omits the upstream copy of the query sequence. The cache may contain public
target sequences returned by EMBL-EBI.

`render-html` creates a standalone UTF-8 HTML report with embedded CSS and no JavaScript,
tracking, external fonts, or server requirement. It escapes provider text before rendering.
Query residues remain excluded unless `--include-query-sequence` and a matching
`--sequence-file` are both provided; that option is appropriate only when the user accepts that
the generated file will contain the query sequence. Public-query alignment views use a shared
10-residue position ruler, five-residue grouping, and numbered substitution chips so differences
remain aligned with their absolute amino-acid positions. They also include a symmetric identity
matrix and transparent counts for exact matches, substitutions, and gap columns.

Planning is local and makes zero external submissions. Execution submits only cache misses,
requires `--confirm-external-submission`, and uses a stable idempotency key to reuse local task
state. Polling and cache reads make no new analysis submissions.

`render-html` never calls PatSeek. It reads an existing `enrichments/<search-id>.json` when
present; otherwise it renders a non-blocking optional-enrichment notice. Missing PatSeek Skill,
missing/invalid/disabled Key, insufficient credits, and uncertain outcomes are surfaced by the
optional helper with a concrete `user_action`. The helper sends only normalized P1 publication
identifiers to PatSeek, never the query sequence, alignment residues, digest, or local task state.

The default destination is the official EMBL-EBI JDispatcher FASTA endpoint. The
`PATENT_SEQUENCE_EBI_URL` override exists for isolated local testing; non-loopback overrides
must use HTTPS. Redirects and oversized responses are rejected.
