# 0005: GitHub Actions and Databricks Jobs for scheduling

- **Status:** Accepted (team meeting 2026-11-26)
- **Date:** 2026-11-05

## Context

The pipeline has two scheduled parts: a daily crawl and upload, and Databricks processing. The team has no budget for infrastructure and no one to run it.

## Options

1. **GitHub Actions plus Databricks Jobs:** free, with nothing to host, and each tool runs the work closest to it. There is no single view across the two, and no dependency tracking between them.
2. **Airflow:** a single orchestrator with dependencies and backfills, and a skill many companies use. It has to be hosted and maintained, which is out of proportion for one daily pipeline.
3. **Cron on a machine we own:** simple, but it depends on one person's machine, and logs and secrets are not shared.

## Decision

Option 1. A GitHub Actions workflow (`daily.yml`) runs the crawl and upload, and Databricks Jobs process what has landed.

## Consequences

- There is nothing to host: the mock API starts inside the workflow job and the adapter calls it on localhost.
- Secrets live in GitHub Secrets.
- GitHub's scheduled runs can start late, so Databricks processing must tolerate files arriving late or not at all. Auto Loader and the crawl manifests support this.
- Failures must be visible in two places, so alerting needs to cover both.
- **Open:** whether to also host the mock API publicly on a free tier. The default is to keep it inside each workflow run.
