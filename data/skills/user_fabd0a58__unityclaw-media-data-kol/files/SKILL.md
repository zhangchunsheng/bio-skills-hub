---
name: unityclaw-media-data-kol
description: Retrieve a public social-media creator or KOL profile snapshot from a homepage URL, including identity, bio, follower, following, like, post, and update fields when available. Use for public creator research, profile summaries, audience-size checks, campaign screening, and KOL comparison while preserving raw platform values and saving a local JSON result.
version: 1.2.5
metadata:
  openclaw:
    requires:
      env:
        - UNITYCLAW_KEY
      bins:
        - node
        - npm
    primaryEnv: UNITYCLAW_KEY
    install:
      - kind: node
        package: "@unityclaw/sdk"
        bins: []
---

# UnityClaw Media KOL Profile

Retrieve a structured snapshot of one public social-media profile. Preserve raw values, localize labels for presentation, warn about incomplete snapshots, and save `kol-profile.json` in the task folder.

## Agent Workflow

### 1. Confirm the target

Accept one public creator homepage URL per invocation. Use a profile page, not an individual post, video, search page, private network address, or URL containing credentials. Xiaohongshu URLs must contain `/user/profile/`; TikTok URLs must identify an `@username` profile.

Use this skill for public profile metrics. Do not use it to access private accounts, bypass authentication, identify an anonymous person, infer sensitive traits, or make high-impact employment, credit, insurance, housing, or legal decisions.

### 2. Execute the snapshot

Run `scripts/generate.js` with `--json` and an explicit `--output-dir`. Quote the URL. Select `--lang` from the user's conversation language or leave it as `auto`.

Fetch each profile once. Allow the CLI to handle transient retries, but do not issue duplicate concurrent requests. For multiple KOLs, run one URL at a time and retain each result's source URL and timestamp fields.

### 3. Preserve platform values

Use `data` as the raw service response. Do not silently convert abbreviated counts, round metrics, merge fields, or invent missing values. Use localized `fields` only for presentation; every field retains its raw `key`.

Treat the result as a time-dependent snapshot. Follower, following, like, and post counts can change, and similarly named metrics may have different meanings across platforms. Do not claim cross-platform comparability without explaining the platform context.

### 4. Validate completeness

Inspect `missingCoreFields` and `warnings`. The CLI warns when it cannot find a profile identity or follower count, and when the platform is unrecognized. Missing fields remain unknown rather than zero.

The returned profile does not prove identity, account ownership, audience authenticity, engagement quality, or suitability for a campaign. Combine it with content and engagement analysis when the user needs those conclusions.

### 5. Deliver the result

Accept completion only when `success` is `true` and `resultPath` points to a non-empty `kol-profile.json`. Present the requested metrics in the user's language, identify the detected platform, retain the source URL, and mention warnings or missing fields.

### 6. Handle failures deliberately

Retry only when `error.retryable` is `true`; respect the CLI retry limit. Correct invalid URLs and profile-page mistakes before retrying. If the platform blocks access or the profile is private or unavailable, report that limitation instead of fabricating data.

## Authorization

Provide the API key through the fixed `UNITYCLAW_KEY` environment variable. Obtain a key from [UnityClaw](https://unityclaw.com/) if needed. The runtime installation declaration installs `@unityclaw/sdk`; for manual execution, run `npm install @unityclaw/sdk` when the package is unavailable.

## Usage

```bash
node scripts/generate.js --url "https://www.xiaohongshu.com/user/profile/xxxx"
node scripts/generate.js --url "https://www.tiktok.com/@username" --lang zh --json --output-dir ./tasks
```

## Parameters

| Parameter | Short | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| `--url` | `-u` | Yes | - | One public social-media profile URL |
| `--lang` | `-l` | No | `auto` | Presentation-label language: `auto`, `zh`, `en`, or `ja`; locale variants are accepted |
| `--output-dir` | - | No | `./tasks` | Task output directory; resolved to an absolute path |
| `--timeout` | - | No | `900000` | SDK request timeout in milliseconds, from 1,000 to 3,600,000 |
| `--retries` | - | No | `1` | Retry count for transient failures, from 0 to 3 |
| `--json` | - | No | `false` | Emit one machine-readable JSON result without progress output |
| `--help` | `-h` | No | - | Show help |

## Known Fields

| Raw key | Meaning |
|---------|---------|
| `user_id` | Platform user identifier |
| `username`, `name`, `nickname` | Public profile names when returned |
| `signature`, `description`, `bio` | Public profile description |
| `follower_count` | Follower count or platform-formatted value |
| `following_count` | Following count or platform-formatted value |
| `like_count` | Like count or platform-formatted value |
| `post_count`, `note_count` | Published content count |
| `avatar` | Public avatar URL when returned |
| `updated` | Snapshot update value when returned |

Extra fields returned by the service are preserved.

## Output Contract

With `--json`, the command emits exactly one JSON object. A successful result contains task metadata, `resultPath`, `resultBytes`, `sourceUrl`, `platform`, `language`, raw `data`, localized `fields`, `missingCoreFields`, and `warnings`. The task folder contains `kol-profile.json` plus SDK request and response logs.

A failed result contains a stable `error.code`, human-readable `error.message`, `error.retryable`, `attempts`, and available task or log information. The process exits non-zero on failure.

## Resource Index

- Run `scripts/generate.js` for KOL profile retrieval.
