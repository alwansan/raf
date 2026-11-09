"""Fail-closed source-only parity audit of native Unity vs original-managed Android runtime files.

No Unity Editor, proprietary binaries, LFS, SDK or GitHub token required.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[1]
MANAGED_HELPER = ROOT / "scripts/verify_android_offline_candidate.py"
NATIVE_WORKFLOW = ROOT / ".github/workflows/raft-unity-editor-android-import.yml"
RUNTIME_DIR = ROOT / "android-port/Runtime/Platform"
SYMBOL = "RUNTIME_COMPILE_SUPPORT_FILES"
SAFE_SOURCE = re.compile(r"[A-Za-z][A-Za-z0-9_]*\.cs\Z")
# Exact native project destination is an integrity boundary: otherwise a
# matching list could be silently copied into the wrong Unity directory.
COPY_LINE = (
    'cp "android-port/Runtime/Platform/$name" '
    '"$RUNNER_TEMP/project/ExportedProject/Assets/RaftAndroid/Platform/"'
)


def _safe_names(value, label: str) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)) or not value:
        raise ValueError(label + " requires a nonempty literal file list")
    if not all(isinstance(name, str) and SAFE_SOURCE.fullmatch(name) for name in value):
        raise ValueError(label + " contains an invalid or unsafe source filename")
    if len(value) != len(set(value)):
        raise ValueError(label + " contains duplicate source filenames")
    return tuple(value)


def managed_sources(source: str) -> tuple[str, ...]:
    tree = ast.parse(source)
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == SYMBOL
    ]
    if len(assignments) != 1:
        raise ValueError("Expected exactly one original-managed runtime source manifest")
    try:
        value = ast.literal_eval(assignments[0].value)
    except (ValueError, TypeError, SyntaxError, MemoryError) as error:
        raise ValueError("Original-managed runtime source manifest must be static") from error
    return _safe_names(value, "original-managed")


def native_sources(workflow: str) -> tuple[str, ...]:
    # Assert the exact block and sole copy point, not an arbitrary comment
    # containing matching filenames or a shell loop with a different target.
    pattern = re.compile(
        r"(?m)^([ \t]*)for name in ([^;\n]+); do[ \t]*\n"
        r"\1  " + re.escape(COPY_LINE) + r"[ \t]*\n"
        r"\1done[ \t]*$"
    )
    matches = list(pattern.finditer(workflow))
    if len(matches) != 1:
        raise ValueError("Expected one exact native Android Unity runtime source copy loop")
    # No other copy or loop is allowed to silently stage an alternate runtime
    # source, and the literal entries cannot contain shell control characters.
    try:
        tokens = shlex.split(matches[0].group(2), posix=True)
    except ValueError as error:
        raise ValueError("Malformed native Android runtime source filenames") from error
    return _safe_names(tokens, "native-Unity")


def verify(managed: str, native: str, runtime_dir: Path) -> tuple[str, ...]:
    managed_names = managed_sources(managed)
    native_names = native_sources(native)
    if set(managed_names) != set(native_names):
        raise ValueError(
            "Original-managed/native Unity runtime staging drift: "
            + "managed_only=" + str(len(set(managed_names) - set(native_names)))
            + " native_only=" + str(len(set(native_names) - set(managed_names)))
        )
    for name in native_names:
        path = runtime_dir / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing regular native Android runtime source: " + name)
    return tuple(sorted(managed_names))


def verify_staged_runtime_bytes(
    runtime_dir: Path, project_root: Path, expected_names: tuple[str, ...]
) -> tuple[str, ...]:
    """Check the FINAL Unity candidate's C# sources, not merely its copy list.

    The 17 runtime .cs inputs, including the offline profile identity writer,
    must have identical bytes to current repository source immediately before
    starting the native Unity Editor. Does not inspect original Raft resources.
    """
    names = _safe_names(expected_names, "expected-staged")
    if "LocalProfileStore.cs" not in names:
        raise ValueError("Missing required offline profile identity source")
    runtime_dir = Path(runtime_dir)
    project_root = Path(project_root)
    platform = project_root / "Assets" / "RaftAndroid" / "Platform"
    for candidate in (
        runtime_dir, project_root, project_root / "Assets",
        project_root / "Assets" / "RaftAndroid", platform,
    ):
        if candidate.is_symlink() or not candidate.is_dir():
            raise ValueError("Missing or linked native runtime staging root")
    listed = list(platform.iterdir())
    if any(path.is_symlink() for path in listed):
        raise ValueError("Linked runtime candidate source")
    staged_cs = {path.name for path in listed if path.suffix.lower() == ".cs"}
    if staged_cs != set(names):
        missing = sorted(set(names) - staged_cs)
        unexpected = sorted(staged_cs - set(names))
        # Only filenames from the Android-owned Platform folder are exposed;
        # never print original Raft bytes or Unity asset content.
        raise ValueError(
            "Missing or unexpected staged Android runtime source: "
            + "missing=" + repr(missing) + " unexpected=" + repr(unexpected)
        )
    for name in names:
        original, staged = runtime_dir / name, platform / name
        if (original.is_symlink() or staged.is_symlink()
            or not original.is_file() or not staged.is_file()):
            raise ValueError("Non-regular native runtime source")
        if original.stat().st_size > 2 * 1024 * 1024 or staged.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Oversized staged Android runtime source")
        if staged.read_bytes() != original.read_bytes():
            raise ValueError("Staged Android runtime bytes changed: " + name)
    return tuple(sorted(names))


def main() -> None:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--managed-helper", type=Path, default=MANAGED_HELPER)
    arg.add_argument("--native-workflow", type=Path, default=NATIVE_WORKFLOW)
    arg.add_argument("--runtime", type=Path, default=RUNTIME_DIR)
    arg.add_argument("--project", type=Path, help="Final staged unity-candidate project, for byte-level attestation")
    args = arg.parse_args()
    matches = verify(
        args.managed_helper.read_text(encoding="utf-8"),
        args.native_workflow.read_text(encoding="utf-8"),
        args.runtime,
    )
    if args.project is not None:
        verify_staged_runtime_bytes(args.runtime, args.project, matches)
    # Public-source names only. Never dump original Raft data or game code.
    print(
        "T5_RUNTIME_STAGING_PARITY status=PASS "
        + "native_count=" + str(len(matches))
        + " original_managed_count=" + str(len(matches))
        + " source_names_identical=true runtime_sources_regular=true "
        + "final_unity_candidate_bytes_equal=" + str(args.project is not None).lower()
        + " unity_editor_build=false device_verified=false"
    )


if __name__ == "__main__":
    main()
