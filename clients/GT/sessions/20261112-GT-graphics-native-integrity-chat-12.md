# GT — Chat-12: actual original 416 external texture identities and complete 50 BC3 top mips, native integration

- session_id: GT-20261112-CHAT-12-SOURCE-LINKS-AND-DEPTH-NATIVE
- origin: chat; agent: GT; write branch only feature/android-native-port
- Owner stopped T1–T5; GT independently operates build/graphics; source only immutable ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; never Git LFS.

## Real ZIP2 CPU acceptance now PROVEN

- [Real isolate 43156857287 PASS](https://github.com/alwansan/raf/actions/runs/43156857287): separate original source FileIdentifier tables for 82 SHA-verified owners: all 416 original external material Texture references match exact same AssetRipper instance exported pointers (GUID/fileID/type), 0 missing/mismatch. Another 20 source bundled Font/engine materials have separate non-loose export treatment; these aren't changed/guessed. Original 82 owner TexEnv source scope 10,216 slots; another 4,151 internal Texture target same-owner identity matches.
- [Real isolate 43155325887 PASS](https://github.com/alwansan/raf/actions/runs/43155325887): original 50/50 source-populated BC3 top-mip slice pixels byte-equivalent to true AssetRipper PNG cells, exact slice-major in 8 arrays. Original ninth array has 2 logical layers but zero source payload. No synthetic pixels inserted. Lower mips and actual Unity Android GPU remain unverified.
- Original full graphics source 134/134 SHA/size files, 7,532,909,297 bytes; Class187 nine array importer grids, 28/28 material refs, original GUIDs unchanged. Postvendor: 1536 material YAML docs, 750 builtin, 770 custom dummy, 16 custom nonDummy after official TMP/PostFX/volumetric restoration; no numerical DXBC/Adreno parity.

## Actual failed native and fixed input

- [43155854860 FAILED](https://github.com/alwansan/raf/actions/runs/43155854860) at original W1 Depth Copy wrapper: it read `$RUNNER_TEMP/input/Raft_Data` after Mesh inlining changed the serialized owner; the original pinned source hash check rejected it. This is a GOOD fail-closed result, not LFS acquisition required.
- [3e8a3bfff2](https://github.com/alwansan/raf/commit/3e8a3bfff2d320fc33706664cd4cf92978e77c27) correct production W1 wrapper to `$RUNNER_TEMP/w1-original/Raft_Data` pristine SHA-pinned ZIP2; GT [393b2f5a](https://github.com/alwansan/raf/commit/393b2f5aaf2ed630f05e14e25ede2286151b14c3) fixed stale structural test expecting mutated input; [43205382836 PASS](https://github.com/alwansan/raf/actions/runs/43205382836).
- GT requested full APK OBB XAPK at commit [c8680938](https://github.com/alwansan/raf/commit/c86809380ab1e5b95ccf65e30074422a7e744c05), native run [43205543533](https://github.com/alwansan/raf/actions/runs/43205543533) in progress (last stage: AssetRipper real export, license preflight passed). Immutable snapshot at c868; do not claim newer code included in this run.

## Additional production graphics fidelity merged *after* native request

- [f3ea4bea](https://github.com/alwansan/raf/commit/f3ea4bea5f2be80c307e91ac5b4761082daacc97) strict same-AssetRipper original external Material→Texture authenticity 416/416 at production import gate before Unity, source owners 82 authenticated, no GUID rewrite; fail-closed, safe numeric receipt. Source guard [43206068246 PASS](https://github.com/alwansan/raf/actions/runs/43206068246).
- [10563bf4](https://github.com/alwansan/raf/commit/10563bf43ebc2efa611c26e5d7fd76ebca1299da) optional `--stream-source` in array payload recovery: authentic serialized owners read from pristine ZIP2, original stream bytes read from different independently SHA-verified .resS source; no duplicate multi-GB streams or source mutation. Tests with poisoned streams and unsafe destinations, [43206376993 PASS](https://github.com/alwansan/raf/actions/runs/43206376993).
- [e687c0c4](https://github.com/alwansan/raf/commit/e687c0c4c251cc49adf5b76ec968413ccab641f5) strict full 50 actual BC3 top-mip slice source pixel parity in production before Unity; no lower mip or Android GPU claim; keeps original 2 zero-source layers, private stage deleted. Native source-only guard [43206535542 PASS](https://github.com/alwansan/raf/actions/runs/43206535542), Editor test [43206535361 PASS](https://github.com/alwansan/raf/actions/runs/43206535361).

## Next action

Review latest native run 43205543533, its first failing gate if any, and real APK OBB XAPK delivery if succeeded. Do not duplicate/cancel active run. If new native needed, request full delivery once via .github/raft-native-build-request.json, include latest f3ea/10563/e687, retain original Shader/Water, FMOD, C# Android, packaging & delivery integrity guards. If GitHub Release HTTP403 occurs, do not report success; previous 42296450023 Release failed 403 and optional RAFT_RELEASE_TOKEN may be needed. Do not invent a secret. Maintain full GT memory, state, summary, restore session evidence after work.

## Same-session follow-up: strict real-source acceptance

**إغلاق ثغرة نجاح Workflow الصوري في فحص الرسوميات:** المصدر الحقيقي [43156857287](https://github.com/alwansan/raf/actions/runs/43156857287) أثبت 416/416، و[43155325887](https://github.com/alwansan/raf/actions/runs/43155325887) أثبت 50/50، لكن خطوات المصدر التشخيصية كانت `continue-on-error` مما قد يخفي فشلها تحت Workflow SUCCESS. أضاف GT بوابة `scripts/gt_original_graphics_critical_gate.py` [7242726f](https://github.com/alwansan/raf/commit/7242726f3d857c61ce88ee4575d652a96430d01c) + اختبار 7 حالات سلبية [4c252b4c](https://github.com/alwansan/raf/commit/4c252b4cfae0fd47232d04e09467128f1f70a191)، ودمج خطوة `GT fail-closed accepted original source graphics parity` في real CI [666ca2d7](https://github.com/alwansan/raf/commit/666ca2d7798c8ad97407aa88b4da50db2779d525). [CI synthetic 43207734504 PASS](https://github.com/alwansan/raf/actions/runs/43207734504)؛ [CI ZIP2 real 43207734641](https://github.com/alwansan/raf/actions/runs/43207734641) جارٍ، فلا تنسب له PASS قبل انتهاء الخطوة الصارمة. Full native [43205543533](https://github.com/alwansan/raf/actions/runs/43205543533) اجتاز staged arrays/Builtin Shader/Scene-owned rebinding start ويجري؛ لا يضم commits الأحدث للـ416 و50. لا APK/OBB/XAPK جديد مثبت، لا original lower-mip أو Adreno GPU proof. 

