# 0010: Linear for tasks, GitHub for code and decisions

- **Status:** Proposed (not yet decided; reviewed 2026-11-26)
- **Date:** 2026-11-25

## Context

Work is now split across two repos (House_Prices and house-prices-generator) and four people, and
the team needs one place to see who is doing what. ADR 0007 puts docs and decisions in GitHub and
chat in Discord, but it doesn't say where tasks live. The team has started using Linear.

## Options

1. **Linear (free plan):** fast and pleasant to use, unlimited members, two teams (one per repo),
   and a GitHub integration that links pull requests to issues and closes them on merge. It is one
   more account, and the free plan stops at 250 issues.
2. **GitHub Issues and Projects:** free with no limits and right next to the code, but slower to
   work with and less pleasant for planning.
3. **Jira:** the industry standard, but heavy for a small learning group.

## Decision

Option 1. Tasks and planning live in Linear, with one Linear team per repo. Code, docs, ADRs and
reviews stay in GitHub (ADR 0007), and chat stays in Discord. A milestone in a repo's
`docs/handoff.md` becomes one or more Linear issues.

## Consequences

- Each pull request names its Linear issue (for example `DK-12` in the branch name or title), so
  the GitHub integration links them.
- Decisions made in a Linear comment still need an ADR in GitHub.
- Credentials never go into Linear; passwords are sent by direct message.
- **Watch:** the 250-issue limit of the free plan. If we get close, archive done issues or revisit
  this decision.
