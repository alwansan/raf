#!/usr/bin/env python3
"""Restore Unity 2021 UI packages to an ephemeral AssetRipper project.

Preserves generated source, GUID .meta and scenes, and refuses version changes.
These editor-compatible packages supersede Windows-managed UI/TMP DLLs.
"""
import argparse
import json
from pathlib import Path

PACKAGES = {
    "com.unity.ugui": "1.0.0",
    "com.unity.textmeshpro": "3.0.6",
}

def ensure(project: Path, *, apply: bool) -> dict:
    manifest = project / "Packages" / "manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError("Unity Packages/manifest.json is missing")
    original = manifest.read_text(encoding="utf-8")
    data = json.loads(original)
    if not isinstance(data, dict):
        raise ValueError("Unity manifest must be a JSON object")
    deps = data.get("dependencies")
    if not isinstance(deps, dict):
        raise ValueError("Unity package dependencies must be a JSON object")
    changed = {}
    for name, version in PACKAGES.items():
        current = deps.get(name)
        if current is not None and current != version:
            raise ValueError(f"Refusing to override existing {name}={current}")
        if current is None:
            changed[name] = version
    # Do not stage prebuilt versions of these Unity-owned assemblies as plugins.
    installed = project / "Assets" / "Plugins" / "RaftManagedReferences"
    for dll in ("UnityEngine.UI.dll", "Unity.TextMeshPro.dll"):
        if (installed / dll).exists():
            raise ValueError(f"UI package conflicts with staged Windows DLL: {dll}")
    if apply and changed:
        deps.update(changed)
        manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    result = {"packages": PACKAGES, "added": changed, "applied": apply}
    print("Restored Unity 2021 packages:", result)
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    ensure(args.project, apply=args.apply)
