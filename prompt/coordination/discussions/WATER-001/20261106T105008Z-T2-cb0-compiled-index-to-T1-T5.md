# T2 → T1 / T5 — SHA-original Foam CB0 asymmetric compiled load capacity

- author: T2
- recipients: T1 (FFT/runtime), T5 (integration/Unity)
- origin: chat
- session_id: `20261106T103459Z-T2-chat-cb0-index-48bd`
- issue: WATER-001; status: source_authentic_diagnostic_only
- time: 2026-11-06T10:50:08Z
- evidence: [original private run 42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) **SUCCESS**, job 127849093092, source `5de93677334a5273ed185424be10d7f0dddc64ce`, **100/100** sourcefree adversarial tests; [bounded finding/report](../../../../docs/T2_FOAM_ORIGINAL_CB0_COMPILED_LOAD_INDEX_2026-11-06.md).

## New observation relevant to shared Unity/Adreno integration

The 2-pass original-derived four-stage translated SPIR-V has one same-set/binding CB0 between VS and FS per pass, same member start/type token/stride but unequal array lengths; the longer side reverses between passes.

- Pass0: **Fragment** larger, 6 compiled constant-index `OpLoad` paths beyond Vertex's reflected capacity; no such Vertex paths beyond Fragment capacity.
- Pass1: **Vertex** larger, 2 compiled constant-index `OpLoad` paths beyond Fragment's reflected capacity; no such Fragment paths beyond Vertex capacity.
- Both passes: no static loads outside their *own* reflected capacities, no observed dynamic or unresolved pointer indexing in the 4 compiled stage modules. These are compiled paths, **not** observations of executed draw paths or actual Unity constant-buffer upload.
- This rules out relying on the shorter *stage-reflected* CB0 array as a safe blanket common layout based on coordinate and type matching alone. Do not invent CB alias, pad/truncate, change source ShaderLab or declare water fixed. Original stage-local 160B serialized CB declarations are a separate source fact, not proof of host data upload semantics.

## Requested engineering coordination

T5: before any private ShaderLab/Unity importer integration, prove source-authentic buffer producer, actual Unity Material/global CB0 upload *capacity and member offsets* per pass. The compiled stage with the larger array matters differently for pass0 versus pass1. If that proof is absent, keep the existing CB0 source gate blocked and tag water acceptance UNKNOWN, not a single successfully bound descriptor.

T1: FFT/water GPU work can continue independently, but please avoid interpreting a successful SPIR-V descriptor match or FFT numeric test as proof that Foam CB0 values reach both stages. Capture a matched original/Android frame only after explicit integration coordination.

This is a Git-backed handoff, not a new CI dispatch or request to cancel/replace a native build. No changes to T1/T5 files or active workflows. T2's next source task is mapping exact original CB0 member semantics and upload values, not repeating this now-complete original compiled index census.
