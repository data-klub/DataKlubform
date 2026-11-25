# 0009: Databricks Free Edition, one workspace per member, shared through GitHub

- **Status:** Proposed (for review on 2026-11-26)
- **Date:** 2026-11-19

## Context

Everyone in the team will use Databricks, and we want to stay free. What Free Edition offers,
from the [limitations page](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)
(checked 2026-11-19):

- Free, no credit card, non-commercial use only. No support or SLA. Accounts that stay inactive
  for a long period may be deleted.
- Serverless compute only. One SQL warehouse (2X-Small), at most 5 concurrent job tasks, one active
  pipeline per pipeline type. Going over the daily quota shuts compute down for the rest of the day.
- One workspace per account. Outbound internet is limited to trusted domains, and custom storage
  locations are not supported. Reading our own S3 bucket is not documented, so we must not depend on it.
- Shared notebooks allow real-time collaboration. A Databricks blog says an account is meant for up
  to five people on a group project, but the docs don't describe adding users to a workspace.

**Tried on 2026-11-22:** a job with a file arrival trigger on our S3 bucket failed with "storage
location not found": Free Edition has no external location for the bucket. A trigger on a Unity
Catalog volume (`/Volumes/house_prices/raw/landing/`) is the supported way. Files get into the
volume by upload, or from a Lambda through the Files API (ADR 0011).

## Options

1. **One workspace per member, code shared through GitHub:** each person signs up for free and owns
   their workspace. Code lives in this repo and is pulled into each workspace with Git folders; data
   gets there with `uv run upload`. Nobody depends on someone else's quota or account.
2. **One shared team workspace:** everyone sees the same tables, but adding members is not documented,
   all work shares one daily quota, and the team depends on one person's account.
3. **A paid workspace on AWS:** full features, including S3 access, but it costs money.

## Decision

Option 1, to be confirmed on 2026-11-22. One member also tests whether a Free Edition workspace can
add users; if it can, a shared workspace can be added later for demos.

## Consequences

- Every member runs the full pipeline in their own workspace with the same catalog layout
  (`house_prices` with `raw`, `bronze`, `silver`, `gold`), so notebooks and jobs must not hard-code
  a workspace URL or user name.
- Each member keeps their own `DATABRICKS_HOST` and `DATABRICKS_TOKEN` as environment variables.
  The scheduled `daily.yml` uploads to one workspace, set by GitHub Secrets.
- The pipeline does not read S3. Lab 01 on AWS stays a separate learning exercise.
- The daily quota and the 30-day backfill (ADR 0004) keep data volumes small.
