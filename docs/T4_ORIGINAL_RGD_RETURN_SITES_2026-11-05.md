# T4 LOCAL-005 — source-authentic original SaveWorld RGD producer return-site audit

Date: 2026-11-05; worker T4; origin: chat; session `20261105T1713Z-T4-chat-original-rgd-return-sites-j7q4`.

## Why this is a distinct question

The previous source-authenticated [CI42068520588](https://github.com/alwansan/raf/actions/runs/42068520588) SUCCESS 32/32 identified the original SaveWorld RGD-producing callee as a **zero-argument instance method declared by SaveAndLoad with a genuine compiled body**. The world object was passed via a local, with a single lexical store fed by that callee; SaveUser instead uses a SaveAndLoad field with three direct stores. That prior experiment did not inspect the method's return-site and constructor structure.

This experiment asks what the genuine original body contains: lexical ret sites, immediate operand-source classes, direct derived-RGD creation and call-return sites, local slots, conditional branches, null literal loads and explicit throws. These are **syntactic compiled IL counts only**, not execution traces, reachability, SSA/value tracking, or proof of a successful `.rgd` file.

## Proven original input

Immutable owner ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original `Raft/Raft_Data/Managed/Assembly-CSharp.dll`, **3,211,776 bytes** and SHA256 **`0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`**. GitHub workflow revalidates commit, size and SHA before using Mono.Cecil 0.11.5 and refuses one-byte altered source. No original bytecode, private members, game assets, serialized saves, decompiled IL or CLR type identifiers released.

## Authenticated result

[**FINAL CI42072718216**](https://github.com/alwansan/raf/actions/runs/42072718216) **COMPLETED SUCCESS**, tested source SHA `b1203fb30fa91eab56ec0507e720574d7aa75ecf`. **50/50** source-free synthetic/adversarial controls, actual .NET8 C# original inspector compiled and executed read-only against authenticated original DLL, deliberate bad DLL SHA rejected before inspection. Bounded original source report:

| Original SaveAndLoad world factory metric | Static count |
|---|---:|
| Lexical `ret` sites | **1** |
| Immediately preceding a return: derived-RGD local | **1** |
| Return immediately preceded by `ldnull` | **0** |
| Return directly preceded by derived field / call / constructor / unknown | **0** each |
| Local slots whose declared type derives from `RGD` | **2** |
| Direct constructor calls producing derived-RGD types | **1** |
| Direct method calls with derived-RGD return type | **1** |
| Conditional branch instructions in factory method | **34** |
| `ldnull` literal-load instructions in factory method | **10** |
| `throw`/`rethrow` instructions | **0** |

The one return loads a derived-RGD local. The genuine compiled factory contains a derived-RGD constructor site as well as an additional derived-RGD-returning call site, but **no assertion is made that the constructor or call assigns the returned local**. Thirty-four conditional branch sites and ten `ldnull` instructions do not identify paths that reach the return, nor imply that a null or non-null RGD is actually returned in any particular world state. No explicit throw instruction is not an absence of possible exceptions from called methods.

**Critical negatives enforced by the verifier**: `factory_control_flow_paths_or_runtime_values_proven=false`, `derived_RGD_runtime_value_initialized_proven=false`, `same_world_saved_or_reopened_proven=false`, `Android_Unity_IL2CPP_phone_executed=false`. No gameplay methods executed, no original .rgd read or written, and no Android device testing.

## Reproduction and safety

The narrow additive inspector is `android-port/Experiments/T4/OriginalRgdInitContext/Program.cs`, commit `a5dec4b734725969ece9ade9cc589bcb71d60883`. The fail-closed original-free report validator is `scripts/t4_validate_original_rgd_init_context.py`, commit `3cbee8c415d9ad289acc90ff422e70b439d8e7a7`. Test suite `tests/test_t4_validate_original_rgd_init_context.py` (32→**50**, 18 new) updated at `5772262d51b36dec657a5520ca3407270215c025` and `b1203fb30fa91eab56ec0507e720574d7aa75ecf`. Existing isolated path-scoped workflow `.github/workflows/raft-t4-original-rgd-init-context.yml` reused, non-cancelling, no original game data artifacts.

Three transitional CI runs [42072414751](https://github.com/alwansan/raf/actions/runs/42072414751), [42072490701](https://github.com/alwansan/raf/actions/runs/42072490701) and [42072568029](https://github.com/alwansan/raf/actions/runs/42072568029) failed under mixed report/test schema while staged edits were being published. The last was an outdated synthetic acceptance test for unresolved external producer, now correctly rejected by the stronger exact-original-body requirement. **None is an Android, serializer, Unity or game runtime failure.** Matched final CI above passed all tests plus actual source analysis.

## Coordination and remaining game acceptance

T4 scheduled session `20261105T1640Z-T4-scheduled-r8k2` separately owns JSONL overflow evidence integrity, not changed here. T5's immutable native candidate [CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) was still **in_progress** in Unity Editor Android import at start, not cancelled or duplicated by T4. Last verified actual game Release is APK86; no T4-produced signed APK/OBB/XAPK or phone proof.

Next experiment should investigate **the local-slot assignments reaching the single return** using bounded source-only def-use/branch ambiguity checks, not blindly replace original data structure or invent RGD. Runtime acceptance still requires actual offline playable world → genuine saved world/user `.rgd` on disk → full process exit → reopen same world playable in the new native APK/OBB/XAPK. Preserve original save format, local-host path, GUIDs/.meta, existing B50 Steam guard, working audio/Settings, deferred touch. **LOCAL-005 OPEN; NOT_READY 0/3.**
