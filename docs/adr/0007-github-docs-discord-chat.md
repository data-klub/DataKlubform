# 0007: Handbook and docs in GitHub, chat in Discord

- **Status:** Accepted (team meeting 2026-11-26)
- **Date:** 2026-11-05

## Context

The team has 3+ contributors, and people will join later. Late joiners need to find out what was decided and why, without reading through old chat.

## Options

1. **Handbook and docs in GitHub, chat in Discord:** durable knowledge is versioned and reviewed next to the code, and day-to-day talk stays quick. Decisions made in chat have to be written down deliberately.
2. **Discord for everything:** the least effort, but decisions get lost in the scrollback.
3. **A separate wiki or docs tool:** easy to edit, but it sits away from the code and PR review, and it may add accounts or cost.

## Decision

Option 1. Anything people need to find later lives in GitHub, and Discord is for conversation.

## Consequences

- Late joiners have a searchable history that doesn't depend on chat.
- Docs changes go through PRs, which adds some friction.
- A decision reached in Discord doesn't count until it is recorded in GitHub. Hard-to-reverse decisions need an ADR.
- ADRs about this project live in `docs/adr/` in this repo. Decisions that affect the whole Data Lab go in the shared `handbook` repository once it exists (decided 2026-11-05).
