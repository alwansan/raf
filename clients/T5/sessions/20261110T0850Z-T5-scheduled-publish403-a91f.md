# T5 session 20261110T0850Z-T5-scheduled-publish403-a91f
origin=scheduled
baseline_sha=704271c8412b7cd56df9d21b9519e4614cb60882
scope_commit=3283de2173d8cebc0b8a5c956278a05d71ac6415

## Verified decisive evidence
Read phone report docs/DEVICE_FEEDBACK_42058825739_AR.md first. Source for device build e9c358eda01785b65e4eb14f18723da426635628. User confirmed world entry/save/re-entry only for this build.
Fetched job list for run 42058825739: reconstruct succeeded, publish-early-test failed at job 127441439836, delivery-result failed downstream.
Fetched full publish job log: actions/download-artifact@v4 successfully downloaded raft-android-test-delivery artifact ID 13441227298, size 5,948,243,524 bytes, and verified ZIP sha256 29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6. The publish script then ran gh release create android-early-test-42058825739-1, which returned **HTTP 403 Resource not accessible by integration** on /repos/alwansan/raf/releases. This is an API authorization failure, NOT an observed package hash or OBB failure. Job token shows Contents: write, Actions: read, but effective integration permissions denied release creation. Do not repeat Unity build for this.
Reference https://github.com/alwansan/raf/actions/runs/42058825739 ; job https://github.com/alwansan/raf/actions/runs/42058825739/job/127441439836 .

## Next actions
Investigate repository Actions workflow permission policy, GitHub App token restrictions and whether release creation is intentionally denied; test release capability via minimal permission-safe API probe or use owner-approved external release path, without rerunning full Unity or weakening gate. Download and inspect delivery.json and signed APK/OBB bytes before claiming package parity. Device FPS baseline 57 samples mean 22.29, HUD 18.27/p95 82.82ms remains historical only. T4 owns mouse, no touch changes. Buttons right and Resolution need device verification; full READY remains NOT_READY.

## Limitations
No phone execution, no binary download, no APK/OBB SHA verification in this cycle. No Unity build triggered. Source files unchanged.
