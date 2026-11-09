# T2 scheduled — Foam CIL DUP ambiguity fail-closed
session_id: 20261109T1024Z-T2-scheduled-dup-boundary-p8r4
origin: scheduled
branch: feature/android-native-port
baseline_sha: b3076af45843798950314d654f5bad51fb5f5059
scope_commit: 13e9a88b3f2c2bcfd00aa64a8c504f9b1130cf2d
source_commit: 9afeaf26933fae814fb2d1c0eaf1d22817967273
work: work/experiments/20261109T1024Z-T2-scheduled-dup-boundary-p8r4.md
resumed_from: clients/T2/sessions/20261109T0851Z-T2-scheduled-alias-ci-h4q8.md

Read owner phone report, AGENTS, requirements, STATUS, T_TEAM protocols, state/MEMORY and recent sessions. Owner artifact 42058825739 confirms world/save/re-entry; water/FFT failures remain. T2 alias fixture CI 42589085141 succeeded. Latest inspected eight Actions show T5 PNG byte regression 42597471313 failed; do not claim this is water.

Source repair: In original managed CIL Foam Blit backward stack tracer, DUP encountered with depth<2 previously set depth to zero and continued backwards, allowing a later unrelated producer to be classified. Changed this path to fail closed with source-free dup_alias_ambiguous reason. Preserves normal DUP stack accounting when depth>=2. The resulting source was re-fetched and string-level checked: true. No original private assembly executed, no dotnet compilation, no Unity/phone tests. The patch is conservative and not an original texture alias proof.

WATER-001 OPEN / NOT_READY. No ShaderLab, original resources, T3 effects, T4 mouse, T5 Resolution or mini APK changes. Next: add a real Mono.Cecil fixture with DUP stack ambiguity and run dotnet regression; then execute SHA-pinned original CIL analysis in private runner with sanitized output and verify Foam pass0/pass1 object provenance. Do not infer object identity from static type or CFG adjacency.
