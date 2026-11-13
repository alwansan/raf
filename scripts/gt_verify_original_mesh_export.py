#!/usr/bin/env python3
"""Compare original ZIP2 Mesh buffers with same-instance AssetRipper Unity YAML."""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
import json
from pathlib import Path
import re
import struct

from scripts.gt_stage_serialized_owners import OWNERS
from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_zip2_payloads import manifest
from scripts.verify_exported_material_texture_links import HEADER, GUID

HEX32 = re.compile(r"[0-9a-f]{32}\Z")
CHANNEL_FIELDS = ("stream", "offset", "format", "dimension")
SUBMESH_FIELDS = ("firstByte", "indexCount", "topology", "baseVertex", "firstVertex", "vertexCount")


def source_geometry(tree, source, records, verified_streams):
    vertex = tree["m_VertexData"]
    payload = bytes(vertex["m_DataSize"])
    stream = tree["m_StreamData"]
    offset, size = stream["offset"], stream["size"]
    if size:
        name = stream["path"]
        if not name or Path(name).name != name or not name.endswith(".resS"):
            raise ValueError("invalid_original_mesh_stream_name")
        _, stream_size, sha = records["Raft_Data/" + name]
        if offset < 0 or size < 0 or offset + size > stream_size:
            raise ValueError("invalid_original_mesh_stream_extent")
        file = source / name
        if name not in verified_streams:
            verify(file, stream_size, sha)
            verified_streams.add(name)
        with file.open("rb") as handle:
            handle.seek(offset)
            streamed = handle.read(size)
        if len(streamed) != size or (payload and streamed != payload):
            raise ValueError("conflicting_original_mesh_vertex_payload")
        payload = streamed
    return geometry(tree, payload, bytes(tree["m_IndexBuffer"]))


def geometry(tree, payload, indices, *, exported=False):
    def packed_bytes(value, *, uint32=False):
        if exported:
            return hex_payload(value)
        if uint32:
            return struct.pack(f"<{len(value)}I", *value)
        return bytes(value)

    vertex = tree["m_VertexData"]
    compressed = tree["m_CompressedMesh"]
    # Include the packed attributes even when their logical source count is zero.
    packed = {
        key: (value["m_NumItems"], value["m_BitSize"],
              float32(value.get("m_Range")), float32(value.get("m_Start")),
              digest(packed_bytes(value["m_Data"])))
        for key, value in compressed.items()
        if isinstance(value, dict)
    }
    return {
        "vertex_count": vertex["m_VertexCount"],
        "vertex_channels": tuple(tuple(c[k] for k in CHANNEL_FIELDS) for c in vertex["m_Channels"]),
        "vertex_buffer": digest(payload),
        "index_format": tree["m_IndexFormat"],
        "index_buffer": digest(indices),
        "submesh_ranges": tuple(tuple(s[k] for k in SUBMESH_FIELDS) for s in tree["m_SubMeshes"]),
        "compressed_attributes": (compressed["m_UVInfo"], packed),
        "bind_pose_matrices": tuple(tuple(float32(matrix[f"e{r}{c}"]) for r in range(4)
                                          for c in range(4)) for matrix in tree["m_BindPose"]),
        "bone_name_hashes": digest(packed_bytes(tree["m_BoneNameHashes"], uint32=True)),
        "variable_bone_weights": digest(packed_bytes(tree["m_VariableBoneCountWeights"]["m_Data"],
                                                     uint32=True)),
    }


def float32(value):
    return struct.pack("<f", value) if value is not None else None


FLOAT32_ZERO = frozenset((float32(-0.0), float32(0.0)))


def compare_geometry(expected, actual):
    differences = [field for field in expected if expected[field] != actual[field]]
    if "bind_pose_matrices" not in differences:
        return differences, 0
    source, exported = expected["bind_pose_matrices"], actual["bind_pose_matrices"]
    if len(source) != len(exported):
        return differences, 0
    zeros = 0
    for source_matrix, exported_matrix in zip(source, exported):
        for a, b in zip(source_matrix, exported_matrix, strict=True):
            if a == b:
                continue
            if a not in FLOAT32_ZERO or b not in FLOAT32_ZERO:
                return differences, 0
            zeros += 1
    differences.remove("bind_pose_matrices")
    return differences, zeros


def digest(payload):
    return len(payload), hashlib.sha256(bytes(payload)).hexdigest()


def hex_payload(value):
    if value in (None, "", []):
        return b""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]+", value):
        raise ValueError("invalid_exported_mesh_hex")
    return bytes.fromhex(value)


def export_geometry(path, fid):
    from scripts.compare_exported_mesh_geometry import load_mesh_yaml

    text = path.read_text(encoding="utf-8-sig")
    if [(int(h[1]), int(h[2])) for h in HEADER.finditer(text)] != [(43, fid)]:
        raise ValueError("wrong_exported_mesh_yaml_identity")
    tree = load_mesh_yaml(text)
    vertex = tree["m_VertexData"]
    payload = hex_payload(vertex["_typelessdata"])
    if vertex["m_DataSize"] != len(payload) or tree["m_StreamData"]["size"] != 0:
        raise ValueError("invalid_exported_mesh_vertex_storage")
    indices = hex_payload(tree["m_IndexBuffer"])
    return geometry(tree, payload, indices, exported=True)


def trace_meshes(trace, same_instance, owners):
    if (trace.get("schema_version") != 1
            or not isinstance(same_instance, str) or not HEX32.fullmatch(same_instance)
            or trace.get("export_instance") != same_instance
            or not isinstance(trace.get("meshes"), list)):
        raise ValueError("invalid_same_instance_mesh_trace")
    result = {}
    for row in trace["meshes"]:
        src = row["source"]
        name = Path(src["owner"]).name
        if name not in owners:
            continue
        if src["owner"] not in (name, "Raft_Data/" + name) or type(src["path_id"]) is not int:
            raise ValueError("invalid_original_mesh_trace_identity")
        key = name, src["path_id"]
        if key in result:
            raise ValueError("duplicate_original_mesh_trace_identity")
        result[key] = row
    return result


def index_project(project, guids):
    assets = project / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_or_unsafe_export_assets")
    targets = {}
    for meta in assets.rglob("*.meta"):
        if meta.is_symlink():
            raise ValueError("unexpected_export_meta_symlink")
        hits = GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if not hits or hits[0].lower() not in guids:
            continue
        guid = hits[0].lower()
        target = meta.with_suffix("")
        if len(hits) != 1 or guid in targets:
            raise ValueError("ambiguous_exported_mesh_guid")
        if target.suffix != ".asset" or not target.is_file() or target.is_symlink():
            raise ValueError("invalid_exported_mesh_asset")
        targets[guid] = target
    return targets


def inspect(source, records, project, trace, same_instance, owners=OWNERS, *, stream_source=None):
    import UnityPy
    from yaml import YAMLError

    meshes = trace_meshes(trace, same_instance, owners)
    guids = {
        row["export"]["guid"] for row in meshes.values()
        if row["exportable"] is True and HEX32.fullmatch(row["export"]["guid"])
    }
    targets = index_project(project, guids)
    counts, drift, verified_streams, used_targets, seen = Counter(), Counter(), set(), set(), set()
    for owner in owners:
        path = source / owner
        _, size, sha = records["Raft_Data/" + owner]
        verify(path, size, sha)
        env = UnityPy.load(str(path))
        for obj in env.file.objects.values():
            if obj.type.name != "Mesh":
                continue
            key = owner, obj.path_id
            counts["source_meshes"] += 1
            row = meshes.get(key)
            if row is None:
                counts["missing_export_trace"] += 1
                continue
            seen.add(key)
            if row["exportable"] is not True:
                counts["non_exportable_source_meshes"] += 1
                continue
            pointer = row["export"]
            guid, fid = pointer["guid"], pointer["file_id"]
            target = targets.get(guid)
            if target is None:
                counts["missing_exported_mesh_asset"] += 1
                continue
            if type(fid) is not int or not fid or pointer["type"] not in (2, 3):
                counts["invalid_exported_mesh_pointer"] += 1
                continue
            if (guid, fid) in used_targets:
                counts["ambiguous_exported_mesh_target"] += 1
                continue
            used_targets.add((guid, fid))
            try:
                expected = source_geometry(
                    obj.read_typetree(), stream_source or source, records, verified_streams,
                )
                actual = export_geometry(target, fid)
            except (ValueError, KeyError, TypeError, OSError, YAMLError, struct.error):
                counts["source_or_export_decode_error"] += 1
                continue
            differences, signed_zeros = compare_geometry(expected, actual)
            if signed_zeros:
                counts["meshes_with_bind_pose_zero_sign_difference"] += 1
                counts["bind_pose_zero_sign_differences"] += signed_zeros
            if differences:
                counts["mesh_with_geometry_drift"] += 1
                drift.update(differences)
            else:
                counts["matched_mesh_geometry"] += 1
        del env
        gc.collect()
    counts["unmatched_source_trace_records"] = len(meshes.keys() - seen)
    return {
        "schema": "GT_ORIGINAL_MESH_EXPORT_GEOMETRY_V1",
        "authenticated_source_owners": len(owners),
        "authenticated_mesh_streams": len(verified_streams),
        "counts": dict(sorted(counts.items())),
        "mismatch_fields": dict(sorted(drift.items())),
        "all_source_mesh_geometry_matches": (
            bool(counts["source_meshes"]) and counts["matched_mesh_geometry"] == counts["source_meshes"]
            and not counts["unmatched_source_trace_records"]
        ),
        "renderer_bindings_or_unity_import_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("source", "zip2-checkout", "project", "mesh-trace", "export-trace", "report"):
        parser.add_argument("--" + option, type=Path, required=True)
    parser.add_argument("--stream-source", type=Path)
    args = parser.parse_args()
    if any(args.report.resolve().is_relative_to(root.resolve())
           for root in (args.source, args.stream_source, args.project, args.zip2_checkout)
           if root is not None):
        parser.error("aggregate report must remain outside the source and exported project")
    try:
        report = inspect(
            args.source, manifest(args.zip2_checkout), args.project,
            json.loads(args.mesh_trace.read_text()),
            json.loads(args.export_trace.read_text())["export_instance"],
            stream_source=args.stream_source,
        )
    except Exception as ex:
        # Only publish aggregate information, including when parsing fails.
        report = {"schema": "GT_ORIGINAL_MESH_EXPORT_GEOMETRY_V1",
                  "failure_type": type(ex).__name__, "all_source_mesh_geometry_matches": False}
    with args.report.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2, sort_keys=True)
        output.write("\n")
    print("GT_ORIGINAL_MESH_EXPORT_GEOMETRY " + json.dumps(report, sort_keys=True))
    return 0 if report["all_source_mesh_geometry_matches"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
