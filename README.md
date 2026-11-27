# DataKlubform

Formerly `House_Prices` (renamed 2026-11-26; old links redirect). The Python
package and the Databricks catalog keep the name `house_prices`.

A learning data-engineering project that behaves like a real company pipeline. A synthetic
Polish housing market is served through a mock listings API; an adapter crawls it daily into a
data lake (bronze), and Databricks turns that into clean history (silver) and analytics (gold).

**Status: scaffold.** The package modules are empty, so the pipeline does not run yet.

This is the main project of **Data Klub**, a group of data people who learn by building
production-style pipelines together. Fake data comes from
[house-prices-generator](https://github.com/data-klub/house-prices-generator); the pipeline reads any source through config, so real data
can replace it later
([ADR 0008](docs/adr/0008-generator-separate-sources-by-config.md)).

## How we work

- **Meetings:** every Wednesday at 19:00 (Warsaw time) in a Discord voice channel. Chat in Discord
  too; decisions are written down here, as ADRs in [docs/adr/](docs/adr/).
- **Tasks:** in Linear, one team per repo ([ADR 0010](docs/adr/0010-linear-for-tasks.md)). Ask Kubi
  for an invite.
- **Where to start:** [docs/handoff.md](docs/handoff.md) lists the milestones. Pick one, open a
  branch, and send a small pull request with tests that names its Linear issue.
- **Cost:** everything is free. Each member uses their own
  [Databricks Free Edition](https://www.databricks.com/learn/free-edition) workspace
  ([ADR 0009](docs/adr/0009-databricks-free-edition-per-member.md)). There is no AWS dependency;
  members who want to try Lambdas get their own login to the club's AWS sandbox
  ([ADR 0011](docs/adr/0011-aws-team-access-iam-users.md)).
- **Databricks jobs:** job definitions and their deployment live in
  [databricks-jobs](https://github.com/data-klub/databricks-jobs) (Databricks Asset Bundles,
  deployed by GitHub Actions on merge). It connects this pipeline to the generator's data.
- **Warm-up:** [Lab 01](https://github.com/data-klub/house-prices-generator/tree/main/labs/01-s3-data-lake), a small AWS data lake
  you can build in an evening (it lives in the generator repo).

Start with [CLAUDE.md](CLAUDE.md) for the project rules and [docs/spec.md](docs/spec.md) for the
technical spec. Decisions are recorded in [docs/adr/](docs/adr/).

## Setup

Everything runs natively on macOS and Windows, with no WSL or Docker. You need
[Git](https://git-scm.com/downloads) and [uv](https://docs.astral.sh/uv/). uv installs
Python 3.12 for you.

### macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh    # or: brew install uv
git clone https://github.com/data-klub/DataKlubform.git
cd DataKlubform
uv sync
uv run pre-commit install
uv run pytest
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Close and reopen PowerShell so that uv is on your PATH.
git clone https://github.com/data-klub/DataKlubform.git
cd DataKlubform
uv sync
uv run pre-commit install
uv run pytest
```

The first commit after `pre-commit install` takes longer, because the hooks download their tools
(including a Go toolchain for the secret scan, if you don't have one).

## Everyday commands

These are the same on both platforms:

```bash
uv run pytest                  # run the tests
uv run ruff check .            # lint
uv run ruff format .           # format
uv run pre-commit run -a       # run every hook on every file
```

`uv run mock-api`, `uv run crawl` and `uv run upload` are listed in CLAUDE.md but don't exist
yet. They will be added along with the code they run.

## Secrets

Never put secrets in code, config or chat. Set them as environment variables locally and as
GitHub Secrets in CI: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `MOCK_API_KEY`.

```bash
export MOCK_API_KEY=...        # macOS
```

```powershell
$env:MOCK_API_KEY = "..."      # Windows
```

## Layout

```
config/                  pipeline settings (sources, scope)
docs/                    spec and decision records (ADRs)
src/house_prices/
  contract/              bronze envelope, crawl manifest, canonical listing
  generator/, mock_api/  empty; removed once house-prices-generator v0.1.0 is pinned
  adapters/              source adapters and templates for real sources
  runner/                shared crawl loop and bronze file writing
  parsers/               payload to canonical listing, one per source
  upload.py              push data/raw to the Databricks Volume
tests/
data/, truth/            generated locally, never committed
```
