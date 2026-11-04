# B09 — Engineering memory

Session: `20261104T213740719Z-B09-28fc` (new identity, no prior B09 state found).
Started: 2026-11-04T21:38:14.359Z; branch `feature/android-native-port`; initial HEAD `1aebdfba4502fe0a86fc4986867ec32e207a8cd6`.

## Scope and starting evidence
Read live B_TEAM PROMPT_AR/README/OPERATING_MODEL/SOURCES_AND_ACTIONS/TEMPLATES/REVIEW/SUMMARY, AGENTS, owner requirements, ZIP2 provider, W4 water frontier and current status. Owner's installed game is APK86 released via Actions 41812889049; independent source fix commits after APK86 are not device proof. Device log: water Spectrum 1/6 passes; Foam 1/2; Blur 1/2; compute kernel count 0; sound and Settings owner-confirmed working. Touch deferred. B24 is working Foam and B45 Blur; B49 already fixed independent pass coverage gate; B48/ B01 are handling FFT selectors, so B09 takes unique Spectrum pass restoration/staging lane.

Source provider pin: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (zip2; authenticity must be rechecked per file). Private archive asset sizes do not match manifest; no assumption of payload equivalence. CL review evidence at commit `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29` documented by team REVIEW_2026-11-04, not independently downloaded by B09 yet.

## Hypothesis, approach and constraints
Native export still emits a one-pass `UltimateWater/Spectrum/Water Spectrum` shell. Need authentic six-pass original program/order/target identity, not fake Pass duplication or merely synthetic coverage. First inspect pipeline and existing restoration; then implement isolated source-pinned staging/validation and tests if a demonstrated gap exists. Do not change gameplay, resources, sound, Settings, touch, native request, releases or concurrent workflows. Test and record limitations precisely.

Work: `B09-20261104T213740719Z-B09-28fc-spectrum-pass-staging` (planned-to-active). At registration no B09 code modifications, run or source artifact exists yet; no Unity/device proof. Next: inspect native pipeline and original Spectrum source route, implement valid minimum scope or record precise blocker and pivot.
