"""Count water-related metadata candidates without exporting managed identifiers."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

ASSEMBLY_BYTES = 3211776
ASSEMBLY_SHA256 = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"
ANCHORS = {"dx11fft", "gpufft", "wavesrendererfft", "waterqualitysettings"}
FAMILIES = {
    "surface_and_waves": ("watersurface", "waterspectrum", "waverender", "wavesrender", "fft", "gerstner"),
    "ripple_and_wake": ("ripple", "wake"),
    "buoyancy_and_queries": ("buoyancy", "buoyant", "waterphysics", "waterheight", "waterlevel", "displacement"),
    "foam_and_particles": ("foam", "splash", "spray", "waterparticle"),
    "shore_and_local_water": ("shore", "waterbody", "watervolume", "watermask", "river", "waterfall"),
    "underwater_and_composite": ("underwater", "subsurface", "waterblur", "waterreflect", "waterrefract"),
}


def summarize(rows):
    anchors = set()
    family_types = Counter()
    family_methods = Counter()
    family_method_owners = Counter()
    total_types = 0
    water_scope_types = 0
    for namespace, typename, methods in rows:
        total_types += 1
        namespace, typename = namespace.lower(), typename.lower()
        if typename in ANCHORS:
            anchors.add(typename)
        # Explicitly limit the lexical census to water-related type/namespace names.
        water_scope = ("water" in namespace or "water" in typename or typename in ANCHORS
                       or any(term in typename for term in ("buoyan", "gerstner", "wavesrender")))
        if not water_scope:
            continue
        water_scope_types += 1
        for family, terms in FAMILIES.items():
            family_types[family] += any(term in typename for term in terms)
            count = sum(any(term in method.lower() for term in terms) for method in methods)
            family_methods[family] += count
            family_method_owners[family] += count > 0
    if anchors != ANCHORS:
        raise ValueError(f"Expected all {len(ANCHORS)} source anchors, found {len(anchors)}")
    return {
        "evidence": "ORIGINAL_SOURCE_METADATA_LEXICAL_CANDIDATES",
        "assembly_sha256": ASSEMBLY_SHA256,
        "types_examined": total_types,
        "water_scope_types": water_scope_types,
        "confirmed_anchor_count": len(anchors),
        "families": {name: {
            "type_name_matches": family_types[name],
            "method_name_matches": family_methods[name],
            "method_owner_types": family_method_owners[name],
        } for name in FAMILIES},
        "scene_instances_verified": False,
        "original_water_runtime_verified": False,
    }


def census(path):
    import dnfile
    data = path.read_bytes()
    if len(data) != ASSEMBLY_BYTES or sha256(data).hexdigest() != ASSEMBLY_SHA256:
        raise ValueError("Original managed assembly size or SHA-256 mismatch")
    assembly = dnfile.dnPE(data=data)
    try:
        if assembly.net is None or assembly.net.mdtables.TypeDef is None:
            raise ValueError("Missing managed TypeDef metadata")
        return summarize(
            (str(row.TypeNamespace), str(row.TypeName),
             [str(method.row.Name) for method in row.MethodList])
            for row in assembly.net.mdtables.TypeDef.rows
        )
    finally:
        assembly.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assembly", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    args.report.write_text(json.dumps(census(args.assembly), indent=2) + "\n", encoding="utf-8")
