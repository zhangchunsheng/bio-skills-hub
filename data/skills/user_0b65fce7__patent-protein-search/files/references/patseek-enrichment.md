# Optional PatSeek enrichment

PatSeek is not part of sequence planning, execution, or polling. Use it only after the
self-hosted search has produced `P1` publication identifiers and the user asks for enrichment.

1. Run `scripts/patseek_enrichment.py check`. If capability is unavailable, show its
   `user_action`; the sequence workflow remains usable.
2. Run `plan <search-id> --top 5`. Planning is local and sends nothing. Preserve the raw
   accession-to-publication mapping, normalize and deduplicate publication numbers, and never
   guess a publication for `P0` records.
3. Report the distinct public identifiers, planned detail calls, expiry, confirmation
   requirement, and that credits are unknown until the response. Do not execute merely because
   the Skill and Key appear configured.
4. After explicit confirmation, run `execute --plan-id ... --confirm-patseek-use`. It validates
   the Key first and then requests details sequentially. Do not retry an uncertain call; inspect
   PatSeek account/task records before creating a new plan.
   If the standard-library HTTPS stack itself is incompatible, the explicit
   `--transport skill-client` option may use the installed PatSeek Skill's HTTP dependency. It
   still makes one attempt per detail and never falls back automatically.
5. The normalized output keeps patent identity, applicant/inventor, dates, aggregated legal
   status, family/citation counts, source URLs, and conservative claim signals. `C2` requires an
   explicit claim SEQ ID that matches an ID parsed from the source hit; other claim/identity
   language remains `C1`, and absent evidence remains `C0`.
6. Run the ordinary `render-html` command again. It automatically merges a matching enrichment
   state. Report enriched, unresolved, failed, uncertain, and not-attempted publications, plus
   actual returned credits, separately from local sequence-search submissions.
7. Never send the query sequence, query digest, alignment residues, or local task state to
   PatSeek. Never call PatSeek sequence endpoints as a fallback.

Legal status is jurisdiction- and time-dependent. A WO or EP publication alone does not prove
an enforceable right in a particular country, and API data is not a legal opinion.
