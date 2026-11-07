# T3 scope: private original/export RGB pair provenance

session_id: 20261107T1732Z-T3-scheduled-pair-provenance-v7m4
origin: scheduled
track: RENDER-002
baseline_head: d06d8f9858768645438a1020a2e10ffdf08e2004
experiment_key: T3-private-rgb-pair-source-provenance-v1
shared_resource: none (no Unity/ZIP2/Actions launched)

## Scope and hypothesis
Only this work file and unique T3 session file. Diagnose whether the 30/106 RGB-drift originals from CI41968665857 can be classified with authenticated per-pair source/export metadata, without leaking original game bytes. Do not touch T1/T2 shader or water files, T4 mouse, T5 Resolution/delivery, shared vote, original assets or metadata. The public three JSON summaries lack per-pair format/sRGB: no source-level root cause can be inferred from aggregates.

## Acceptance contract for future private extraction
1. Pin all nine ZIP2 provider SHA256 and exporter tool SHA, and require same-instance original/export pairing by stable original owner+pathID, with one-to-one cardinality and no duplicate or unpaired identity.
2. Record true source texture format, source sRGB and exported importer sRGB separately; preserve unknown values as null, never substitute defaults.
3. Prove original/export pixel dimensions and alpha equality before categorizing RGB drift. Pixel comparison must use explicit decoding and color-space interpretation; a byte mismatch alone does not prove visually wrong RGB.
4. Run scripts/t3_rgb_drift_strata.py --require-drift-metadata on private per-pair rows, and publish only aggregate counts/strata plus pinned code and provider digests. No raw textures, paths, hashes of individual game assets, or identifying pathIDs in public logs.
5. Map only affected material and ParticleRenderer references to shader GUID, passes, alpha/blend, keywords, lighting; keep evidence labels separate: source/export parity != Unity import != Android GPU pixels.

## Verified blockers and next execution
The current public aggregate is 106 paired textures with 30 RGB differences, but no individual format/sRGB fields; thus --require-drift-metadata cannot validly run on it. Earlier 41 selected Material identities passed 227/227 UV and 150/150 RGBA source/export parity (CI41939404454 and CI41940350604); this rejects some pointer/tint-loss hypotheses, not white/square-smoke shader issues. Next: instrument the *private exporter* rather than add more synthetic classifier tests. No APK or workflow duplication without current overlap and resource checks.
