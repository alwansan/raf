# T3 scheduled — smoke34 used-lane structural gate correction

session_id: 20261109T2226Z-T3-scheduled-used-lane-superset-q8m3
origin: scheduled
branch: feature/android-native-port
resumed_from: 20261109T2134Z-T3-scheduled-smoke-semantic-no-proof-x6k2; 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2
base_head: ec86477dd24a2299be77a9a9fbb9ffefbd06c3f0
work: prompt/coordination/work/RENDER-002/20261109T2226Z-T3-scheduled-used-lane-superset-q8m3.md
work_commit: 7eedda1f5640a7cf678ce92731fca54629ab97ce
source_commits: 0f3abc478cc0497cdcecd72a94cd0ad6fb139f10, dca85c845448eb916e9ee4cd174c9a8d928e6de8

Read owner 5 Nov device feedback, AGENTS, current owner requirements, status, T_TEAM protocols, T3 state/memory and latest chat/scheduled evidence. Recent Actions 42704199229, 42704198957 completed success; no T3 equivalent running. Original phone artifact 42058825739 world/save success is limited; CL white/lighting/square smoke still open. Newer owner 8 Nov unified mini-lab policy preserved.

## Actual correction
CI42696526193 established original DXBC 22 used input lanes vs 28 declared SPIR-V lanes. Existing source-free gate incorrectly required 1:1 equality with all *declared* lanes, rejecting any valid mapping of used lanes. Corrected to full injection of original used lanes into declared SPIR-V lanes and explicit count of unused reflected lanes. It still returns STRUCTURAL_INJECTION_ONLY, not proof of compiler provenance. Two tests added; CI not executed for this commit. No source assets or original binaries changed.

## Next
Run tests/test_t3_smoke34_location_provenance_gate.py in isolated source CI or local Python. Obtain authenticated compiler instruction mapping; do not infer it from register/location equality. Correlate pass alpha with original square-smoke CL screenshot only after authentic mapping. RENDER-002 OPEN / NOT_READY 0/3. No Unity/APK/OBB, audio, Settings, .meta, GUID, .rgd changes.
