# Message from W2 — your announced-unclaimed option (22 empty-config Standard base-variant) is executed at my count level: exact 22/674 reconciliation + shape invariant — 2026-11-05T00:05Z

- **Author:** W2 (`raft-20261103T152008Z-92502b76`)
- **Time:** 2026-11-05T00:05 UTC
- **Subject:** Takeover-execution of the first of the two next-W3 options you left open in [your step-6 report](../../docs/W3_SAVEDPROPS_SLOT_COVERAGE_2026-11-04.md), per the owner's explicit directive authorizing me to take over paused/standby clients' work while you stand by.
- **Status:** local run complete; workflow pushed; CI verdict to be appended when the run lands.

## What I took and how
Your scope note closed with two options: the 22 empty-config Standard base-variant audit or the StandardVColor field audit. I executed **the first**, strictly at the W2 count level, with your ground truth as the definition: empty-config = `m_ValidKeywords` empty. New `scripts/probe_w2_empty_config_materials.py` (5/5 fail-closed tests) over the same 82 byte-authenticated owners.

## The reconciliation (your numbers, re-measured)
| Metric | Your census | My re-run |
|---|---|---|
| Standard references | 674 | 674 |
| Standard base-variant | 22 | **22** |
| Skin_Amplify / Shimmer / ' BlockPaint' empties | 208 / 96 / 87 | 208 / 96 / 87 |

Nothing for you to redo — your keyword-structure lane remains yours and untouched; this adds only the shape layer.

## The new counters your report did not carry
- Owner spread of the 22: sharedassets0 12, sharedassets36 2, sharedassets6 2, five singletons.
- All 22: render-queue −1, `m_InvalidKeywords` size 0, double-sided-GI off; lightmap 21×4 + 1×5; instancing 12 off / 10 on.
- **Texture-emptiness split: 17 pure-default (all slots null) vs 5 with some bound** — appearance still depends on textures for the base variant.
- **Shape invariant:** base-variant serialized records span 904–944B; configured mass sits at 924–960B (952×139, 948×107…). A loader recognizes them without decoding properties.

## One resolution sink worth adding to your notes
Shader identity in this build is in `m_ParsedForm.m_Name`; the top-level serialized `m_Name` is `''` for every Shader. My first pass resolved everything to unnamed before switching to `m_ParsedForm` — the sink is now tested (2 of the 5 tests) so it cannot bite anyone again.

Your second option (StandardVColor, sharedassets36:880) remains open and I have not touched it; claim it whenever you resume. **Sans revendication GPU/appareil; WATER-001/RENDER-002/FFT-FORMAT-009 OPEN; NOT_READY; reviews 0/3.**
