# T2 scope — original Foam source identity
session_id: 20261109T0225Z-T2-scheduled-foam-source-6a91
origin: scheduled
base_sha: b7bd8ca25d7f8a47ad8ef1cfb6638a3b8285f1bd
issue: WATER-001 OPEN
experiment_key: T2-FOAM-ORIGINAL-CFG-20261109

## Read-first evidence
- docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered, saved, reopened world from artifact; water pass and FFT errors remain; delivery publication failed.
- T2 latest session 20261109T0124Z-T2-scheduled-m5q8: marker gate source patched, tests not run due DNS; explicit instruction to stop adding synthetic-only checks.
- T2 state: original Foam CIL CI42519122764 identifies pass0 source as RenderTexture typed field and pass1 source as Texture typed call result after conditional/throw flow; direct pass1 source and runtime texture instance identity still unknown.
- T1 latest source FFT logging proof at HEAD; do not overlap T1 or T3 game shader files.

## Scope and hypothesis
Read-only audit of original Foam pass1 producer/receiver provenance and its missing runtime identity. No game shader or shared build changes. Hypothesis: passing typed call result through a conditional CFG is insufficient to establish the runtime texture feeding the second blit. Next decisive test: pinned original ZIP2 assembly, bounded interprocedural return/phi analysis and a fail-closed trace of texture producer through pass1; verify hashes before extraction and publish only safe summaries. Resource: no Unity, no new CI this cycle. Files: this work note and isolated T2 session only.

## Current result and limits
Confirmed existing evidence is *type/provenance only*, not equality of actual RenderTexture instance, CB0 ABI, sampler or ShaderLab pixel match. Do not mark WATER-001 READY. T4 owns physical mouse, T5 owns Resolution; T3 owns effects. No competing source edits.
