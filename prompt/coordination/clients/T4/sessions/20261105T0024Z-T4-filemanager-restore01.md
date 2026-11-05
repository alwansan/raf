# T4 isolated restoration session — 20261105T0024Z-T4-filemanager-restore01

Identity T4; branch feature/android-native-port only. Started after owner's explicit hourly scheduling and immediate execution request.

Previous T4 state at inspection: session 20261104T2357Z-T4-lw01, status active, updated 2026-11-05T00:22:00Z. Treat as **possible identity conflict**. This is a separate session, status `paused_identity_conflict` for shared state/MEMORY ownership. Do not overwrite existing T4 state.json, MEMORY.md, original work, or another T4 session. Independent read-only/source-probe files only.

Baseline branch SHA: 365ffc9be6f952e89bfa6f227cfa6577e8df8d68; CL main 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29; last confirmed Android game: APK86 tag android-early-test-41812889049-1 from d181ee7152580f49ee0b41dfd05fa2bfdacfafe5. No newer installed game evidence. Previous T4: original SaveAndLoad.Load<T> proof CI41939908432 SUCCESS; Android catch log managed CI41939846508 SUCCESS, not phone. B50 original Steam guards exist. LOCAL-005 OPEN, NOT_READY 0/3.

Scope: investigate **original FileManager I/O and caught-read paths** fed by SaveAndLoad.Load<T>/Save, distinct from the completed loader/binder census. Read exact original managed DLL from immutable zip2 SHA15964ea8f246b6e076ce26b60931ee2e1a9a2385 with verified DLL SHA0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e, private ILSpy staging, and report sanitized structural contract only. Do not publish proprietary source/data/strings. Explicit negative controls for missing/ambiguous code, masked literals, unverified source. Run isolated affordable source CI if source tool is ready; do not modify native request, start Unity build, cancel jobs or stage .rgd migration. Adapted source/Unity/phone validation distinct.

Inherited evidence: B07 original callback and coroutine CI41929721761; B14 SaveGame ordering CI41929777877; B19 save backup/path CI41929845587; B37 RGD seed CI41928767833; B50 Steam source patches; T4 original loader CI41939908432 / 41939846508. They remain attributed to original workers.

Plan: 1) inspect FileManager and the authenticated original SaveAndLoad direct call edges; 2) assert and record FileManager read/catch/IO classification with original binary SHA gate and adversarial fixtures; 3) use observed facts to decide if Android-specific repair/instrumentation is justified, not a blind shim; 4) document tested result, CI link, rejected hypotheses and next device roundtrip test.

No native success claim and no state/MEMORY collision. Session resumed_from=20261104T2357Z-T4-lw01 for continuity only, not proof that predecessor ceased.
