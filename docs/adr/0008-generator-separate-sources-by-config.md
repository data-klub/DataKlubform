# 0008: Generator in its own project; the pipeline reads any source through config

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decided by:** the team at the Data Klub meeting on 2026-11-18

## Context

The generator and mock API were being built in a separate project, while the spec still placed
them in `src/house_prices/generator/` and `src/house_prices/mock_api/` (see the open decision in
`docs/handoff.md`). The team also wants the pipeline half to be useful on its own: if someone
later has real data, they should be able to plug it in and drop the fake data without touching
the Databricks code.

## Options

1. **Keep everything in one repo:** one place to look, but the pipeline and the simulator change
   together, and anyone reusing the pipeline also inherits the simulator.
2. **Split, with the bronze contract and config as the boundary:** the pipeline only knows the
   bronze contract (spec §3) and the `sources` list in `config/pipeline.yaml`. The generator and
   mock API become one source among others. Two repos to keep in step.
3. **Split, with the pipeline reading the generator's files directly:** simplest at first, but it
   skips the adapter, so a real source would need new pipeline code.

## Decision

Option 2. The generator and mock API live in their own project. House_Prices keeps no generator
code; it reads every source the same way:

```
any source ──> adapter + parser (chosen in config) ──> bronze files (contract §3) ──> Databricks
```

`config/pipeline.yaml` is the plug. Each entry under `sources` names the adapter, the parser and
where to reach the source, and secrets are referenced by environment-variable name only:

```yaml
sources:
  - {name: olx, adapter: mock_api, parser: olx_v1, base_url: "http://localhost:8000/olx/api/v1", api_key_env: MOCK_API_KEY}
  # A real source later, for personal use:
  # - {name: my_csv, adapter: csv_files, parser: my_csv_v1, path: "data/inbox/my_csv/"}
```

Swapping fake data for real data means: add the real source's adapter and parser, add its entry,
and delete the `mock_api` entries. Bronze, silver and gold stay unchanged.

## Consequences

- The `generator/` and `mock_api/` packages leave this repo, and `config/generator.yaml` moves to
  the generator project. Spec §4–5 describe that project until it has its own docs.
- House_Prices installs the generator as a pinned dependency for tests and the daily workflow,
  which still gets `uv run mock-api`.
- Milestone 2 (config models) adds `parser` and the `*_env` secret fields to the `sources` model.
- Tests that compare against `truth/` run with the generator installed; pipeline code still never
  reads `truth/`.
- **Open:** the generator project's name and when it moves into the `data-klub` organization.
