# Original User Request

## Initial Request — 2026-07-13T19:58:38Z

# Teamwork Project Prompt

Fix or replace the non-functioning radio stations on the M2 panel in the `synapse-ia` project. The goal is to ensure all available stations stream correctly. If a station's URL is dead, the team should actively search for and implement an alternative streaming URL for the same station.

Working directory: /home/pirate/docker/synapse-ia
Integrity mode: demo

## Requirements

### R1. Fix Broken Radios
Identify all non-functioning radio streams in the M2 panel and replace them with valid, working stream URLs for the corresponding stations.

### R2. Web Search Access
The team is permitted and expected to use the web to search for alternative radio stream URLs.

## Acceptance Criteria

### Verification Script
- [ ] A programmatic test or script is provided that checks every radio URL used in the M2 panel, ensuring it returns an HTTP 200 status code and points to a valid media stream.
- [ ] All configured radios pass this verification script.
