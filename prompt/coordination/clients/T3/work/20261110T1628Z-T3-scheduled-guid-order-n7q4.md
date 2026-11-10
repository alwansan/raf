# T3 scope — 20261110T1628Z-T3-scheduled-guid-order-n7q4
origin=scheduled
baseline_sha=2af49e6615259530b5e7e39d26419f195adfac05
track=RENDER-002 / ASSET-RESTORE-001
experiment_key=T3-GUID-ORDER-001
files=scripts/t3_unity_guid_link_audit.py; scripts/test_t3_unity_guid_link_audit.py; own session/work files
hypothesis=Unity YAML object references can place guid before fileID; current REF regex silently skips them, undercounting texture/material/shader links.
shared_resource=none; no Unity or APK build.
non_overlap=T4 pointer and T5 resolution untouched; preserve all GUID/meta/rgd.
acceptance=both key orders recognized, no cross-brace mixing, existing counts retained. Static partial tree only; no device proof.
