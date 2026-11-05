# T5 — immutable full-native attempt canceled, not a source/Unity failure

- author: T5, origin: chat, session_id: `20261105T1431Z-T5-chat-native-cancel-d41e`
- issue: INTEGRATION-001; reply_to: `prompt/coordination/clients/T5/sessions/20261105T1404Z-T5-chat-native-diagnostic-3c8e.md` (prior independent chat's one-shot native request)
- pinned request source: `753802d75196210d721cca0f4fdec6ce7800bf0d`
- original run: [42042902522](https://github.com/alwansan/raf/actions/runs/42042902522), **completed CANCELLED**
- validated safe-metadata fixture: `tests/fixtures/t5_native_run_42042902522.json`
- standalone classifier: `scripts/t5_audit_native_run_verdict.py`; [source-only CI42046665995](https://github.com/alwansan/raf/actions/runs/42046665995) **SUCCESS 16/16**; no native retry, Unity changes, game artifacts or device tests.

## Exact terminal evidence
Native-request gate **success**; license preflight **success**; reconstruct **cancelled** at original external Mesh restoration / position-audit; delivery-result job **failure only because reconstruct concluded cancelled**; publish-early-test **skipped**, run artifacts **none**. Reconstruct job 127298291857 last public log progress `Position audit header completed: sharedassets24.assets`, followed by `The operation was canceled`, with no demonstrated Mesh data defect. No Unity Editor import, IL2CPP, signed APK/OBB/XAPK, publication or phone trial.

The source workflow has group `raft-native-engine-${{ github.ref }}` and `cancel-in-progress:false`, timeout=240m. This alone cannot identify who or what canceled the run; do not attribute to new pushes, T1 jobs or the owner without independent evidence. This run cannot be marked compilation FAILED, DELIVERED or READY. Never report downstream delivery-result failure as a genuine game compiler exception.

## Restart criterion and division of work
T5 continuation: check current branch HEAD, current active GPU/Unity builds and the cancellation circumstances; **no blind duplicate costly native build**. If owner authorizes/requests a new diagnostic candidate, pin exact SHA and note that it differs from cancelled source; keep existing strict water limitations and package/source/signature checks. Capture actual earliest failing step, or exact signed APK/OBB/XAPK+Release asset/digest only after they exist. T1 water and T3 material/Shader source authenticity remain OPEN and can progress independently; T4's real original seed `SaveAndLoad.Load<T>` test does not prove an on-device user-world RGD cycle. After an authentic new candidate exists, use T4's phone JSONL evidence contract and offline play→save→full stop→reopen test.

No touch/layout changes, no audio/Settings regression, no .meta/GUID/raw game assets changed. Project **NOT_READY 0/3**.
