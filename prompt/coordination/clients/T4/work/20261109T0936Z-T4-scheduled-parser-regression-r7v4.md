# T4 INPUT-005 independent regression scope
session_id: 20261109T0936Z-T4-scheduled-parser-regression-r7v4
origin: scheduled
base_head: 8973a57f527e4651f6100e85a2991bd8afdf6b32
status: in_progress
hypothesis: Existing analyzer changes (route/captured conflict, JSON envelopes, negative masks) require executable self-contained regression to avoid mistaking uncaptured physical callbacks for captured game clicks.
files: scripts/t4_test_mouse_route_regression_r7v4.py; this work file; matching unique session file.
experiment_key: T4-INPUT005-ROUTE-REGRESSION-r7v4
shared_resource: none; no Unity, APK or Actions dispatch.
coordination: T5 owns Mini/Resolution; T4 owns mouse evidence. Existing game adapter untouched. CL read-only.
owner_device: artifact 42058825739 entered world, saved and reopened .rgd; do not regress.
next: execute standalone unittest and compare with real captured=true logs, then check Unity legacy consumption.
