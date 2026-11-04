# B49 — 20261104T2054Z-B49-c81f

- Session initial HEAD 649ec8e5b227ecae970b161ceb3339e2be1929c2; live read B_TEAM prompts/README/OPERATING_MODEL/SOURCES/TEMPLATES/REVIEW/SUMMARY/RESTORE, AGENTS, owner requirements, STATUS, ZIP2 provider, WATER-001 issue, shader contract.
- Latest game release APK86/run 41812889049; B50 LOCAL-005 source checks 41909535306 and 41909535307 succeeded. CL review 5394407: water pass failures and kernel count zero remain device-observed on APK86; new code not device-tested.
- Current work WATER-001: existing gate uses shader-wide program presence with raw Pass token count; multiple pass declarations can be accepted with only one program. Plan to require independently executable authored programs per pass, synthetic valid/missing/comment/string controls; preserve strict authentication flag, no dummy and no Unity native request.
- Original ZIP2 provider SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385; no original raw source fetched/published. B50 working LOCAL-005 independently. Audio/Settings preserved; touch deferred.
- Next: implement/test small code fix, update work/event/MEMORY/STATUS, verify CI. Water/GPU/device NOT_READY 0/3.
