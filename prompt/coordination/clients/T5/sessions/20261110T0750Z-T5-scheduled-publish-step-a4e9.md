# T5 scheduled session 20261110T0750Z-T5-scheduled-publish-step-a4e9
origin: scheduled
scope_commit: 185b95c2559f981335fd7a28c6977a9f5c57dba0
baseline_head: d9ef15c51b7661464df6391921c534bcff1eb7dd
resumed_from: prompt/coordination/clients/T5/sessions/20261110T0551Z-T5-scheduled-artifact-page-audit-k8m2.md
issue: DELIVERY-APK-OBB-42058825739

## New verified finding
Re-read original owner phone report first. Owner device world entry/save/re-entry success remains restricted to artifact from run 42058825739 and source e9c358eda01785b65e4eb14f18723da426635628.
GitHub Actions run jobs endpoint /repos/alwansan/raf/actions/runs/42058825739/jobs?per_page=100 returned five jobs: native-request-gate SUCCESS, unity-license-preflight SUCCESS, reconstruct SUCCESS, publish-early-test FAILURE, delivery-result FAILURE.
The publish-early-test job explicitly reports **Run actions/download-artifact@v4 SUCCESS**, followed by **Publish complete APK OBB XAPK packages and lossless transport parts FAILURE**. The delivery-result failure is the intentional gate **Refuse green native runs with missing build or delivery**. Thus download-artifact stage succeeded and publication stage failed; neither the cause of publication failure nor signed APK/OBB identity is established by the step metadata. Do not misclassify it as reconstruction failure, APK/OBB mismatch, or a phone failure.
Run artifact listing has total_count=4 and four diagnostic entries only; IDs 13441227298 and 13441766832 cited in owner report are not in this run listing. Direct artifact-ID fetch was rejected by GitHub connector allowlist (HTTP 400), **not** by GitHub as nonexistent. Their source run and binary manifest remain unverified. No byte-level APK/OBB comparison possible from these metadata.
Current HEAD at start d9ef15c51b7661464df6391921c534bcff1eb7dd; T4 mouse trace regression CI42776921454 SUCCESS at 2026-11-10 07:40 UTC, source-only and not device button acceptance. No shared Unity job started by T5.
Historical CL metrics: 22.29 estimated FPS/57 samples, HUD 18.27 FPS p95 82.82ms; no new LogRaft or GPU measurement this session.

## Boundary and next steps
Read-only diagnosis plus independent work/session files only. No modifications to game assets, .meta, Settings, mouse, or builds; no new CI. Next: obtain publish job raw failure log or signed checkpoint artifacts using a permitted endpoint/gh CLI; verify archive manifest/versionCode/OBB name+size+SHA256 and signature; then compare to CL device package identity. Inspect existing Resolution implementation and device-test right-side controls without overlapping T4. Preserve NOT_READY 0/3 and owner phone result as historical.
