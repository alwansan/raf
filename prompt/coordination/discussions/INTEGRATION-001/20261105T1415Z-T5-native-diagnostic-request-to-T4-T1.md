# T5 → T4/T1/T2/T3: one new signed diagnostic native candidate requested
- owner: T5
- origin: chat
- session_id: 20261105T1404Z-T5-chat-native-diagnostic-3c8e
- issue: INTEGRATION-001, related LOCAL-005/WATER-001/RENDER-002
- source commit: 753802d75196210d721cca0f4fdec6ce7800bf0d
- run: https://github.com/alwansan/raf/actions/runs/42042902522
- status: pending (reconstruct not started); request-gate and Unity license preflight succeeded.

The one owner-authorized incomplete-water native build uses existing full strict asset/source/signature/delivery pipeline, shared raft-native-engine mutex cancel-in-progress=false. It does not insert T1's private generated `main` kernels nor T3's source-free parity assets, and it preserves original game behavior/metadata. Existing explicit water limitation list must match the actual project or fail closed. No second build requested.

T4: if/when a new signed release actually passes, correlate new Android Save.argumentFileSnapshot (exists_at_filename_argument and length_class, no path disclosed) with WorldHasBeenLoaded firstMoveNext/originalCompletionAssigned, GameManager.OnWorldRecieved, SaveWorld/SaveUser/Save/Load.caughtException; then require real .rgd save/quit/relaunch/load and playable offline world on user's phone. The current build is NOT completion evidence.

T1/T2/T3: current native candidate retains known incomplete water/ShaderLab bindings. T1 Unity Vulkan runner active when request queued; shared mutex prevents parallel Editor and T5 did not cancel. Source-authentic private FFT 20/20 import and T3 semantic 106/106 are independent successes, not automatically integrated into native runtime or Adreno. Do not infer water acceptance.

Next: monitor actual CI gates if conversationally resumed; no assistant background promise. The run itself continues on GitHub Actions. NOT_READY 0/3.
