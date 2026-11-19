# House_Prices — Technical Spec

Source of truth for the pipeline. Condensed from the team's design docs (Nov 2026).

## 1. Decisions so far (candidate ADRs)

| # | Decision | Why |
|---|---|---|
| 0001 | Synthetic data served by a mock API, no scraping in the public repo | Legal, reproducible, publishable; real sources plug in via adapters |
| 0002 | Bronze contract: raw envelope + crawl manifest, append-only | Any source works downstream without changes |
| 0003 | Generate all of Poland; filter to Warsaw only in gold via `analysis_scope` | Scale to other cities by config |
| 0004 | Load only the last 30 days at start, then daily | Fits Databricks Free Edition limits; extend later |
| 0005 | GitHub Actions + Databricks Jobs for scheduling, no Airflow | Free, nothing to host |
| 0006 | English text, Polish geography and PLN | Readable for all, realistic market |
| 0007 | Handbook and docs in GitHub, chat in Discord | Searchable history for late joiners |
| 0008 | Generator in its own project; sources plug in through `config/pipeline.yaml` (Accepted) | Real data replaces fake data without pipeline changes |
| 0009 | Databricks Free Edition, one workspace per member, code shared through GitHub (Proposed) | Free, and nobody depends on one account's quota |

## 2. Architecture

```
generator (seeded world) ──> mock API (FastAPI, OLX-like + Otodom-like)
        │                          │  HTTP: pagination, API key, 429, 5xx, as_of
        ▼                          ▼
   truth/ (tests only)       adapter + runner ──> data/raw/... (bronze files + manifests)
                                                   │  upload (GitHub Actions)
                                                   ▼
                    Databricks Volume /Volumes/house_prices/raw/landing
                                                   │  Auto Loader
                                                   ▼
            bronze.listings_raw ─> silver.* (parse, SCD2, lifecycle) ─> gold.* (Warsaw)
```

The generator and mock API live in their own repo, [house-prices-generator](https://github.com/data-klub/house-prices-generator) (ADR 0008). House_Prices starts at the adapter.

Databricks naming: catalog `house_prices`; schemas `raw` (volume `landing`), `bronze`, `silver`, `gold`.

## 3. Bronze contract

### 3.1 Envelope — one JSON line per record

| Field | Type | Example | Rule |
|---|---|---|---|
| `schema_version` | string | `"1.0"` | Bump on breaking change |
| `source` | string | `"olx"` | Lowercase source key |
| `adapter` | string | `"mock_api"` | Which code produced it |
| `adapter_version` | string | `"0.1.0"` | Package version or git SHA |
| `crawl_id` | string | `"olx-20261102-0600"` | Links to manifest |
| `fetched_at` | timestamp | `"2026-11-02T06:00:12Z"` | Always UTC |
| `record_type` | string | `"detail"` | `card`, `detail`, `development` |
| `source_listing_id` | string | `"1104369854"` | Site's own id, as text |
| `source_url` | string | URL | Tracking params removed |
| `fetch_status` | string | `"ok"` | `ok`, `not_found`, `gone`, `error` |
| `http_status` | int\|null | `200` | |
| `payload_format` | string | `"json"` | `json` or `html` |
| `payload` | string\|null | raw body | Untouched; null if status ≠ ok |
| `payload_sha256` | string\|null | hex | Cheap change detection |

Ship a JSON Schema at `src/house_prices/contract/schema/bronze_envelope.schema.json` and validate in tests.

### 3.2 Crawl manifest — one per crawl, written last

`crawl_id`, `source`, `started_at`, `finished_at`, `mode` (`full`|`incremental`), `scope` (e.g. `{"region": "PL", "type": "sale"}`), `as_of` (date or null), `cards_seen`, `details_fetched`, `errors`, `status` (`complete`|`partial`|`failed`).
Only a **complete full** crawl can prove a listing disappeared.

### 3.3 File layout

```
data/raw/{source}/ingest_date=YYYY-MM-DD/{crawl_id}/part-0001.jsonl.gz
data/raw/{source}/ingest_date=YYYY-MM-DD/{crawl_id}/_manifest.json
```
Same layout under the Volume. `ingest_date` = the simulated/business date (`as_of` or today).

### 3.4 Adapter rules

1. Append-only; never overwrite or delete in `raw/`.
2. No cleaning in adapters: `payload` is stored exactly as received. The only exception is envelope metadata: `source_url` has tracking parameters removed (§3.1).
3. Duplicates allowed; removed downstream.
4. Removed listing re-checked ⇒ envelope with `fetch_status = gone`, null payload.
5. Re-running a day ⇒ new `crawl_id`.

## 4. Generator

Moved to the [house-prices-generator](https://github.com/data-klub/house-prices-generator) repo (`docs/spec.md` there) on 2026-11-19, per
ADR 0008: the world model, determinism, geography, daily events, source renderers, descriptions,
renovation labels and the 28 injected edge cases.

## 5. Mock listings API

Also in the generator repo (its spec §3). What this pipeline relies on is listed in that repo's
README under "How it fits with House_Prices": the endpoints, `X-API-Key`, 429 with `Retry-After`,
404/410 for removed listings, payload shapes pinned by golden files, stable listing ids, and
`uv run mock-api` on `localhost:8000`.

## 6. Adapters and runner

```python
class SourceAdapter(Protocol):
    source: str
    version: str
    def list_cards(self, scope: Scope, as_of: date | None) -> Iterator[RawRecord]: ...
    def fetch_detail(self, listing_id: str) -> RawRecord: ...
```
The **runner** (shared) handles envelopes, manifests, retries with backoff, rate limiting, gzip writing, and calls the adapter.
Crawl strategy: read all search pages daily (full), fetch details for new ids or cards whose price/date line changed, weekly full detail refresh, re-check vanished ids once (→ `gone`).
Templates in `src/house_prices/adapters/templates/`: `scraper_template.py`, `provider_api_template.py`, `csv_template.py` (examples only, not wired to real sites).

**Personal-use swap = 3 changes:** adapter, one `parse(payload) -> CanonicalListing` parser in `src/house_prices/parsers/`, and config (`sources`, `analysis_scope`).

## 7. Configuration

`config/generator.yaml` lives in the [generator repo](https://github.com/data-klub/house-prices-generator).

`config/pipeline.yaml`
```yaml
sources:
  - {name: olx, adapter: mock_api, base_url: "http://localhost:8000/olx/api/v1"}
  - {name: otodom, adapter: mock_api, base_url: "http://localhost:8000/otodom/api/v1"}
raw_dir: data/raw
volume_path: /Volumes/house_prices/raw/landing
analysis_scope:
  - teryt: "1465"   # Warszawa
delisting_missed_full_crawls: 3
```

## 8. Silver

| Table | Grain | Purpose |
|---|---|---|
| `silver.listing_snapshot` | listing × crawl | Parsed, typed, deduped canonical fields |
| `silver.listing_history` | listing × version (SCD2) | `valid_from`, `valid_to`, `is_current`, `version`, `change_type` |
| `silver.listing_lifecycle` | listing | first_seen, last_seen, status (active/delisted/relisted), delisted_on, last_asking_price |
| `silver.crawl_health` | crawl | From manifests |
| `silver.development` | development × day | status, completion quarter, units available |
| `silver.dim_location` | location | TERYT hierarchy |

- **Canonical listing** fields (nullable where a source lacks them): source, listing_id, url, title, property_type, market, price_pln, price_on_request, is_promo, price_lowest_30d_pln, price_negotiable, area_m2, usable_area_m2, plot_area_m2, rooms, floor, building_floors, building_type, year_built, finishing_state, heating[], amenities[], monthly_rent_pln (+ rent_status), ownership, available_from, advertiser_type, agency_ref, investment_id, location_text, location_precision, teryt, lat, lon, description, description_sha256, refreshed_at, created_at, source_last_updated, seller_hash.
- **SCD2 tracked**: price_pln, price_on_request, area_m2, rooms, floor, finishing_state, description_sha256, title, advertiser_type. **Ignored**: refreshed_at, fetched_at, photos, field order.
- **Late data** merges into history by date, never becomes "current" wrongly.
- **Delisting**: missing from N (=3) consecutive **complete full** crawls ⇒ `delisted`; store `last_asking_price`, never call it a sale price; reappearance ⇒ `relisted`.
- **PII**: drop names/phones/emails; scrub phone patterns from description; hash seller/profile ids and NIP.

## 9. Gold (first versions, filtered by `analysis_scope`)
- `gold.price_history` — one row per listing per price version.
- `gold.comparables` — median price/m² by district × property type × area band × month.
- `gold.property_match` (later) — links reposts and cross-posts (keys: agency_ref, parcel number, area±1%, price, location, text similarity).

## 10. Notes for real sources
- OLX served plain HTTP in our test; Otodom blocked automated fetching (bot detection). Do not bypass bot protection, logins or CAPTCHAs.
- Real sources cannot backfill; history starts when you start crawling. Respect terms of use and robots.txt.
