"""Prevent repeat of real Unity Editor CS0234 after costly authentic export.

Tests only the actual native workflow's early preflight wiring. T4's separate
original-ABI CI compiles the real physical-mouse C# against original Unity2021
assemblies; no native Unity editor or proprietary payload is used here.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / ".github/workflows/raft-unity-editor-android-import.yml"
SOURCE_CI = ROOT / ".github/workflows/raft-t5-native-runtime-byte-parity.yml"
EDITOR = ROOT / "android-port/Tests/PhysicalMouse/UnityEditorBridgeCompile.csproj"
ANDROID = ROOT / "android-port/Tests/PhysicalMouse/UnityBridgeCompile.csproj"
CAPTURE = ROOT / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"
LABEL = "      - name: T5 compile real Unity2021 Editor and Android mouse ABI before original ZIP2 acquisition"


def native_stage(workflow: str) -> str:
    if workflow.count(LABEL) != 1:
        raise ValueError("exact early native mouse ABI step is required")
    begin = workflow.index(LABEL)
    try:
        end = workflow.index("\n      - ", begin + len(LABEL))
    except ValueError as exc:
        raise ValueError("early native ABI step has no successor") from exc
    after = workflow.index("      - name: Reuse authenticated ZIP2 shader-owner cache before acquisition")
    before = workflow.index("      - name: Validate original CLR providers before any LFS transfer")
    unity = workflow.index("      - name: Unity Editor 2021.3.45f2 Android import and compile")
    if not before < begin < end < after < unity:
        raise ValueError("early ABI must run after original CLR authentication and before ZIP2 and Unity Editor")
    step = workflow[begin:end]
    for required in (
        'managed="$RUNNER_TEMP/input/Raft_Data/Managed"',
        'for mode in UnityEditorBridgeCompile UnityBridgeCompile; do',
        'timeout 150s dotnet build "android-port/Tests/PhysicalMouse/$mode.csproj"',
        '-p:OriginalManagedDir="$managed"',
        'test "$(stat -c', '3211776',
        'sha256sum -c --status', 'exit 1',
        'T5_NATIVE_EARLY_MOUSE_ABI', 'originalUnity2021ABI=true',
    ):
        if required not in step:
            raise ValueError("early ABI lacks original staged assembly, both modes or fail-closed behavior")
    if "continue-on-error:" in step or "|| true" in step:
        raise ValueError("early ABI cannot silently ignore CSharp compile errors")
    setup = workflow.rfind("      - uses: actions/setup-dotnet@v4", before, begin)
    if setup < before or "dotnet-version: 8.0.x" not in workflow[setup:begin]:
        raise ValueError("early native compile requires pinned dotnet setup")
    return step


class EarlyEditorNativeAbi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = NATIVE.read_text()

    def test_current_production_native_stage_prevents_expensive_rebuild(self):
        self.assertIn("originalUnity2021ABI=true", native_stage(self.native))

    def test_early_stage_cannot_be_delayed_after_zip2_download(self):
        stage = self.native[self.native.index(LABEL):self.native.index(
            "      - name: Reuse authenticated ZIP2 shader-owner cache before acquisition")]
        changed = self.native.replace(stage, "", 1)
        with self.assertRaises(ValueError):
            native_stage(changed)

    def test_losing_real_editor_or_android_compile_is_rejected(self):
        for command in ("UnityEditorBridgeCompile UnityBridgeCompile",
                        'test "$(stat -c', 'sha256sum -c --status', 'exit 1'):
            with self.subTest(command=command):
                changed = self.native.replace(command, "REMOVED", 1)
                with self.assertRaises(ValueError):
                    native_stage(changed)

    def test_error_suppression_and_fake_abi_proof_are_rejected(self):
        for change in ("      - name: fake step\n        continue-on-error: true",
                       ' || true'):
            mutated = self.native.replace(
                "      - name: Reuse authenticated ZIP2 shader-owner cache before acquisition",
                change + "\n      - name: Reuse authenticated ZIP2 shader-owner cache before acquisition", 1,
            ) if "fake" in change else self.native.replace(
                'timeout 150s dotnet build', 'timeout 150s dotnet build' + change, 1)
            if "fake" in change:
                self.assertEqual(native_stage(mutated), native_stage(self.native))
            else:
                with self.assertRaises(ValueError):
                    native_stage(mutated)

    def test_editor_and_android_compile_use_different_real_unity_define_branches(self):
        editor = EDITOR.read_text()
        android = ANDROID.read_text()
        capture = CAPTURE.read_text()
        self.assertIn("<DefineConstants>UNITY_ANDROID;UNITY_EDITOR;UNITY_5_3_OR_NEWER</DefineConstants>", editor)
        self.assertIn("<DefineConstants>UNITY_ANDROID;UNITY_5_3_OR_NEWER</DefineConstants>", android)
        self.assertIn("UnityEditorBridgeUsage.cs", editor)
        self.assertIn("AndroidPhysicalMouseCapture.cs", editor)
        self.assertIn("#if UNITY_ANDROID && !UNITY_EDITOR", capture)
        self.assertIn("#elif UNITY_5_3_OR_NEWER", capture)
        self.assertIn("public static float GetAxisRaw", capture)
        self.assertIn("return Input.GetAxisRaw(axis);", capture)

    def test_new_light_ci_trigger_tracks_csharp_abi_and_native_workflow(self):
        ci = SOURCE_CI.read_text()
        self.assertIn("- tests/test_t5_native_early_editor_abi.py", ci)
        self.assertIn("- android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs", ci)
        self.assertIn("- android-port/Tests/PhysicalMouse/UnityEditorBridgeCompile.csproj", ci)
        self.assertIn("- android-port/Tests/PhysicalMouse/UnityBridgeCompile.csproj", ci)
        self.assertIn("- .github/workflows/raft-unity-editor-android-import.yml", ci)
        self.assertIn("python3 -W error -m unittest -v tests.test_t5_native_early_editor_abi", ci)


if __name__ == "__main__":
    unittest.main()
