# Plan for Synapse-IA Radio Fix

## Milestone 1: Exploration & Diagnosis
- **Objective**: Identify all broken radio URLs and find alternative working streams.
- **Verification**: Subagent `teamwork_preview_explorer` delivers a handoff report diagnosing all URLs.
- **Status**: Active (Conv ID: `2b391c0a-8ca5-4a06-b4e6-ca3da926778a`)

## Milestone 2: Implementation
- **Objective**: Update the broken URLs in all relevant files:
  1. `stations_data.js`
  2. `radio_m2.json`
  3. `test_radio.py`
- **Objective 2**: Inject the new configuration to M2 Touch Dashboard and Home Assistant configurations:
  - Run `radio_injector_v2.py` to regenerate `custom_sentences/es/nasu_intents.yaml` and update `configuration.yaml`.
  - Run `fix_radio_json.py` to write `radio_results.json` and upload config to M2.
  - Run `push_to_m2.py` to push updated configuration files and restart M2 touch GUI.
- **Verification**: Subagent `teamwork_preview_worker` implements changes, runs injector/updater commands, and reports success.
- **Status**: PLANNED

## Milestone 3: Verification Script Development
- **Objective**: Provide a programmatic verification script that check ALL radio URLs configured on the M2 panel, ensuring:
  1. It returns HTTP 200 (or other successful status code < 400).
  2. The Content-Type header matches a valid media/audio stream (e.g. `audio/mpeg`, `application/ogg`, `audio/aacp`, etc. or stream formats like `application/vnd.apple.mpegurl` for HLS).
- **Verification**: Script runs successfully and returns exit code 0 when all URLs are valid.
- **Status**: PLANNED

## Milestone 4: Final Testing & Audit
- **Objective**: Run the verification script, run a Challenger agent to search for gaps, and run a Forensic Auditor agent to verify integrity.
- **Verification**: Challenger and Forensic Auditor confirm correctness and clean verdict.
- **Status**: PLANNED
