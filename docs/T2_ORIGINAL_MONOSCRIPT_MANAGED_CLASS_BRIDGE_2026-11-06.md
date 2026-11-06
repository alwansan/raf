# T2 — original MonoScript to original managed Assembly-CSharp TypeDef bridge

**Date: 2026-11-06 UTC · owner T2 · origin chat · WATER-001 OPEN.**

## New engineering question
The previous original [typed target SHA join](T2_ORIGINAL_SCRIPT_TARGET_PROVENANCE_2026-11-06.md) and [strict positive evidence gate](T2_ORIGINAL_MONOSCRIPT_POSITIVE_ATTESTATION_2026-11-06.md) prove 55,328 original opaque scene component `m_Script` PPtrs reference 473 distinct source-original typed MonoScript objects. Yet original MonoScript *class metadata* had not been linked to real managed TypeDef rows, preventing source-authentic reconstruction of custom water component fields.

## Source provenance and method
- Source ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; immutable original 366-row manifest blob `4201fda426d80caba36c275ceaddb440b05c5b4e`. Within that manifest there is exactly one **758,412-byte** MonoScript serialized provider and one **3,211,776-byte** Assembly-CSharp.dll source provider. Each is independently reconstructed and checked against its exact manifest SHA, not filename/size alone.
- Private runner on Ubuntu24.04 uses `UnityPy==1.25.4` to read the original built-in MonoScript `m_AssemblyName`, `m_Namespace`, `m_ClassName` and `dnfile==0.18.0` to read original Assembly-CSharp `TypeDef` namespace and class names. Identity compare is **exact and case-sensitive**. No fuzzy namespace shortcuts, no runtime GUID inference. Original data, names and class paths never leave runner private memory. Outputs are count/bool only.
- `scripts/t2_original_monoscript_managed_class_bridge.py` and `tests/test_t2_original_monoscript_managed_class_bridge.py` with isolated `.github/workflows/raft-t2-original-monoscript-managed-class-bridge.yml`. **18** source-free adversarial tests: duplicate original manifest sizes, wrong DLL path/kind, empty and untrusted names, case and namespace mismatch, duplicate managed TypeDef rows, other assemblies, unreadable metadata and partition accounting.

## CI outcomes
Initial [CI42274792423](https://github.com/alwansan/raf/actions/runs/42274792423) failed in private scratch path setup **before** processing original data (source-free tests 18/18 passed); corrected staging directory initialization at commit `d09d74bd0c0890d02d4122fc7ad80e2175e529bc`. No game bytes or source SHA issue inferred from the setup failure.

**Final [CI42275038330](https://github.com/alwansan/raf/actions/runs/42275038330) SUCCESS**, source files pinned to code commits `b44c5f55899bba22a2da019126a4978084315ca7` + `d09d74bd0c0890d02d4122fc7ad80e2175e529bc`.

| Safe aggregate | Count |
|---|---:|
| Source-original typed MonoScript objects in full target provider | **3,827** |
| Class/namespace/assembly metadata unreadable | **0** |
| MonoScript objects declaring Assembly-CSharp | **1,789** |
| Exactly one original managed TypeDef exact match | **1,605** |
| No exact managed TypeDef match | **183** |
| Ambiguous duplicate exact managed TypeDef | **1** |
| MonoScript objects from other assemblies | **2,038** |
| Original managed TypeDef rows | **3,033** |
| Distinct original TypeDef namespace/class keys | **2,914** |
| Source-original MonoScript target serialized bytes SHA verified | **758,412** |
| Source-original managed DLL bytes SHA verified | **3,211,776** |

Safe report artifact [13532172702](https://github.com/alwansan/raf/actions/runs/42275038330/artifacts/13532172702), **646 bytes**; artifact ZIP SHA256 `7eea596fa9f76f02059142ee3749ed2c72f411ceb8329bbdae24a8d604bfcadc`. This artifact digest is not a game-source digest. Private original source stage purged before upload.

## Strict meaning and limits
We now have source-authentic, exact managed class identity for **1,605** original MonoScript objects in the single provider; **183** exact misses and one ambiguous original class remain **unclassified**, not evidence of corrupt resources. **This is not 1,605 in-scene component matches.** Prior original scene census covered only **473 distinct referenced script PathIDs** among that provider; their intersection with the 1,605 has not been measured in this experiment. No custom MonoBehaviour fields, Unity runtime GUID, Material/Shader creation, CB0/Spectrum/Blur/FFT shader binding, Android graphics pixels, phone performance or world save proof is claimed.

**Next distinct proof:** SHA-authenticate source-original scene m_Script target PathID subset of 473 and join its original class identity to managed TypeDef; then narrow to actual water hosts before any ShaderLab/material implementation. Never use fuzzy name matching to silence the 183 misses. T2 trial round `trial-20261106-r1` remains **«لا يحتاج»** absent integrated substantial Android water renderer improvement. WATER-001 OPEN; project NOT_READY.
