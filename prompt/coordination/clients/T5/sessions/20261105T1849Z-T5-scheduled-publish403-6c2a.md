# T5 scheduled — Native build succeeded, Release publish HTTP 403

- session_id: `20261105T1849Z-T5-scheduled-publish403-6c2a`
- origin: `scheduled`; status: `completed`
- base_sha: `21891344ae3307816db7c4719b1d38085834b238`
- resumed_from: `20261105T1738Z-T5-chat-release-manifest-6e91`, `20261105T1646Z-T5-scheduled-c71e`
- issue: INTEGRATION-001; independent read-only forensic scope.

## Decisive new evidence

[Native CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) on immutable `e9c358eda01785b65e4eb14f18723da426635628` is now **completed FAILURE**, but **reconstruct job127354763134 SUCCESS**. Actual Unity Editor import/compile step62, private APK structural audit step65, FMOD/data audit step66, signature verification step67, signed checkpoint step68, full APK/OBB/XAPK package step69, and artifact retention step71 all SUCCESS. No claim of on-device functionality.

The separate publish job127441439836 downloaded the real delivery artifact, verified ZIP digest `sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6`, then `gh release create` returned **HTTP 403 Resource not accessible by integration** at `POST /repos/alwansan/raf/releases`. The workflow declares publish-job `contents: write`, so the runner token's displayed permission alone is insufficient to establish actual release-create authorization. Exact repository rule/policy cause unknown. Expected release tag `android-early-test-42058825739-1` was 404 when checked. Downstream delivery-result job failure is consequence of absent publication, not evidence of Unity compile failure.

**URGENT recovery:** delivery artifact ID `13441227298`, compressed size **5,948,243,524 B**, expires **2026-11-06 18:19:05 UTC**; signed checkpoint ID `13441766832`, size **2,974,110,506 B**, expires **2026-11-07 18:18:17 UTC**. Preserve before expiry. Artifact API digest is archive digest, not independently verified signed APK hash. Avoid redundant 2.5h native rebuild. First diagnose Release authorization (repo workflow policy, branch/ruleset, app token permission), then publish existing immutable artifact through an authorized publication-only route with exact hashes, names, sizes and source SHA verification. Do not bypass provenance/signature or publish game raw assets.

## Boundaries and handoff

No CI cancelled or repeated, no Unity workflow/game/.meta/GUID/Steam/audio/Settings/touch changed. Source and signed packaging passed in CI, **no Release** and **no phone/FFT/world/.rgd proof**. NOT_READY 0/3. Work and experiment are independent from T1–T4. Next cycle: recover artifact with authorized publication-only operation before expiry, verify all files, and request phone validation when safe.
