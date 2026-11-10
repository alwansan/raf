# T3 session 20261110T1931Z-T3-scheduled-guid-regex-proof-q5m8
origin=scheduled
issue=RENDER-002; status=SOURCE_FIX_PENDING_CI; NOT_READY 0/3
owner_report=docs/DEVICE_FEEDBACK_42058825739_AR.md
scope=prompt/coordination/work/RENDER-002/T3-20261110T1931Z-T3-scheduled-guid-regex-proof-q5m8.md
scope_commit=362dd34f46c4e7409c06d24180c3947da4a8a1ce
fix_commit=993f36ada1b38bcf4b9379c50faeb9de197f22a0
before_blob=b13ecc03220090eb2fd5eafacb678afcfffe2375
after_blob=7cf1e19185f624b5fb24cdf1cee590e606562bbc

## Finding
Direct GitHub source read showed raw Python regex patterns with two literal backslashes in GUID, REF_BLOCK, REF_FILE_ID and REF_GUID. Python regex evaluation of a minimal source-free fixture proves r'\\\\{' does not match ordinary '{', and r'guid:\\\\s*' does not match 'guid: ' whereas single-backslash regex patterns do. Prior session had dismissed this hypothesis; current inspection of actual blob b13ecc and isolated Python demonstration supersede that statement. This bug makes static YAML GUID audit undercount, independent of original/export asset parity.

## Work
Registered independent scope before editing. Updated only four regex constants using the expected existing file blob SHA via contents API, preserving the rest of the source. Existing source-free regression suite tests resolved, unresolved, builtin, reversed order, cross-reference separation, duplicate .meta and extension grouping; not rerun in GitHub Actions during this cycle. No source/game asset/Unity APK modifications or original ZIP2 scan. T4 mouse, T5 resolution and T1/T2 water unaffected. World/save/reentry on artifact 42058825739 remains accepted only for that device build; white raft/hand, smoke square and lighting still OPEN.

## Next
1. Run tests/test_t3_guid_audit_regression.py on commit 993f36ad or newer and inspect failures before further changes.
2. Execute read-only audit on authenticated ZIP2/export tree and link smoke particle Renderer -> Material -> Shader GUID and texture references; treat unresolved as partial-tree only.
3. Compare actual Blend/Alpha/ZWrite and keywords to source, then request a shared mini-lab test only for a concrete GPU hypothesis. Preserve NOT_READY 0/3.
