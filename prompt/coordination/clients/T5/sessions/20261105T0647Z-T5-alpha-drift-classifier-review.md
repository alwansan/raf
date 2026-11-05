# T5 session 20261105T0647Z-T5-alpha-drift-classifier-review
Status: active; resumed from 20261105T0554Z-T5-ci-boundary-forensics (paused).
Baseline HEAD: 388b5317780f438667cbb62351ba999fbbcc153c.
Scope: independent diagnosis of the 30/106 genuine decoded RGB mismatches; inspect T3 aggregate classifier without changing T3-owned scripts.
Hypothesis: alpha-only differences may be mislabeled RGB_1 by the existing diagnostics; verify with minimal synthetic control and record actionable evidence. Do not claim this explains 30 genuine RGB mismatches.
CI baseline: T3 41968665857 failed decoded-pixel parity; T1 41978496060 failed pre-FFT Unity activation. No active runs among latest 30 fetched; no cancellation.
Source: zip2 pinned 15964ea8f246b6e076ce26b60931ee2e1a9a2385. Device evidence unchanged APK86; NOT_READY 0/3.
