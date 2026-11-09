# T4 scheduled checkpoint

session_id=20261109T2335Z-T4-scheduled-mouse-game-boundary-v3k8
origin=scheduled
identity=T4
branch=feature/android-native-port

Restored owner report docs/DEVICE_FEEDBACK_42058825739_AR.md and T_TEAM instructions, AGENTS, owner requirements, STATUS, state and MEMORY. Most recent scheduled checkpoint was 20261109T2238Z-T4-scheduled-device-provenance-r6v2; chat checkpoints are separate and must not be overwritten. HEAD on initial read a7a58cd330f19a24e242014457ffac195cc77c20.

## Verified
Owner-confirmed local world create/enter/save/exit/reenter only on Artifact 42058825739. CI 42704145152 succeeded on 3a8faa8777f83ffcadb1d769db8c1c93e5aedee0. T5 original Android offline integration run 42715257606 failed on f03af6c3c4f2e0aad2cee5862787932d6e1c52da. No signed-game physical mouse button/wheel acceptance log available in inspected evidence. No actual device gameplay claim or new build. Source mouse correlator requires same logger scope and epoch and refuses gameplay PASS.

## Work
Independent scope published at prompt/coordination/work/INPUT-005/T4-20261109T2335Z-T4-scheduled-mouse-game-boundary-v3k8.md commit d05b69e2833997972dd5d893d00fba0cb007ae9e. This checkpoint is independent of T5 Resolution/layout and T4 chat. No modifications to game, keyboard, touch, .rgd, audio, Settings, or shared CI. CL linked owner report inspected for references, but individual fresh binary screenshots and entire CL log tree were not independently audited this cycle.

## Next
After T5 integration is unblocked, inspect one authentic signed game capture with physical LEFT/RIGHT/MIDDLE + wheel and keyboard/focus alongside Unity Legacy getter counters; correlate same epoch and actual game response. Confirm original world .rgd save/reopen regression. If no real captured log, keep INPUT-005 OPEN and do not infer from mini logs. No duplicate CI. NOT_READY.
