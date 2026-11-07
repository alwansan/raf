# T4 scoped work — 20261107T0538Z-T4-scheduled-artifact-lease-m7q4
origin: scheduled
baseline_sha: 278485fdf2621e0954b606895e578ef0ee30d6e7
owner: T4
scope: artifact expiry / mouse device-test provenance; no Unity source or release workflow edits.
files: this work record and clients/T4/sessions/20261107T0538Z-T4-scheduled-artifact-lease-m7q4.md only.
hypothesis: Android signed artifacts remain retrievable but are not yet safely preserved in Releases; SHA provenance must remain tied to a1737bd7 rather than live HEAD.
experiment_key: T4-ARTIFACT-LEASE-42296450023
shared_resource: GitHub Actions artifacts (read-only); release publishing owned by T5.
source: https://github.com/alwansan/raf/actions/runs/42296450023
observed 2026-11-07 05:38 UTC: checkpoint 13550196498 2,974,171,581 bytes expires 2026-11-09 23:48:15Z; delivery 13549514149 5,948,365,703 bytes expires 2026-11-09 23:49:06Z; both expired=false.
No equivalent rebuild requested. Release listing latest entries are LogRaft, not evidence of a Raft Android release. Device success belongs exclusively to 42058825739/e9c358eda01785b65e4eb14f18723da426635628.
Next: T5 should preserve both signed artifact archives before expiry, verify APK signing and OBB version/sha from manifest, and provide device-test build provenance; T4 to validate physical mouse capture/cursor/menu transitions without keyboard regression on the exact installed build.
