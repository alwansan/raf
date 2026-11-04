# B21 — Raft Android engineering memory

Session: `20261104T2153Z-B21-72ab` (2026-11-04 UTC). Assigned identity B21; writable branch only `feature/android-native-port`.

## Read and live baseline
Read team PROMPT_AR, README, OPERATING_MODEL_AR, SOURCES_AND_ACTIONS_AR, REVIEW_2026-11-04, TEMPLATES, SUMMARY, AGENTS, owner requirements, continuation, STATUS, ZIP2 provider; latest HEAD at inspection `153787bcb85b0a0af9382b8d19e7dc85c6fc0ee8`. Release `android-early-test-41812889049-1`, actual APK86 source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`; newer repository edits have not been device validated. CL main pin `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`: review reports white materials and zero-kernel FFT/insufficient Spectrum/Foam passes; world SaveGame→SteamUserStats.StoreStats→steam_api64 after WorldHasBeenLoaded. Audio and Settings owner-confirmed working, touch deferred.

## Scope and hypotheses
RENDER-002 P0 distinct lane: lighting/lightmap export integrity and source provenance to separate white material pixels from missing scene lighting. No other current B work registered for LightmapSettings→texture/renderer index chain at inspection. Proposed read-only real-export diagnostic first; fix exact observed provenance defect only, with original GUID/.meta preservation. Existing renderer→material and material→texture/keyword/scalar/color tools are not to be repeated. This hypothesis is **unverified** and must be rejected if no qualifying scene/lightmaps or no proven broken edges.

## Coordination, limits and evidence
Current agents handle Spectrum B09/B17, Foam B24, FFT B08/B30/B48, Blur B45, materials B03/B05/B22/B38/B44/B46, local B07/B12/B13/B14/B19/B50; avoid shared script/workflow writes. Use pinned ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` only when needed, verify size/SHA; archive payload metadata is not authenticated. No game build/run/CI requested yet in this session; no success claimed. Source-only CI cannot prove Android pixels. Running jobs B17 and B24 observed; do not interfere. Read issue files for WATER-001/RENDER-002/LOCAL-005.

## Restore step
Read current HEAD and this work record before modification; inspect original/export lightmaps through available source and live pipeline. If project contains no lightmap binding evidence, record negative result and move to another distinct P0 blocker. Keep memory/state/events truthful; never set READY (currently 0/3).
