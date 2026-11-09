# T5 session 20261109T0548Z-T5-scheduled-png-inflate-k8r2
origin: scheduled
baseline: 0044c27256418394594110566b21d243c94b355e
scope: work/T5/20261109T0548Z-scheduled-png-inflate-integrity.md
source commits: ffc56d415f8b00eb42093305a33552db4fefc550, acb3b0f8a3de77a82fac3de23c5720e50c92827d, 1e22a7326373406272a789ef6a99e0aa66e938f9, f51d5b8ff6346ce00e9ff0a59ba949e14fe90604
finding: Previous validate_png verified chunk CRC but not IDAT decompression. A CRC-correct PNG could have an invalid zlib stream. Now decompresses bounded to 128 MiB and checks EOF/trailing bytes, with four isolated regressions.
validation: source reviewed; tests NOT executed in this environment because container has no GitHub DNS; no claim of CI PASS. Existing T5 source tests should run: python -m unittest discover -s tests -p 'test_t5_png_idat_integrity.py' -v.
limits: decompression integrity is not PNG scanline filter validation or visual pixel parity; phone and APK/OBB are not available here. No Unity or T4 mouse edits.
next: execute four regressions in Actions or local checkout, then inspect real six CL PNGs and proceed with APK/OBB/Resolution/right-buttons scoped repair. Full game NOT_READY.
