# GT V16 — direct corrected exporter Unity reimport (prepared, NOT PASS)

Starting immutable head `2d3adcabfa60198072c9f70da4206c5e0e62b02f` verified. V14 [45972362899](https://github.com/alwansan/raf/actions/runs/45972362899) and V15 [45975084812](https://github.com/alwansan/raf/actions/runs/45975084812) actual jobs success, V15 archive 15186083739 digest checked against Actions metadata. Previous local checkout is not mounted in this session, network Git unavailable; no prior local bytes changed. GitHub connector uses non-force updates against expected head.

V16 stages fresh actual V15 opt-in public exporter PNG and metadata directly (replay of same pinned exporter, not pretending old ZIP contains a complete project). Recheck all six V15 pair fingerprints and historical V12 opt-out separately. Stage the same trace-driven mesh/material/shader adapter path; exact candidate texture GUID/fileID, PNG and metadata are copied byte-for-byte, no alpha edit. Editor uses licensed authored Unity 2021.3.45f2 Vulkan Linear and unfiltered Texture2D.Load, no manual texture metadata writes; independent comparison requires 84 actual texels, six V14 alpha_off mip hashes and exact mip bytes, 70/70 top pixels, four texture/material and four shader adapter slot matches, CPU orientation from readable fixture only. Fresh GUIDs are export-volatile; match the candidate GUID within the actual route and compare prior runs by source key/hash, not invented equal GUIDs.

Eight source regression controls and ten actual-receipt falsifiers planned; actual Unity not run/verified yet. Default off; no original assets, source lower-mip claim, Android/device, production activation, CL/lab, BLACK, animation or APK/XAPK. A3 blocked, G0–G6 open; historical 688/786 non-Dummy and 98 Dummy/37 GUID unchanged. Ali pinned restore: https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md.

Next: activate only authored V16 workflow after review; inspect exact run and retain raw/verified archive. No PASS until actual evidence.

## Activation and live status

Source 4a206be8844aa0e455079208a301dcddf0c0e1bb; activation 97666cc835f929053aa7621a058ce9bdfbfe633f; [45976163790](https://github.com/alwansan/raf/actions/runs/45976163790), job 140428299621, IN PROGRESS. [Guard 45976163752](https://github.com/alwansan/raf/actions/runs/45976163752) SUCCESS. At check, checkout underway; no actual Unity result. Workflow expected 291 regressions and 37+6+10 controls; no new game build. Next inspect exact run and archive, not a new activation.

## Independent archive inspection

`inspect_archive.py` is an independent offline checker, not an executed result. After V16 succeeds, download the exact Actions ZIP, verify its digest from the API, then run from a repo checkout with Python + Pillow:

```bash
python3 clients/GT/sessions/20261127-dxt5nm-exporter-reimport-v16/inspect_archive.py --archive actual-v16.zip --sha256 <Actions-artifact-sha256> --run 45976163790 --head 97666cc835f929053aa7621a058ce9bdfbfe633f --out actual-pass-45976163790.json
```

It checks CRC, every member SHA, immutable run ID, actual candidate PNG/metadata bytes and decoded RGBA, six normalized V15 export pairs, four exact route and shader adapter slots, all six V14 alpha_off observed mip byte strings and hashes, 70 top pixels, 84 actual GPU texels and negative-control/regression counts. Do not run it on a substituted or constructed receipt. It has not yet been exercised on the V16 archive. Last live check: checkout and source-only regression step SUCCESS, public exporter build in progress; no V16 actual Unity verdict.
