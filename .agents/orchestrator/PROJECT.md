# Project: Synapse-IA Radio Fix

## Architecture
The synapse-ia project features an M2 Touch Dashboard (HTML/JS front-end) which plays music/radio streams.
- **Frontend Configuration**: `stations_data.js` contains a JavaScript object `window.STATIONS_DATA` defining categories and stream URLs.
- **API Backend**: `m2_status_api.py` serves the list of stations dynamically from `radio_results.json` at `/radio`.
- **Intents configuration**: `radio_injector_v2.py` converts `stations_data.js` into Home Assistant configurations (`nasu_intents.yaml` and `configuration.yaml`).
- **Push and Update tools**: `push_to_m2.py`, `update_m2.py`, `update_m2_html.py`, `fix_radio_json.py` push configuration files to the running M2 instance.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| 1 | Exploration & Diagnosis | Find broken radio stations and alternative streaming URLs | None | DONE |
| 2 | Implementation | Update URLs in `stations_data.js`, `radio_m2.json`, `test_radio.py`, and run config injector/update scripts | M1 | DONE |
| 3 | Verification Script | Develop/fix a verification script to validate all URLs (HTTP 200, valid media content type) | M2 | DONE |
| 4 | Verification & Audit | Run verification and Forensic Auditor validation | M3 | DONE |

## Interface Contracts
### `stations_data.js` -> M2 Dashboard
- JavaScript script containing `window.STATIONS_DATA` object mapping categories to arrays of objects: `{ name: string, url: string, ok: boolean }`.
### `radio_results.json` -> `m2_status_api.py`
- JSON representation of `window.STATIONS_DATA` with verification status.
