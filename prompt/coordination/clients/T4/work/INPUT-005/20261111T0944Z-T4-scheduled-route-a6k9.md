# INPUT-005 — 20261111T0944Z-T4-scheduled-route-a6k9
origin=scheduled
baseline_sha=402dc2cfef0d322611f1903b301b5ab2a004be5e
scope=source-only pointer-capture route audit; no Unity/Settings/Resolution edits
files=prompt/coordination/clients/T4/work/INPUT-005/20261111T0944Z-T4-scheduled-route-a6k9.md; prompt/coordination/clients/T4/sessions/20261111T0944Z-T4-scheduled-route-a6k9.md
hypothesis=Native captured callback can record buttons while Raft legacy readers remain unobserved; distinguish callback from game consumption before modifying routing.
experiment_key=T4-callback-to-reader-gap-20261111
shared_resource=none; no CI or native build
owner_device_evidence=42058825739 world create/save/reopen confirmed only; mouse clicks and wheel not confirmed
prior=20261111T0842Z-T4-scheduled-callback-route-j4n8.md; CI 42974039265 source tests passed.
next=inspect same-session physical_mouse_captured_action_callbacks and physical_mouse_legacy_reader_evidence; if callbacks exist but readers absent, audit all gameplay Input.GetMouseButton* call sites before changing listener return semantics.
