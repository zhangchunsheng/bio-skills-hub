# Runtime independence

Every final `MAINTAINABLE_SOURCE` delivery, including editable `FAITHFUL_CLONE` and later `CREATIVE_REBUILD` results, must make no runtime requests to the source origin. Final `CLEAN_REBUILD` results have the same requirement. Check both captured network evidence and the final build output:

```text
python <skill-root>/scripts/check_runtime_independence.py <network-evidence.json> --source-url <canonical-url> --build-dir <dist>
```

Third-party origins are not blocked by this gate. The source origin cannot be allowlisted; if the deliverable intentionally depends on it, the runtime-independence gate has not passed. Default HTTP and HTTPS ports are normalized before origins are compared.

Sanitized SPA HAR fixtures can be checked with the same command by passing the `.har` file as network evidence. A runtime-independent fixture must rebase recorded service origins to the candidate origin and pass the gate together with the final build. During browser replay, also require no candidate-side API path in `capture-manifest.json` under `harFixtures.fallbacks` and no candidate-side blocked request; otherwise the HAR is incomplete or the candidate still targets an external runtime.

Teardown does not require this gate. Replay-only choice A may explicitly stop without it. Recovery work may temporarily use the original production backend; document the recovery stage and apply the gate incrementally rather than pretending independence already exists. Choices B and C cannot enter formal review until the final candidate passes.
