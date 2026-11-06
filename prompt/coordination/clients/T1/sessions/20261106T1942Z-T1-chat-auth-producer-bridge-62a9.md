# T1 — original FFT signed-Input versus translated loop-Phi source-evidence bridge

- **session_id:** `20261106T1942Z-T1-chat-auth-producer-bridge-62a9`
- **origin:** `chat`
- **base_sha:** `83eb4f1f90c1436afc5c529c525791f50ac0b068`
- **resumed_from_sessions:** `20261106T1933Z-T1-chat-zero-coordinate-signature-73e1`; `20261106T1916Z-T1-chat-address-provenance-e6b2`; `20261106T1850Z-T1-chat-gpu-input-join-b71c`.
- **issue:** WATER-001 **OPEN**; game readiness **NOT_READY 0/3**; T1 trial vote `trial-20261106-r1`: **لا يحتاج** unchanged.
- **status:** scoped source-only evidence bridge **completed** with [Actions 42283086865](https://github.com/alwansan/raf/actions/runs/42283086865) SUCCESS (14/14).
- **work:** `prompt/coordination/work/WATER-001/20261106T1942Z-T1-chat-auth-producer-bridge-62a9.json`
- **experiment:** `prompt/coordination/experiments/T1/20261106T1942Z-T1-chat-auth-producer-bridge-62a9.json`
- **event:** `prompt/coordination/B_TEAM/events/T1/20261106T1942Z-T1-chat-auth-producer-bridge-62a9.json`.

## Live recovery and noninterference

Read T_TEAM RESTORE_AR, CHAT_AND_SCHEDULE_AR, trial votes and latest T1 chat+scheduled sessions through 19:33Z. At startup live HEAD `c97252e137ef153d53d88c47fb5d42747e36d142`, rechecked HEAD `83eb4f1f90c1436afc5c529c525791f50ac0b068` before source reservation. `Raft full native APK OBB XAPK build and delivery` [42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) was **in_progress** at beginning, reconstructing original resource payloads after native-request gate and Unity license preflight success. No other nonterminal Actions at initial read. To avoid competing with the native build, this chat selected **source-only 4-minute Python tests**, no full Unity, ZIP2 download, project patch, native request, artifact or private assets. Did not cancel/override other clients. Reserved independent work before code edits in [f0e3b10e](https://github.com/alwansan/raf/commit/f0e3b10e73817bf90e50330fa0db683df3c2bc39).

## Rechecked REAL prior original, translated, synthetic evidence

Inspected actual decoded terminal job logs and run SHA (not assumed from stale state):
1. [Original SHA-source Vulkan 42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) source `00a9157d69ba7bdbca9ba9d9cd1d8881feb1fe3f`, job `127901229510`, **SUCCESS**. Safe `RAFT_T1_FFT_BUTTERFLY_X_WRITER_LINEAGE` marker for site=1, role=butterfly, coordinate=x lists one reachable final whole-vector writer from `OpVectorShuffle → OpBitcast → OpVectorShuffle → OpLoad`, cast `sint32_bits_to_float32`, a `sint32_vector` **Input** storage load boundary. No unknown alias, pointer escape or uninitialized path within bounded static analysis. Marker still reports `complete_proof=false`, `original_numeric_semantics_proven=false`.
2. [SHA-original-derived HLSL roundtrip 42228497335](https://github.com/alwansan/raf/actions/runs/42228497335) source `e936ad1f96c0bb0617a7a7199c2304c5f47442ff`, job `127928005249`, **SUCCESS**. `RAFT_T1_FFT_HLSL_NESTED_PHI_X` site=1 selects `float32_vector` Phi, two incoming edges, one structural CFG loop/backedge; noncyclic typed source traverses bitcasts toward `uint32_vector` **Private** storage load boundary. `selected_runtime_predecessor_proven=false` and `actual_original_vs_unity_numeric_parity_proven=false`.
3. [Real Unity2021.3.45f2 OpenGLCore sourceFREE 42279949574](https://github.com/alwansan/raf/actions/runs/42279949574) source `93f27342d4b2c46d811c6c16a2672d9a247f346a` **SUCCESS**. Synthetic calculated integer-address carrier had 63/64 signed-zero signatures and x0 texture samples in each of 5 diagnostic paths, while matched buffer-staged carrier had 0/64 in all 5, 6 positive controls passed. Does **NOT** execute Raft original shader or Adreno GPU.

These are three separate, genuine prior CI contexts but NOT a same-runtime paired original-vs-Unity trace. Different terminal storage classes could be semantically equivalent through intermediate copies; a translated `OpPhi` does not establish which predecessor was selected during actual GPU execution. This is **not** sufficient to patch actual Raft shader or explain water failure as FTZ.

## New safety/engineering files and results

Published:
- `tests/data/t1_fft_original_phi_evidence_public.json` commit [e1626586](https://github.com/alwansan/raf/commit/e162658679b56f2b98bd1265a89328e5c9f053cc): only selected safe public opcode-family / storage-class / typed producer categories and pinned historical run/commit IDs. No private original or translated shader bytes, pixels, raw original SHA secret values, numeric coordinates or private debug identifiers. **Manual transcription does not cryptographically authenticate the source log**.
- `scripts/t1_fft_original_phi_bridge.py` commit [f4cf3d9f](https://github.com/alwansan/raf/commit/f4cf3d9fe45df18f22949336724313e8654ff159): strict max4096 byte JSON gate, duplicate rejection and fixed schemas/IDs/commit SHA/source ZIP2 pin; verify original site1 X Input signed32 vector via bitcast, no uninitialized/alias path, candidate uint32 Private noncyclic Phi + loop-carried float32 Phi, synthetic Unity2021/OpenGLCore 63/0 computed vs buffered zero-signature matrix and explicitly disallow promoted runtime/Adreno/FTZ causal flags. Whitelisted **aggregate-only** result `original_input_bitcast_vs_translated_private_loop_phi_gap`, with `source_report_authenticated_by_this_gate=false`, `original_candidate_numeric_parity_in_Unity_proven=false`, and required next actual keyed capture.
- `tests/test_t1_fft_original_phi_bridge.py` commit [4f8678c1](https://github.com/alwansan/raf/commit/4f8678c15469291db7bebbc3b5af35e7b438f353): **14 adversarial tests** spanning honest baseline, pinned source/commit, fake runtime claims, mismatched site/type/phi/CFG/alias, changed synthetic zeros, malformed/duplicate/unbounded/unsafe JSON and symlink, stdout private redaction.
- `.github/workflows/raft-t1-fft-original-phi-bridge.yml` commit [73e40fbb](https://github.com/alwansan/raf/commit/73e40fbbc591557cf8150f7bb36743acd8e22de5): Ubuntu24.04 4-minute, contents:read, 100% public sourcefree checkout, no Unity license/assets, `cancel-in-progress:false`. A concurrent branch HEAD update returned an expected-lease 409 on first create; re-read HEAD/Actions/script+tests then re-created without force. CI auto-triggered.

### Actual source-only CI proof

[Actions **42283086865**](https://github.com/alwansan/raf/actions/runs/42283086865) @ `73e40fbbc591557cf8150f7bb36743acd8e22de5`, job `128116844932`, **COMPLETED SUCCESS**, parsed decoded logs: `Ran 14 tests ... OK` and `RAFT_T1_FFT_ORIGINAL_PHI_BRIDGE` safe result:
```json
{
  "status": "original_input_bitcast_vs_translated_private_loop_phi_gap",
  "original_source_boundary": "sint32_input_vector_bitcast_to_float32",
  "candidate_source_boundary": "uint32_private_vector_through_float32_loop_phi",
  "synthetic_computed_carrier_zero_signature_lanes_per_path": 63,
  "synthetic_buffered_carrier_zero_signature_lanes_per_path": 0,
  "candidate_runtime_phi_branch_known": false,
  "source_report_authenticated_by_this_gate": false,
  "original_candidate_numeric_parity_in_Unity_proven": false,
  "translation_is_cause_of_water_failure_proven": false,
  "original_runtime_kernel_mapping_proven": false,
  "android_adreno_water_proven": false
}
```
No Unity2021 or original Raft GPU execution in this cycle, no original graphics shader code imported, and no Android APK built.

## Strong next action

An **authorized private original-vs-Unity keyed run** must pin ZIP2 original `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, capture **actual** source/butterfly images and dispatch SHA separately for original Vulkan and Unity2021, run exact same input/variant, record dynamic selected Phi predecessor or invocation-keyed per-site read coordinates, require the Unity `T1PrivateFftInputIdentityTests.cs` GPU CopyInput verification and compose with `scripts.t1_fft_private_unity_input_join`. This can test whether first butterfly X really follows the zero-carrier path, not merely a static Phi or compiler possibility. Do not reproduce synthetic 63/64 canary again, do not make up an original runtime FindKernel mapping, and do not replace production water shader without real numeric parity and binding proof. Keep native 42281310905 intact. T1 vote `لا يحتاج`; WATER-001 OPEN and NOT_READY 0/3.
