# Sequence evidence and reporting

Classify two independent evidence dimensions.

| Code | Observable criterion | Allowed wording |
|---|---|---|
| `QX` | identity = 100% and query coverage = 100% | exact match across the submitted query |
| `QH` | identity >= 90% and query coverage >= 90% | high-similarity, high-query-coverage candidate |
| `QS` | another API-filtered hit | sequence-similarity candidate |
| `P1` | at least one publication identifier parsed | eligible for patent-detail enrichment |
| `P0` | accession/internal identifier only | unresolved; do not invent a publication number |

The MVP claim-link state is always `C0` until a specific claim or text location is verified.
`QX` does not imply full target identity unless target coverage is also 100%.

Report:

1. Query digest and length, not the raw sequence.
2. Thresholds and selected databases.
3. Planned and actual external submissions, cache state, destination, and zero monetary cost.
4. Per-database status and representative candidates: identity, query/target coverage, E-value,
   accession, parsed publication IDs, and `Q*`, `P*`, `C0` classes.
5. Searched, failed, empty, and not-searched coverage.
6. Unresolved accessions, timeouts, partial results, and provider limitations.

State that similarity is candidate recall rather than claim scope, validity, FTO, or
infringement; empty results do not prove absence; database coverage and update timing are
provider-controlled; and cross-database results may not be family-deduplicated.
