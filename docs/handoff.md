# Handoff

Where the project stands and what to build next. Read `CLAUDE.md` and `docs/spec.md` first.
Update this file in the PR that finishes or changes a milestone.

Last updated: 2026-11-14

## How to work

- **Check the real state first.** Docs drift: confirm with `git log`, open PRs, CI runs and
  branch protection before relying on anything below.
- **Work on a branch and open a PR.** Never push to `main`; CI must pass, and a person merges.

## Current state

| Area | State |
|---|---|
| Code | Scaffold only: every module under `src/house_prices/` is empty |
| Tests | `tests/test_scaffold.py` (imports, config values) |
| CI | ruff and pytest on ubuntu, windows and macos, plus a gitleaks scan of the full history |
| `main` protection | `ubuntu-latest`, `windows-latest` and `secret-scan` must pass. No review rule yet: the only contributor can't approve their own PRs |
| Decisions | ADRs 0001–0007 are Proposed, waiting for team review |
| Databricks | Catalog `house_prices` with schemas `raw`, `bronze`, `silver`, `gold` and volume `raw.landing`. No token or Git folder yet |

## Open decision: where the generator lives

The generator and mock API are being built in a separate project. The spec still places them
in `src/house_prices/generator/` and `src/house_prices/mock_api/`.

- If they stay separate, write an ADR, remove those two packages, and let House_Prices install
  the generator as a pinned dependency that provides `uv run mock-api`.
- If they come back, they land in those packages.

Until this is decided, don't write code in `generator/` or `mock_api/`.

## Milestones

Each step is one small PR with tests.

1. **Bronze contract** (spec §3.1–3.2). JSON Schema at
   `src/house_prices/contract/schema/bronze_envelope.schema.json`, pydantic models for the
   envelope and the crawl manifest, and tests that validate a sample of each.
2. **Config models.** Pydantic loaders for `config/pipeline.yaml` and `config/generator.yaml`.
   TERYT codes stay text.
3. **Runner writer** (spec §3.3–3.4). Gzipped JSONL parts and `_manifest.json` in the
   `data/raw/{source}/ingest_date=…/{crawl_id}/` layout. Append-only; a re-run gets a new
   `crawl_id`; the manifest is written last.
4. **Adapter protocol** (spec §6). `SourceAdapter` plus an in-memory fake adapter, so the
   runner can be tested without HTTP.
5. **Mock API adapter.** Pagination, `X-API-Key`, 429 with `Retry-After`, 5xx retries,
   404/410 → `gone`. Test with `httpx.MockTransport`.
6. **Crawl CLI.** `uv run crawl --mode daily|backfill`.
7. **Upload and daily workflow.** `uv run upload` to the Volume and `daily.yml`.
8. **Databricks.** Auto Loader into `bronze.listings_raw`, then silver and gold (spec §8–9).

Steps 1–4 need nothing from the generator. Step 5 needs the mock API's payload formats.

## Traps

- **macOS CI:** the job sometimes fails without running ("not acquired by Runner"). That is
  GitHub capacity, not the code. Rerun it; don't change the workflow.
- **Windows:** use `pathlib`, pass `encoding="utf-8"` on every file read and write, and write LF.
- **Bronze contract changes:** bump `schema_version` and update `docs/spec.md` in the same PR.
- **ADRs:** don't mark them Accepted; that's the team's decision.
- **Tutor page:** the House_Prices Tutor on claude.ai holds a copy of these docs. After changing
  `CLAUDE.md`, `README.md`, `docs/spec.md` or the ADRs, the page needs rebuilding.
