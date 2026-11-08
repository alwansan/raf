# T4 scheduled evidence review — 20261108T2035Z-T4-scheduled-cl-evidence-r7k4
origin: scheduled
baseline_sha: 28024e36a57c053a79699c90c34c871ce373a40f
scope: INPUT-005 / CL read-only evidence correlation; no runtime or T5 UI changes
experiment_key: T4-CL-SHARED-20261108-230157
shared_resource: none; no CI requested
files: this session and independent INPUT-005 work note only

## Established facts
- Owner 5 Nov artifact 42058825739 entered, saved, exited and re-entered world. Delivery publish failure is separate. Keep LOCAL-005 regression open.
- New CL/main/test/shared-20261108-230157-466487336/summary-20261108-230157-466487336.json is linked to pack_sha256 6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f and app_source 93e32950c521d9890ce845eb8213cd6704cd7f98.
- All nine T4-01..T4-09 entries report NEEDS_INPUT, observed 'User action, mouse/file or judgment is required'; these are not PASS or FAIL and do not establish a mouse event route. The newer shared folder is dominated by T3 image evidence.
- Earlier CL/main/test/t4-builtin-mouse-20261108-191456-452866288/events-20261108-191456-452866288.jsonl contains startup, test_begin T4-01..03, activity pause and MediaStore export, but no button/scroll/capture events; do not interpret absence as device failure.
- Prior T4 route analyzer tests distinguish source mouse vs touchscreen, ACTION_SCROLL vs movement, and button transitions vs state; they do not prove Unity Mouse0/1/2.
- Owner 8 Nov reports physical mouse camera movement improved but left/right/middle/scroll remain broken in Raft; distinguish device report from mini-lab result.

## Next engineering action
Inspect newly uploaded T4 physical-mouse event JSONL from unified APK with test IDs, ACTION_BUTTON_PRESS/RELEASE, ACTION_SCROLL, source, buttonState and capture on/off. Correlate Android View delivery with Unity legacy Input.GetMouseButton/GetAxis to isolate bridge failure. Keep keyboard, .rgd, sound, Settings and T5 UI/resolution untouched. No native build without coordinated gate.
