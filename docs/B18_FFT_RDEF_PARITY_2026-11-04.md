# B18 original compiled FFT DXBC RDEF/Unity resource parity

2026-11-04; WATER-001. Independent gate for serialized source-to-compiled
program resource identity. Prior inspectors verify original Unity resource
metadata and C# callsite, but had not compared all 20 actual DXBC RDEF reflection
records. B18 tests t0, t1, u0 types/registers/name digests against their
same-slot serialized Unity values; all original game data remains private.
The new synthetic fixture contains no game assets and intentionally falsifies
names, registers, dimension, count, table offsets, UTF-8 and chunk multiplicity.

Source input pinned ZIP2 commit:
15964ea8f246b6e076ce26b60931ee2e1a9a2385.
Original FFT object SHA checked before reflection; compiled DXBC order
cross-checked with original object scan. Scope and status must be taken from
the exact GitHub Actions run; synthetic tests alone do not validate original
binary reflection. This is not game shader integration, kernel runtime mapping,
Unity import, GPU numerical equivalence or phone proof.

Files: scripts/b18_fft_compiled_rdef_bindings.py,
tests/test_b18_fft_compiled_rdef_bindings.py,
.github/workflows/raft-b18-fft-rdef-parity.yml.

No source/asset/GUID/.rgd, native request, audio, Settings, touch or
protected branch changes. WATER-001 remains OPEN. NOT_READY 0/3.
