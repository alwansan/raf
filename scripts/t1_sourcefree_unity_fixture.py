"""Generate a small public, source-free Unity 2021 EditMode test fixture.

Do not stage original Raft assets, FFT shader source, license files or secrets.
This fixture tests GameCI's supported Editor activation and managed test
execution only; it cannot validate FFT water or Adreno graphics.
"""
import argparse
import json
from pathlib import Path

EDITOR_VERSION = "2021.3.45f2"
TEST_FRAMEWORK = "1.1.33"
ASSET_PATH = "Assets/Tests/Editor"
ASSET_FILE = "T1SourceFreeEditorTest.cs"
ASSEMBLY_FILE = "T1SourceFreeEditorTests.asmdef"

_TEST = """using NUnit.Framework;
using UnityEngine;

public sealed class T1SourceFreeEditorTest
{
    [Test]
    public void ExpectedEditorMajorVersionIs2021()
    {
        Assert.That(Application.unityVersion.StartsWith("2021.3."), Is.True);
        Assert.That(2 * 3 + 4, Is.EqualTo(10));
    }
}
"""

_ASMDEF = {
    "name": "T1SourceFreeEditorTests",
    "rootNamespace": "",
    "references": [],
    "includePlatforms": ["Editor"],
    "excludePlatforms": [],
    "allowUnsafeCode": False,
    "overrideReferences": True,
    "precompiledReferences": ["nunit.framework.dll"],
    "optionalUnityReferences": ["TestAssemblies"],
    "autoReferenced": False,
    "defineConstraints": [],
    "versionDefines": [],
    "noEngineReferences": False,
}


def construct(project: Path):
    project = Path(project)
    if project.is_symlink() or project.exists() or project.parent.is_symlink() or not project.parent.is_dir():
        raise ValueError("Synthetic project must be new beneath an existing regular parent")
    if len(str(project)) > 1024:
        raise ValueError("Invalid synthetic project path")
    test_dir = project / ASSET_PATH
    test_dir.mkdir(parents=True)
    (project / "Packages").mkdir()
    (project / "ProjectSettings").mkdir()
    (test_dir / ASSET_FILE).write_text(_TEST, encoding="utf-8")
    (test_dir / ASSEMBLY_FILE).write_text(
        json.dumps(_ASMDEF, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (project / "ProjectSettings/ProjectVersion.txt").write_text(
        "m_EditorVersion: " + EDITOR_VERSION + "\n", encoding="utf-8")
    (project / "Packages/manifest.json").write_text(
        json.dumps({"dependencies": {"com.unity.test-framework": TEST_FRAMEWORK}}, sort_keys=True) + "\n",
        encoding="utf-8")
    return {"synthetic_unity_test_fixture_created": True, "unity_version": EDITOR_VERSION,
            "fixture_test_methods": 1, "private_game_source_used": False,
            "original_raft_data_acquired": False, "unity_activation_verified": False,
            "original_fft_import_or_device_proven": False}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--project", type=Path, required=True)
    args = cli.parse_args()
    print("RAFT_T1_GAMECI_SOURCEFREE " + json.dumps(construct(args.project), sort_keys=True))


if __name__ == "__main__":
    main()
