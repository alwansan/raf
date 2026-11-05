# T3 independent session 20261105T0625Z-T3-pixel-drift-differential

Identity T3 only; resumed_from_session 20261105T0529Z-T3-real-pixel-drift-triage. Baseline HEAD c8fb81e9d1c3e7db974b5c1474ca1c7ab2471677 at 2026-11-05T06:09Z. Shared state/MEMORY not overwritten: possible overlapping T3 sessions; no same-name session proven inactive. No other agent jobs canceled.

## Verified inherited evidence and plan BEFORE code
Authentic ZIP2 streamed Texture2D comparison CI41968665857: 106 authenticated source/export pairs, 76 EXACT, 30 RGB_DRIFT, no alpha-only, orientation or dimensions differences; original .resS three files size+SHA locked by workflow. NOT_READY; RENDER-002 OPEN. Inherited original/export material 41/41, 227 TexEnv/UV, 150 color slots and 106 sampler fields pass; do not repeat.

Plan: implement privacy-preserving per-texture differential classification in the existing authenticated original-vs-export decoded pixel runner: original Texture2D format and color-space metadata, alpha occupancy, per-channel maximum delta and magnitude bins, plus transform hypotheses (gamma, premultiply) tested but NEVER applied. Emit only aggregated safe buckets and counts; retain exact failure exit when any drift. Add deterministic tests including RGB under zero-alpha. Use a separate optional diagnostic report rather than raw assets, GUIDs, names or pixel values. Validate locally; only then consider another SHA-locked private export run, without disrupting existing workflows.

## Status
IN_PROGRESS at registration. Source edit not yet started. Scope excludes Unity/device claims, game assets, audio, Settings, touch, world and .rgd.
