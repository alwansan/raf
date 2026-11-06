# T5 — Prevent short-lived native APK/OBB loss after Release HTTP 403 (6 Nov 2026)

## Real blocker and scope

The owner-tested native candidate was reconstructed at [Actions 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358eda01785b65e4eb14f18723da426635628` (native build run number and APK `versionCode=89`). Exact native job `127354763134` **succeeded**, producing the original signed APK and OBB plus delivery parts, but publication job `127441439836` **failed** at `gh release create` with **HTTP 403 Resource not accessible by integration** for `POST /repos/alwansan/raf/releases`. The job already requested `permissions: contents: write` and `actions: read`. A YAML permission request alone cannot override effective GitHub installation or repository policy.

The old `raft-android-test-delivery` Action artifact retention in the native workflow was **1 day**; signed checkpoint and audited fallback were **2 days**. This was an avoidable recovery risk once Release creation failed. It necessitated a separate real 5.95 GB delivery rescue in [42110297871](https://github.com/alwansan/raf/actions/runs/42110297871) which verified all 7 transport parts + 3 complete APK/OBB/XAPK SHA-256s and re-retained an exact original ZIP (artifact **13454900880**, expires **2026-11-08 21:12:40 UTC**). Verified subsequent genuine [APK+OBB CI42117471172](https://github.com/alwansan/raf/actions/runs/42117471172) proved the original matching package/version and APK signature. **These are the original build's bytes, not newer P0 shader/FFT fixes.**

## Source-side production delivery improvement

In `.github/workflows/raft-unity-editor-android-import.yml`, changed only three existing `actions/upload-artifact@v4` retention-day settings:

| Original output | Previous retention | New retention |
|---|---:|---:|
| `raft-android-test-delivery` (APK/OBB/XAPK transport, manifest and reassembly) | 1 day | **3 days** |
| `raft-android-signed-output-checkpoint` (signed APK and original OBB) | 2 days | **3 days** |
| `raft-android-audited-output-recovery` (fallback when packaging fails) | 2 days | **3 days** |

The change does **not** make another 6 GB duplicate, alter payload bytes, weaken signature/manifest checks, alter artifact names, extend an artifact already uploaded, or alter Unity source, native request or release permission settings. GitHub storage billing and repository retention policy still apply. Three days is a bounded recovery window, not a durable public Release.

In `publish-early-test`, `GH_TOKEN` now selects `secrets.RAFT_RELEASE_TOKEN || github.token`. This is an **optional, owner-provisioned token path**, not a presumed elevation or a request to reveal a secret. Without the secret, the workflow uses the same `github.token` and may still fail HTTP403. A configured fine-grained token must have access to **alwansan/raf** and **Contents: Read and write** (subject to GitHub policy) to create the Release and upload assets. The owner can create the repository Actions secret called `RAFT_RELEASE_TOKEN` via GitHub Settings → Secrets and variables → Actions, never copying it into source or chat. Deployment should be evaluated under the owner's policy and run logs; no token capability has been exercised in this source-only experiment.

**The native result remains fail-closed**: `publish-early-test` still aborts on `gh release create` or mismatched remote release assets; `delivery-result` requires `publish-early-test.result == success` on the delivery lane. No green run, fake Release URL or auto-ready claim is made when HTTP403 persists. A later authorized job must prove a real reachable GitHub Release by checking remote asset inventory, exact file names and bytes.

## Verification

Added `tests/test_t5_native_delivery_fallback_policy.py` with source-free success and mutation/failure controls for three-day retention, original upload flags, exact release token precedence, branch gating, remote asset equality and strict delivery-result handling. Added isolated `.github/workflows/raft-t5-native-delivery-fallback-policy.yml`, max 5 minutes, branch-limited, read-only, no LFS, no Unity/license, no APK/OBB downloads and no Release creation. This guard runs when the actual source workflow or test is changed, not as a native build request.

- Real source-only CI: [42153075428](https://github.com/alwansan/raf/actions/runs/42153075428) — final conclusion must be checked and recorded.
- Original native Release failure: [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739).
- Retained already-tested original artifact: [42110297871](https://github.com/alwansan/raf/actions/runs/42110297871).

## Follow-up / acceptance boundary

On the **next explicitly coordinated native build**, check three retention-day settings and independently verify the full delivery artifact before it expires. Only report a published Release when `gh release view` and the remote asset inventory match. If HTTP403 persists, the job stays failed and the 3-day artifact gives a bounded manual recovery opportunity. For a durable public release, the owner needs authorized workflow token policy or a securely configured token; the source patch alone does not resolve access policy.

No game runtime, assets, shader/water/FFT, Settings/audio/touch, T1 FFT/Vulkan live comparison, T2 Foam private source, T3 materials, T4 local-save/input, LFS, source ZIP2, or existing 5.95GB artifact was modified. This scope is **native artifact recoverability and publisher authorization only**. WATER-001/RENDER-002 and gameplay/device acceptance remain open; overall **NOT_READY 0/3**.

- T5 chat session: `prompt/coordination/clients/T5/sessions/20261106T0248Z-T5-chat-native-delivery-retention-e8a3.md`
