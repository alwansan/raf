"""Verify native Class187 YAML payloads against a pinned ZIP2 owner and stream."""
import argparse
import csv
import json
from pathlib import Path
import re

from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.verify_export_lineage import identity, pointer

FIELDS = ("m_Width", "m_Height", "m_Depth", "m_MipCount", "m_Format")


def inspect(source, manifest, trace_file, assets, owner):
    import UnityPy

    pins = read_expected(manifest)
    stream_name = owner + ".resS"
    _, size, digest = pins[owner]
    verify(source / owner, size, digest)
    with manifest.open(encoding="utf-8") as table:
        matches = [row for row in csv.DictReader(table, delimiter="\t")
                   if row["relative_path_under_Raft"] == "Raft_Data/" + stream_name]
    if len(matches) != 1:
        raise ValueError("missing_or_duplicate_array_stream_pin")
    stream_size = int(matches[0]["bytes"])
    verify(source / stream_name, stream_size, matches[0]["sha256"])

    trace = json.loads(trace_file.read_text(encoding="utf-8"))
    if trace["schema_version"] != 1 or not re.fullmatch(r"[0-9a-f]{32}", trace["export_instance"]):
        raise ValueError("invalid_native_array_export_trace")
    targets = {}
    for row in trace["objects"]:
        if row["class_id"] != 187:
            continue
        collection, path_id = identity(row["source"])
        if collection == owner:
            file_id, guid, kind = pointer(row["export"])
            if file_id != 18700000 or kind != "2" or path_id in targets or guid in targets.values():
                raise ValueError("invalid_native_array_export_pointer")
            targets[path_id] = guid

    files = {}
    for meta in assets.rglob("*.asset.meta"):
        match = re.search(r"(?m)^guid: ([0-9a-f]{32})$", meta.read_text(encoding="utf-8-sig"))
        if match and match[1] in targets.values():
            guid = match[1]
            if guid in files:
                raise ValueError("duplicate_native_array_export_guid")
            files[guid] = meta.with_suffix("")

    arrays = layers = total_bytes = 0
    with (source / stream_name).open("rb") as stream:
        for obj in UnityPy.load(str(source / owner)).objects:
            if obj.type.name != "Texture2DArray":
                continue
            yaml = files.pop(targets.pop(obj.path_id)).read_text(encoding="utf-8-sig")
            if not re.search(r"(?m)^--- !u!187 &18700000$", yaml):
                raise ValueError("invalid_native_array_yaml_identity")
            tree = obj.read_typetree()
            for field in FIELDS:
                value = re.search(rf"(?m)^  {field}: (\d+)$", yaml)
                if not value or int(value[1]) != tree[field]:
                    raise ValueError("native_array_metadata_mismatch")
            data = tree["m_StreamData"]
            if (Path(data["path"]).name != stream_name or data["size"] <= 0 or
                    not 0 <= data["offset"] <= stream_size - data["size"]):
                raise ValueError("invalid_original_array_stream_range")
            stream.seek(data["offset"])
            payload = re.search(r"(?m)^  _typelessdata: ([0-9a-fA-F]+)$", yaml)
            if not payload or bytes.fromhex(payload[1]) != stream.read(data["size"]):
                raise ValueError("native_array_mip_payload_mismatch")
            arrays += 1
            layers += tree["m_Depth"]
            total_bytes += data["size"]
    if not arrays or targets or files:
        raise ValueError("incomplete_native_array_export_scope")
    return {"arrays": arrays, "layers": layers, "exact_mip_payload_bytes": total_bytes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "manifest", "trace-file", "assets"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--owner", required=True)
    report = inspect(**vars(parser.parse_args()))
    print("GT_NATIVE_ARRAY_MIPS " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
