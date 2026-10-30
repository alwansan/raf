#!/usr/bin/env python3
"""Compare finite positions in two ephemeral exports; never rewrite their assets."""
import argparse
import hashlib
from collections import Counter
import json
import math
from pathlib import Path
import re
import struct


def load_mesh_yaml(text):
    import yaml
    class MeshLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            for key, value in node.value:
                if key.value in ('_typelessdata', 'm_IndexBuffer') and isinstance(value, yaml.ScalarNode):
                    value.tag = 'tag:yaml.org,2002:str'
            return super().construct_mapping(node, deep=deep)
    text = re.sub(r'(?m)^%[^\n]*\n', '', text)
    text = re.sub(r'(?m)^--- !u!43 &[^\n]*', '---', text)
    return yaml.load(text, Loader=MeshLoader)['Mesh']


def positions(tree):
    data = tree["m_VertexData"]
    count = data["m_VertexCount"]
    if type(count) is not int or count <= 0:
        raise ValueError("empty-vertices")
    channels = data["m_Channels"]
    position = channels[0]
    if position["format"] not in (0, 1) or (position["dimension"] & 15) != 3:
        raise ValueError("unsupported-position-format")
    widths = {0: 4, 1: 2, 2: 1, 3: 1, 4: 2, 5: 2,
              6: 1, 7: 1, 8: 2, 9: 2, 10: 4, 11: 4}
    strides = Counter()
    for channel in channels:
        dimension = channel["dimension"] & 15
        if dimension:
            strides[channel["stream"]] += dimension * widths[channel["format"]]
    stream = position["stream"]
    offset = 0
    for index in range(stream):
        offset += count * strides[index]
        offset = (offset + 15) & ~15
    offset += position["offset"]
    encoded = data["_typelessdata"]
    raw = bytes.fromhex("" if encoded is None else str(encoded))
    codec = struct.Struct("<3" + ("f" if position["format"] == 0 else "e"))
    if offset + (count - 1) * strides[stream] + codec.size > len(raw):
        raise ValueError("truncated-positions")
    return [codec.unpack_from(raw, offset + index * strides[stream]) for index in range(count)]


def inspect(root, wanted):
    rows = {}
    errors = Counter()
    for path in sorted((root / "Assets/Mesh").glob("*.asset")):
        try:
            text = path.read_text(encoding="utf8")
            tree = load_mesh_yaml(text)
            if tree.get("m_Name") not in wanted:
                continue
            meta = path.with_suffix(path.suffix + ".meta").read_text()
            guid = re.search(r"(?m)^guid:\s*([a-f0-9]{32})", meta).group(1)
            meta_sha256 = hashlib.sha256(path.with_suffix(path.suffix + '.meta').read_bytes()).hexdigest()
            try:
                values = positions(tree)
                bad = sum(not all(math.isfinite(v) for v in vertex) for vertex in values)
                rows[path.name] = {"guid": guid, "meta_sha256": meta_sha256, "nonfinite": bad, "vertices": len(values),
                                   "valid_positions": bad == 0, "position_status": "decoded"}
            except ValueError as exc:
                if str(exc) not in ("empty-vertices", "unsupported-position-format", "truncated-positions"):
                    raise
                # Missing-stream baseline is an expected observation, not a YAML parse failure.
                # Retain its asset identity so GUID checks still compare the same objects.
                rows[path.name] = {"guid": guid, "meta_sha256": meta_sha256, "nonfinite": 0,
                    "vertices": tree["m_VertexData"]["m_VertexCount"],
                    "valid_positions": False, "position_status": str(exc)}
        except Exception as exc:
            errors[type(exc).__name__] += 1
    return rows, dict(errors)


def compare(before, after):
    common = set(before) & set(after)
    return {"before_meshes": len(before), "after_meshes": len(after),
            "common_meshes": len(common),
            "before_nonfinite_meshes": sum(r["nonfinite"] > 0 for r in before.values()),
            "after_nonfinite_meshes": sum(r["nonfinite"] > 0 for r in after.values()),
            "before_invalid_position_meshes": sum(not r.get("valid_positions", True) for r in before.values()),
            "after_invalid_position_meshes": sum(not r.get("valid_positions", True) for r in after.values()),
            "before_position_status": dict(Counter(r.get("position_status", "decoded") for r in before.values())),
            "common_meta_guid_changes": sum(before[k]["guid"] != after[k]["guid"] for k in common),
            "common_meta_byte_changes": sum(before[k].get("meta_sha256") != after[k].get("meta_sha256") for k in common),
            "common_vertex_count_changes": sum(before[k]["vertices"] != after[k]["vertices"] for k in common)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--stream", choices=["sharedassets29.assets.resS", "sharedassets24.assets.resS"],
                        default="sharedassets29.assets.resS")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    wanted = {r["mesh_name"] for p in ledger["providers"]
              if p["stream"] == args.stream for r in p["meshes"]}
    before, before_errors = inspect(args.before, wanted)
    if args.after is None:
        result = dict(compare(before, {}), before_parse_errors=before_errors)
        print("RAFT_BASELINE_EXPORT_GEOMETRY " + json.dumps(result, sort_keys=True))
        if not before or before_errors:
            raise SystemExit("Baseline analysis incomplete")
        raise SystemExit(0)
    after, after_errors = inspect(args.after, wanted)
    result = dict(compare(before, after), before_parse_errors=before_errors, after_parse_errors=after_errors)
    print("RAFT_EXPORT_GEOMETRY_COMPARISON " + json.dumps(result, sort_keys=True))
    if (not before or not after or before_errors or after_errors or
            result["common_meshes"] != len(before) or len(before) != len(after) or
            result["common_meta_guid_changes"] or result["common_meta_byte_changes"] or result["after_invalid_position_meshes"]):
        raise SystemExit("Export comparison incomplete or geometry still invalid; inspect diagnostics")
