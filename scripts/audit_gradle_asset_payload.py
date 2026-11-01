"""Privacy-preserving Gradle asset-size evidence after Unity, even on build failure.

Reads generated Gradle files only. No asset bytes, paths, filenames or keys
are printed or uploaded. A missing Gradle project is explicitly unavailable.
"""
import argparse
import json
import os
from pathlib import Path
import stat

JAVA_ARRAY_LIMIT = (1 << 31) - 1
MODULES = ("unityLibrary", "launcher")


def classify(parts):
    if parts[:3] == ("bin", "Data", "StreamingAssets"):
        return "streaming_assets"
    if parts[:2] == ("bin", "Data"):
        return "unity_data"
    return "other_assets"


def audit(project):
    root = Path(project) / "Library/Bee/Android/Prj/IL2CPP/Gradle"
    sizes = []
    categories = {"streaming_assets": 0, "unity_data": 0, "other_assets": 0}
    modules = {}
    skipped = 0
    available = False
    for module in MODULES:
        assets = root / module / "src/main/assets"
        module_bytes = 0
        module_files = 0
        if assets.is_dir() and not assets.is_symlink():
            available = True
            for directory, directories, filenames in os.walk(assets, followlinks=False):
                directories[:] = [d for d in directories
                                  if not (Path(directory) / d).is_symlink()]
                for filename in filenames:
                    path = Path(directory) / filename
                    try:
                        info = path.lstat()
                    except OSError:
                        skipped += 1
                        continue
                    if not stat.S_ISREG(info.st_mode):
                        skipped += 1
                        continue
                    size = info.st_size
                    sizes.append(size)
                    module_files += 1
                    module_bytes += size
                    categories[classify(path.relative_to(assets).parts)] += size
        modules[module] = {"fileCount": module_files, "totalBytes": module_bytes}
    return {
        "available": available,
        "reason": None if available else "gradle_assets_not_generated",
        "fileCount": len(sizes),
        "totalBytes": sum(sizes),
        "largestBytes": max(sizes, default=0),
        "topFiveBytes": sorted(sizes, reverse=True)[:5],
        "atOrAboveJavaArrayLimit": sum(n >= JAVA_ARRAY_LIMIT for n in sizes),
        "totalAtOrAboveJavaArrayLimit": sum(sizes) >= JAVA_ARRAY_LIMIT,
        "categoryBytes": categories,
        "modules": modules,
        "skippedNonRegularOrUnreadable": skipped,
        "fileNamesLogged": False,
        "assetContentRead": False,
        "deviceVerified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_ANDROID_GRADLE_PAYLOAD " + json.dumps(audit(args.project), sort_keys=True))


if __name__ == "__main__":
    main()
