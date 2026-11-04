# B09 — Engineering memory

Session: `20261104T213740719Z-B09-28fc` (new identity, no prior B09 state found).
Started: 2026-11-04T21:38:14.359Z; branch `feature/android-native-port`; initial HEAD `1aebdfba4502fe0a86fc4986867ec32e207a8cd6`.

## Scope and starting evidence
Read live B_TEAM PROMPT_AR/README/OPERATING_MODEL/SOURCES_AND_ACTIONS/TEMPLATES/REVIEW/SUMMARY, AGENTS, owner requirements, ZIP2 provider, W4 water frontier and current status. Owner's installed game is APK86 released via Actions 41812889049; independent source fix commits after APK86 are not device proof. Device log: water Spectrum 1/6 passes; Foam 1/2; Blur 1/2; compute kernel count 0; sound and Settings owner-confirmed working. Touch deferred. B24 is working Foam and B45 Blur; B49 already fixed independent pass coverage gate; B48/ B01 are handling FFT selectors, so B09 takes unique Spectrum pass restoration/staging lane.

Source provider pin: `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385` (zip2; authenticity must be rechecked per file). Private archive asset sizes do not match manifest; no assumption of payload equivalence. CL review evidence at commit `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29` documented by team REVIEW_2026-11-04, not independently downloaded by B09 yet.

## Hypothesis, approach and constraints
Native export still emits a one-pass `UltimateWater/Spectrum/Water Spectrum` shell. Need authentic six-pass original program/order/target identity, not fake Pass duplication or merely synthetic coverage. First inspect pipeline and existing restoration; then implement isolated source-pinned staging/validation and tests if a demonstrated gap exists. Do not change gameplay, resources, sound, Settings, touch, native request, releases or concurrent workflows. Test and record limitations precisely.

Work: `B09-20261104T213740719Z-B09-28fc-spectrum-pass-staging` (planned-to-active). At registration no B09 code modifications, run or source artifact exists yet; no Unity/device proof. Next: inspect native pipeline and original Spectrum source route, implement valid minimum scope or record precise blocker and pivot.

## Checkpoint — 2026-11-04T21:48:42.836Z
- Source code commit `7ee586f3749913e6c02fa2e2763656f860fe2e97`; tests `5511675ccda4c39ac68c4a8c48f257e65bdcef56`; isolated source workflow `5256ac018f7f2da932a34938e99fbb27cca2f1f0`. [Detailed safe handoff](../../../../docs/B09_SPECTRUM_PASS_STAGING_2026-11-04.md).
- Locally executed `python -m unittest discover -s tests -p test_b09_stage_original_spectrum.py -v` in scratch: **10/10 PASS**. No run of original large ZIP2 payload on local container (no external network); workflow push committed, but GitHub connector only exposed PR-filtered run lookup and returned no run ID; current run conclusion UNKNOWN. Do not treat absent lookup as a failed or missing run.
- Real CL HEAD independently checked: `alwansan/CL@5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`, latest session-summary confirms 39290 last-sample invalid passes and 5406 FFT kernel errors; the final aggregate in REVIEW documents 40327/5555. These are snapshots vs end totals, **not** independent sums. Existing APK86 remains older than source changes.
- Materially useful code outcome: stage real indexed DXBC privately under validated original SHA, retain exact original variant matching, reject synthetic missing cases, prevent raw shader bytes in artifact; original success not yet observed, hence no new resource/phone success. Original ShaderLab still absent, WATER-001 OPEN. No changes to audio, Settings, touch, native requests, scheduled tasks or protected branches.
- On resumed session B09: fetch `prompt/coordination/clients/B09/state.json` and this memory, inspect source commits/branch HEAD, inspect first B09 Action by workflow name and retrieve aggregate. If blocked, classify input/schema gap and add targeted negative test; if successful, build authentic Spectrum ShaderLab with pass states/sampler bindings and independent GPU comparison; check concurrent B24 Foam/B45 Blur first.
