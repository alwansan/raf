# T3 RENDER-002 — cross-strata RGB drift attribution
session_id: 20261107T1528Z-T3-scheduled-cross-strata-n3f6
origin: scheduled
baseline_HEAD: b24449923cc9ef75dce7c61c1009720dbc8b7132
scope: scripts/t3_rgb_drift_strata.py; tests/test_t3_rgb_drift_strata.py; unique T3 session markdown.
experiment_key: T3-RGB30-FORMAT-SRGB-CROSS-20261107
shared_resource: none; no Unity/CI dispatch; no raw game data.
Hypothesis: marginal format/sRGB tallies cannot distinguish joint combinations responsible for 30 RGB mismatches; bounded aggregate cross-strata can, without disclosing paths or pixels.
Existing evidence: 106 pairs, 30 RGB drift, 76 exact from authentic export CI41968665857; individual metadata missing in published artifact. This patch only improves subsequent private-manifest diagnosis, not phone rendering.
Overlap: independent of T1/T2 water, T4 mouse and T5 resolution/package; recheck latest HEAD before source update.
Acceptance: cross-strata counts sum to total, known/unknown categories handled, no raw identity emitted; regression test on synthetic pairs.
