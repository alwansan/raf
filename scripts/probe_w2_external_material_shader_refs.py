"""Classify original Material ``m_Shader`` / ``m_TexEnvs`` external PPtr
references using each owner's serialized-file external dependency table
(m_Externals).

CPU-only, read-only. Exactly two SHA256-pinned original LFS owners are read
(reusing ``scripts.verify_targeted_lfs_compute_sources``). The output is an
aggregate-only JSON: counts, resolved-owner dependency names and booleans.
Individual original object names, path IDs and payload bytes are never emitted.

Pointer convention: Unity serialized ``PPtr.m_FileID`` indexes ``m_Externals``
as ``external_id = m_FileID - 1`` (one-based; UnityPy ``PPtr.deref`` implements
the same rule). ``fileID == 0`` denotes the owner file itself; values outside
``[1..len(externals)]`` are recorded as explicit unresolved states.

The zero-based alternative convention is recorded only as a negative-control
aggregate; it must never be used as the engine interpretation.

Optional cross-owner existence validation loads explicit additional owner files
passed with ``--validate-owner``; each is hashed locally and only its boolean
validation outcome is reflected in the aggregate result (the local hash value
is printed for evidence, never any payload bytes).
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

SCHEMA_VERSION = 1
CHUNK = 4 * 1024 * 1024

INTERNAL = "own"


def external_index(file_id: int) -> int | None:
    """Map ``PPtr.m_FileID`` to its one-based ``m_Externals`` index.

    ``None`` denotes the owner file itself (or a missing/invalid fileID).
    """
    if file_id is None:
        raise ValueError("PPtr m_FileID missing")
    if not isinstance(file_id, int):
        raise ValueError("PPtr m_FileID must be an int")
    if file_id < 0 or file_id == 0:
        return None
    return file_id - 1


def classify_pointer(file_id: int, owner_externals_count: int) -> str:
    """Classify the pointer-level resolution state of a ``m_FileID``."""
    index = external_index(file_id)
    if index is None:
        return "own" if file_id == 0 else "unresolved:oob-negative-or-zero-own"
    if index >= owner_externals_count:
        return "unresolved:oob-beyond-table"
    return "external"


def classify_target(path_id: int, owner_sets: dict) -> str:
    """Classify target object existence against known owner object-type sets."""
    if path_id == 0:
        return "target:null-path-id"
    for type_name, ids in sorted(owner_sets.items()):
        if path_id in ids:
            return "target-exists:" + type_name
    return "target-missing" if owner_sets else "target-unvalidated"


def load_object_sets(path: Path) -> dict:
    """Read object type -> path-id sets from an additional local owner file."""
    import UnityPy  # local import keeps synthetic tests dependency-free

    env = UnityPy.load(str(path))
    sets: dict[str, set[int]] = collections.defaultdict(set)
    for obj in env.objects:
        sets[obj.type.name].add(obj.path_id)
    return dict(sets)


def parse_owners(root: Path, names):
    """Load each pinned owner with the exact original loader stack."""
    import UnityPy  # local import keeps synthetic tests dependency-free

    parsed = {}
    for name in names:
        env = UnityPy.load(str(root / name))
        serialized = list(env.files.values())
        if len(serialized) != 1:
            raise ValueError("Expected one serialized file per owner: " + name)
        externals = [file_identifier.path for file_identifier in serialized[0].externals]
        if len(set(externals)) != len(externals):
            raise ValueError("Duplicate external dependency name: " + name)
        parsed[name] = {"externals": externals, "environment": env}
    return parsed


def _material_pointers(environment):
    """Yield (kind, pointer) for every Material m_Shader / m_TexEnvs field."""
    for obj in environment.objects:
        if obj.type.name != "Material":
            continue
        material = obj.read()
        saved = material.m_SavedProperties
        yield "material_shader", material.m_Shader
        for entry in saved.m_TexEnvs:
            texture = entry[1].m_Texture if isinstance(entry, (list, tuple)) else entry.m_Texture
            yield "material_texture_env", texture


def probe(root: Path, *, validate_owners=None, owner_names=("resources.assets", "sharedassets0.assets")):
    """Run the bounded CPU-only probe and return the aggregate-only record."""
    pins = {name: EXPECTED[name] for name in owner_names}
    verify_sources(root, pointers_only=False, expected=pins)
    owners = parse_owners(root, owner_names)

    validation_owners = []
    validation_sets = []
    for raw_path in validate_owners or []:
        path = Path(raw_path)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(CHUNK)
                if not chunk:
                    break
                digest.update(chunk)
        validation_owners.append({"path": path.name, "size": path.stat().st_size, "sha256": digest.hexdigest()})
        validation_sets.append(load_object_sets(path))

    one_based = {"material_shader": collections.Counter(), "material_texture_env": collections.Counter()}
    distinct = collections.defaultdict(set)
    zero_based_owner_mismatch = 0
    zero_based_oob_count = 0
    target_validation = {
        "performed": bool(validation_sets),
        "exists": 0,
        "missing": 0,
    }

    for name in owner_names:
        externals = owners[name]["externals"]
        for kind, pointer in _material_pointers(owners[name]["environment"]):
            file_id = pointer.m_FileID
            level = classify_pointer(file_id, len(externals))
            if level == "external":
                index = external_index(file_id)
                target_name = externals[index]
                key = f"{name}:{level}:{target_name}"
                zero_based_oob_count += 1 if not (0 <= file_id < len(externals)) else 0
                if 0 <= file_id < len(externals) and externals[file_id] != target_name:
                    zero_based_owner_mismatch += 1
                if validation_sets:
                    exists = any(
                        pointer.m_PathID in ids for sets in validation_sets for ids in sets.values()
                    )
                    target_validation["exists" if exists else "missing"] += 1
            else:
                key = f"{name}:{level}"
            one_based[kind][key] += 1
            if level == "external":
                distinct[(name, kind, externals[external_index(file_id)])].add(pointer.m_PathID)

    def _resolve_match(target_name, path_id):
        for sets in validation_sets:
            state = classify_target(path_id, sets)
            if state != "target-missing":
                return state
        return "target-missing"

    aggregate = lambda counter: dict(sorted(counter.items()))
    return {
        "schema_version": SCHEMA_VERSION,
        "owners": [
            {
                "name": name,
                "size": EXPECTED[name][0],
                "sha256": EXPECTED[name][1],
                "external_dependencies_in_order": owners[name]["externals"],
            }
            for name in owner_names
        ],
        "material_shader": aggregate(one_based["material_shader"]),
        "material_texture_env": aggregate(one_based["material_texture_env"]),
        "convention_control": {
            "one_based_external_pointer_total": sum(
                value for key, value in one_based["material_shader"].items() if ":external:" in key
            ),
            "zero_based_owner_name_mismatch_count": zero_based_owner_mismatch,
            "zero_based_out_of_table_count": zero_based_oob_count,
            "note": "one-based is the engine convention (m_FileID - 1); zero-based kept only as negative control",
        },
        "distinct_external_targets": {
            f"{owner}|{kind}|{target}": len(ids) for (owner, kind, target), ids in sorted(distinct.items())
        },
        "target_validation": target_validation,
        "validation_owners": validation_owners,
        "no_unity_or_gpu_execution": True,
        "original_payloads_modified": False,
        "aggregate_only": True,
    }


AGGREGATE_TOP_KEYS = {
    "schema_version",
    "owners",
    "material_shader",
    "material_texture_env",
    "convention_control",
    "distinct_external_targets",
    "target_validation",
    "validation_owners",
    "no_unity_or_gpu_execution",
    "original_payloads_modified",
    "aggregate_only",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="Original owner data root")
    parser.add_argument("--out", required=True, help="Aggregate JSON output path")
    parser.add_argument("--validate-owner", action="append", default=[], help="Optional extra owner for existence checks")
    args = parser.parse_args(argv)
    record = probe(Path(args.source), validate_owners=args.validate_owner)
    unexpected = set(record) - AGGREGATE_TOP_KEYS
    if unexpected:
        raise AssertionError("Non-aggregate output key: " + ",".join(sorted(unexpected)))
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"aggregate_written": str(output), "no_proprietary_payload": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
