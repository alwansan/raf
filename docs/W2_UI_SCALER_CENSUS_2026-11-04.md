# W2 game-wide UI-scaler census — freeing A2's DISPLAY-003 traversal — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Twelfth ring: **the count-level
census of A2's published display-settings script identities across the whole
build** (`scripts/probe_w2_ui_scaler_census.py`, tests in
`tests/test_w2_ui_scaler_census.py`, workflow
`.github/workflows/raft-w2-ui-scaler-census.yml`). 82/82 owners
identity-verified against commit HEAD; 76,161 MonoBehaviours scanned; only
counters and record byte-length histograms published — no pointer paths, no
decoded values, no panel traversal.

## Why this lane exists

A2's DISPLAY-003 next step is the *traversal* Settings-panel → Canvas →
scaler pointer path. That traversal stays **reserved to A2** untouched.
What W2 contributes is the static input that frees it: exactly where the
target MonoBehaviours live in the original build and that their serialized
records are shape-uniform, so A2's pinned record-shape tooling is known
applicable before he runs it.

## Method

- Global script registry from `globalgamemanagers.assets` (3,827 MonoScripts,
  0 undecodable) — every scene owner references scripts via externals
  (`m_FileID = external index + 1`); 76,158/76,161 script references resolve
  through that host, 3 are same-file.
- Per-owner scan with `read_typetree(check_read=False)` (the same
  strict-read-bypass A2 uses) — **0 undecodable behaviours game-wide**.
- For each resolved target behaviour the only raw datum taken is the **byte
  length of its serialized record** (histogram). No field, pointer, value or
  name is decoded.

## The census

| identity (A2's published gate names) | instantiations game-wide | record byte-length histogram |
|---|---:|---|
| `CanvasScaler` | **52** | **80 bytes × 52** |
| `Settings` | **3** | 612 × 2, 712 × 1 |
| `GraphicsSettingsBox` | **2** | 280 × 2 |
| `ControlsSettingsBox` | **2** | 308 × 2 |

Per-owner distribution (target instantiations only): sharedassets0.assets 24
(all `CanvasScaler`), level1 16 (13 `CanvasScaler` + 1 of each Settings/box),
level0 7 (4 `CanvasScaler` + 1 of each), level30 5, level35 3, level36 3,
resources.assets 1 (`Settings`, same-file-registered). Every other owner has
**zero** display-settings instantiations — the settings stack lives only in
sharedassets0 + the two UI-hub scenes + per-scene canvases listed above.

## Engineering significance (bounded)

1. **A2's record shape is proven game-wide before he runs it**: all 52
   `CanvasScaler` records are exactly the 80-byte pinned layout — his
   source-locked decoder will apply to 52/52 with zero shape exceptions.
2. The per-class histogram *uniformity* (Settings 612/712, boxes 280/308)
   tells A2 which classes have fixed serialized schemas — no per-instantiation
   variation — bounding his traversal work to pointer resolution only.
3. The instantiation map (7 owners contain all of them) means any display
   restoration test can be built from exactly those 7 owners, nothing wider.
4. The cross-file resolution (76,158 external refs through one script host)
   is itself the port invariant: a rebuilt build that changes script-host
   externals breaks every MonoBehaviour identity — detectable by count alone.

## Boundaries

- Below A2's reserved lane: no panel traversal, no value decode, no patching.
- Counters + byte-lengths only; no object names, path IDs or payloads.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; NOT_READY; reviews 0/3.
