# 0006: English column names, Polish content and geography, PLN

- **Status:** Accepted (team meeting 2026-11-26)
- **Date:** 2026-11-05, decided 2026-11-26

## Context

Contributors need to read the generated data, and not all of them may read Polish. The data should still feel like the Polish market, with its locations, prices and listing patterns, and a real Polish source should be easy to plug in later (ADR 0008).

## Options

1. **English column names, Polish content:** field and column names (`price_pln`, `district`) are English, so the code and schemas read the same for everyone. Listing text and labels are Polish, like on real sites, with Polish geography and PLN.
2. **English text and labels, with Polish geography and PLN:** readable by everyone, but parsers and text features would not carry over to real Polish sources.
3. **Fully fictional and English:** no language or encoding issues, but it loses TERYT codes and real place names, along with the realism.

## Decision

Option 1. Column names are in English. Content should be Polish. Place names keep their Polish diacritics (Łódź, Białołęka), and prices are in PLN.

## Consequences

- Code, schemas and tables use English names. Values inside payloads (titles, descriptions, labels such as "Cena", "Powierzchnia", month names in date lines) are Polish.
- Parsers written for the mock API are close to what a real Polish source needs, so a real source mostly needs its own field mapping.
- Contributors who don't read Polish need a short glossary of the labels the parsers use. It lives in the generator's spec.
- Encoding is a real concern across macOS and Windows: files must be read and written as UTF-8 explicitly.
- Text-based work such as the renovation classifier works on Polish phrases.
