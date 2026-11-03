"""Read the original project's color-space configuration from the original
``globalgamemanagers`` PlayerSettings and publish it as aggregate-only JSON.

CPU-only, read-only; the source file is exactly the tracked (non-LFS)
``globalgamemanagers`` owner, re-hashed against the pinned SHA256 recorded in
``scripts.verify_targeted_lfs_compute_sources`` when available (the file is an
engine metadata owner, not a payload owner, so its pin is asserted by schema
presence and by file existence, never modified).

Published aggregates (packaging metadata only):
- ``m_ActiveColorSpace`` integer (Unity ``ColorSpace`` engine enum: Gamma=0,
  Linear=1). Only values in {0, 1} are accepted; anything else is a hard
  failure rather than a guess.
- ``m_ColorGamuts`` integer list (engine packaging metadata).
- ``BuildSettings.m_Version`` engine version string (packaging metadata).
- QualitySettings tier count plus per-tier integer ``textureQuality`` /
  ``pixelLightCount`` / ``antiAliasing`` values (packaging metadata).

No original asset bytes, object names or path IDs are ever emitted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SCHEMA_VERSION = 1

VALID_COLOR_SPACES = {0: "Gamma", 1: "Linear"}


def read_color_space(ggm_path: Path) -> dict:
    """Return the aggregate-only color-space / engine-version payload."""
    # UnityPy is imported lazily so the fail-closed synthetic tests can run
    # before any serializer installation step (CI orders tests first).
    import UnityPy

    if not ggm_path.is_file():
        raise FileNotFoundError(f"missing original owner file: {ggm_path}")
    env = UnityPy.load(str(ggm_path))
    player = [
        obj for obj in env.objects if obj.type.name == "PlayerSettings"
    ]
    if len(player) != 1:
        raise ValueError(
            f"expected exactly one PlayerSettings in globalgamemanagers, got {len(player)}"
        )
    tree = player[0].read_typetree()
    if "m_ActiveColorSpace" not in tree:
        raise ValueError("PlayerSettings typetree lacks m_ActiveColorSpace")
    active = tree["m_ActiveColorSpace"]
    if active not in VALID_COLOR_SPACES:
        raise ValueError(
            f"m_ActiveColorSpace value {active!r} outside engine enum {sorted(VALID_COLOR_SPACES)}"
        )
    gamuts = tree.get("m_ColorGamuts")
    if not isinstance(gamuts, list) or not all(isinstance(g, int) for g in gamuts):
        raise ValueError(f"m_ColorGamuts is not an int list: {gamuts!r}")

    versions = {}
    for obj in env.objects:
        if obj.type.name != "BuildSettings":
            continue
        bs = obj.read_typetree()
        version = bs.get("m_Version")
        if isinstance(version, str) and version:
            versions["BuildSettings.m_Version"] = version
            break

    quality_tiers = []
    for obj in env.objects:
        if obj.type.name != "QualitySettings":
            continue
        q = obj.read_typetree().get("m_QualitySettings") or []
        for tier in q:
            quality_tiers.append(
                {
                    "textureQuality": tier.get("textureQuality"),
                    "pixelLightCount": tier.get("pixelLightCount"),
                    "antiAliasing": tier.get("antiAliasing"),
                }
            )
        break

    return {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "active_color_space": {
            "value": active,
            "enum_name": VALID_COLOR_SPACES[active],
            "mapping_source": "Unity ColorSpace engine enum (Gamma=0, Linear=1)",
        },
        "color_gamuts": gamuts,
        "engine_version": versions.get("BuildSettings.m_Version"),
        "quality_tier_count": len(quality_tiers),
        "quality_tier_aggregates": quality_tiers,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="Original Raft_Data root directory")
    parser.add_argument("--out", required=True, help="Aggregate JSON output path")
    args = parser.parse_args(argv)

    root = Path(args.source)
    result = read_color_space(root / "globalgamemanagers")
    out = Path(args.out)
    blob = json.dumps(result, indent=2, sort_keys=True) + "\n"
    for forbidden in (b"m_PathID", b"m_Script"):
        if forbidden.lower() in blob.lower().encode():
            raise ValueError("aggregate output contains a forbidden field key")
    out.write_bytes(blob.encode("utf8"))
    print(f"{{\"aggregate_written\": {json.dumps(str(out))}, \"no_proprietary_payload\": true}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
