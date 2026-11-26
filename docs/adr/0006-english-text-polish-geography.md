# 0006: English text, Polish geography and PLN

- **Status:** Proposed
- **Date:** 2026-11-05

> Reconstructed from `docs/spec.md` §1 and the team design docs. The spec records the decision and its reason, but not the alternatives, so the options below need the team's confirmation before this ADR is accepted.

## Context

Contributors need to read the generated data, and not all of them may read Polish. The data should still feel like the Polish market, with its locations, prices and listing patterns.


## Decision

Option 1. Descriptions and labels are in English. Place names keep their Polish diacritics (Łódź, Białołęka), and prices are in PLN.

## Consequences

- Everyone can read payloads and debug parsers.
- Encoding becomes a real concern across macOS and Windows: files must be read and written as UTF-8 explicitly.
- Mock API parsers will not work on real sites as they stand. A real source needs its own parser for Polish labels, such as month names in date lines.
- Text-based work such as the renovation classifier is trained on English phrases, so it would need rework for real Polish ads.
