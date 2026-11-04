# W2 completes A2's DISPLAY-003 serialized-route gap — the Settings→CanvasScaler route is proven — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`, acting under the owner's explicit
take-over directive for the paused A-clients. This ring **completes A2's
paused DISPLAY-003 open gap** ("instantiated Settings UI→CanvasScaler route")
that A2's managed TypeDef work had explicitly left unresolved
([report](W2_UI_SCALER_CENSUS_2026-11-04.md) fed A2's static inputs; this
report finishes the route itself).

Deliverables: `scripts/probe_w2_settings_panel_route.py`,
7 fail-closed synthetic tests
(`tests/test_w2_settings_panel_route.py`), workflow
`.github/workflows/raft-w2-settings-panel-route.yml`. Owners
identity-verified against commit HEAD. Publication is counters only — no
GameObject names, no path IDs, no settings values.

## The proven instantiated route (count level, both scenes)

For the two scene-embedded Settings manager instances (level0, level1):

1. The Settings component sits on a **root GameObject** (plain `Transform`
   manager node — component family: Transform + Settings + MyInput +
   LocalizationParameters + CharacterManager). No canvas above it
   (`canvasAncestorsAbove = 0`).
2. **Directly one hop below the manager root** hangs a full-page UI Canvas
   whose node carries **CanvasScaler + GraphicRaycaster siblings**
   (`canvasScalerOnCanvasNode = 1/2 instances`).
3. **Three hops below that Canvas node** sit exactly the
   `GraphicsSettingsBox` and `ControlsSettingsBox` settlement panels — the
   serialized settings pages.
4. Route census totals: 90 Canvas objects in the scanned owners
   (level0 4, level1 56, sharedassets0 30, resources 0),
   **41 scaler-sibling canvas nodes** — which exactly reconciles with the
   41 CanvasScaler instantiations in those owners (4 + 13 + 24); the
   remaining 11 canvases-with-scaler live in level30/35/36 with **zero**
   settings-family content. `gameWideScalerCanvasesWithSettingsFamily = 2`
   — only the two Settings manager pages.

## Secondary structural findings (A2's next-stage inputs)

1. **The resources.assets Settings instance is dangling**: its
   `m_GameObject` PPtr is null — a hierarchy-less template asset, never
   parented in any scene. A2's Byte-pattern work on that instance is
   prefab-template material, not panel material.
2. The Settings manager *itself* is 2-subtree-only — the false-negative
   census from the first run (children edges point at **child
   RectTransforms**, resolved to GameObjects through their `m_GameObject`)
   is itself the reason A2's pointer-window scans over raw bytes couldn't
   close the route: the naive child-edge assumption is wrong in this build.
3. All other scaler canvases (the 41 - 2) contain **zero** Settings-family
   components in their entire subtrees — dedicated scaler canvases
   elsewhere (HUD, container canvases etc.) — so any A2 offset work on the
   settings pages is guaranteed to apply to exactly the 2 proven routes.

## What this resolves and what stays A2's

Resolved by this ring: the serialized-form existence and exact topology of
the instantiated Settings UI→CanvasScaler route (A2's explicit unfinished
gap). Stays with A2: typed offsets, full custom Settings TypeTree lengths,
Android orientation-stretch root cause (value-level analysis he owns).

## Boundaries

Follows the owner's take-over directive; A2's session files updated with a
clearly-attributed W2 section. No device/Unity/APK claims. Project
**NOT_READY 0-of-3**; WATER-001 / RENDER-002 / FFT-FORMAT-009 OPEN.
