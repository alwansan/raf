# T4 scheduled checkpoint — 20261108T2241Z-T4-scheduled-input-edge-a6p2
origin: scheduled
identity: T4
scope_commit: 7f6b2cbc89417ffb8708599b9b8b74ca3f474f7d
head_before_session: 7f6b2cbc89417ffb8708599b9b8b74ca3f474f7d
work: ../work/20261108T2241Z-T4-scheduled-input-edge-a6p2.md

## Evidence and engineering finding
Read owner 5 Nov phone report, AGENTS, T4 MEMORY and prior scheduled session 20261108T2140Z, latest shared lab readiness and 8 Nov owner feedback, plus current t4_analyze_mouse_lab_routes.py. Phone Artifact 42058825739 entered/saved/reopened world; packaging publication failure is independent. Later owner directly verified captured camera motion, but game LEFT/RIGHT/MIDDLE and wheel remain unverified/broken. Source-only adapter CI42518143297 passed original 20 legacy call-site tests, NOT a signed game device test. Shared Mini v0.2.13 CI42519487402 delivered by T5; do not duplicate. The older CL/test data show uncaptured LEFT and vertical wheel only; captured true and Unity consumer comparison missing.

## Narrow new risk audit
The current analyzer counts ACTION_DOWN and ACTION_UP edges only when actionButton carries the button bit. Android may supply actionButton=0 for ordinary DOWN/UP; these would not count as left edges. Conversely buttonState in a MOVE is not an edge and must not be counted as one. This is a **testable hypothesis**, not an established device bug. A safe next isolated experiment should replay actual source-identified per-device DOWN/UP sequences and compare actionButton/buttonState transitions, deduplicating Activity/View callbacks by event identity, and report ambiguity rather than invent clicks. Do not modify game runtime or change camera capture before evidence.

## Boundaries and next action
No Unity build, CI, CL write, game code, keyboard, touch, .rgd, audio, Settings, T5 UI/Resolution or shared lab change. No phone test claimed. Local git DNS unavailable, so no local checkout or executable test. Next: inspect fresh captured=true CL T4-02 event exports with epoch and LEFT/RIGHT/MIDDLE/V/H scroll, validate Android callback edge semantics, then confirm on a signed full-game source candidate that Legacy Mouse0/1/2 and wheel are consumed. INPUT-005 OPEN; LOCAL-005 world/save success remains limited to 42058825739; NOT_READY 0/3.
