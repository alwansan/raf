# T4 INPUT-005 scoped evidence audit
session_id: 20261109T0036Z-T4-scheduled-capture-evidence-q4m8
origin: scheduled
baseline_sha: 278c1395fda36d3ff4ae602a0ec1f68dcc375f76
experiment_key: T4-capture-edge-ambiguity-20261109
shared_resource: none (no CI/Unity/Mini)
files: this independent work file and matching sessions/20261109T0036Z-T4-scheduled-capture-evidence-q4m8.md only
hypothesis: Android ACTION_DOWN/UP with actionButton=0 may carry a state transition, but buttonState alone is not a reliable press/release edge; captured=true is mandatory to assess captured routing.

Owner phone 42058825739 world enter/save/reopen is proven for that artifact, packaging publication failed separately. Later CL captured-button evidence is missing; no Unity gameplay success can be inferred from source-only bridge CI42518143297. Existing t4_analyze_mouse_lab_routes.py intentionally only credits actionButton explicit edges. Do not weaken its proof standard without same-device ordered event traces and duplicate filtering.

Latest HEAD read 278c1395fda36d3ff4ae602a0ec1f68dcc375f76; latest observed Actions 42529039014 completed success on dcf9bc3 (not phone proof). Unified Mini v0.2.13 CI42519487402 already delivered by T5, no repeat. Next test: log captured=true, capture_request=ON, device/source/time/action/buttonState/actionButton and wheel axes; derive per-device transitions only for ordered paired events, mark ambiguous instead of PASS. Keep keyboard, .rgd, audio, Settings and T5 UI/Resolution untouched.
