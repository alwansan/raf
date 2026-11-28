#!/usr/bin/env python3
"""Read-only, bounded actual original scene lighting census. Aggregates only."""
import argparse
from collections import Counter
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

PIN = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
MANIFEST_BLOB = "4201fda426d80caba36c275ceaddb440b05c5b4e"
MAX_SCENE_BYTES = 80 * 1024 * 1024
MAX_ALL_BYTES = 512 * 1024 * 1024
MAX_OBJECTS = 500_000
MAX_MAPS = 65535
RENDERERS = {"MeshRenderer", "SkinnedMeshRenderer", "Terrain", "TrailRenderer",
             "LineRenderer", "ParticleSystemRenderer"}
FIELDS = ("m_LightmapColor", "m_LightmapDir", "m_ShadowMask")

class AuditError(ValueError):
    pass

def need(flag, code):
    if not flag:
        raise AuditError(code)

def safe(path, directory=False):
    need(not any(p.is_symlink() for p in (path, *path.parents)), "linked_path")
    need(path.is_dir() if directory else path.is_file(), "missing_regular_path")
    return path

def hash_file(path, expected, blob=None, sink=None):
    safe(path)
    need(type(expected) is int and 0 < expected <= MAX_SCENE_BYTES, "file_budget")
    need(path.stat().st_size == expected, "size_mismatch")
    h = hashlib.sha256()
    g = hashlib.sha1(("blob %d\0" % expected).encode("ascii"))
    n = 0
    with path.open("rb") as f:
        while data := f.read(1024 * 1024):
            n += len(data)
            need(n <= expected, "stream_overrun")
            h.update(data)
            g.update(data)
            if sink is not None:
                sink.write(data)
    need(n == expected, "stream_size_mismatch")
    if blob is not None:
        need(g.hexdigest() == blob, "git_blob_mismatch")
    return h.hexdigest()

def load_pins(path, source):
    pins = json.loads(safe(path).read_text(encoding="utf8"))
    need(pins["source_commit"] == PIN and pins["manifest_git_blob"] == MANIFEST_BLOB, "source_pin")
    rows = pins["levels"]
    need([r["level"] for r in rows] == list(range(6,40)) and pins["selected_count"] == 34, "scene_population")
    need(sum(r["bytes"] for r in rows) == pins["selected_bytes"] <= MAX_ALL_BYTES, "source_total_budget")
    manifest = safe(source / "RAFT_FILE_MANIFEST.tsv")
    hash_file(manifest, manifest.stat().st_size, MANIFEST_BLOB)
    table = {}
    with manifest.open(encoding="utf8") as f:
        need(f.readline().rstrip("\r\n") == "kind\tbytes\tsha256\tmode\trelative_path_under_Raft", "manifest_schema")
        for line in f:
            fields = line.rstrip("\r\n").split("\t")
            need(len(fields) == 5, "manifest_row")
            kind, size, digest, mode, name = fields
            if re.fullmatch(r"Raft_Data/level\d+", name):
                need(name not in table, "duplicate_scene_pin")
                table[name] = (kind, int(size), digest)
    need(set(table) == {f"Raft_Data/level{i}" for i in range(40)}, "all_scene_manifest_population")
    for row in rows:
        n = row["level"]
        need(table[f"Raft_Data/level{n}"] == (row["kind"], row["bytes"], row["sha256"]), "scene_manifest_mismatch")
        need(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None and re.fullmatch(r"[0-9a-f]{40}", row["git_object"]) is not None, "bad_pin")
    return rows

@contextlib.contextmanager
def verified_scene(root, row, tmp):
    path = root / "Raft" / "Raft_Data" / f"level{row['level']}"
    size = row["bytes"]
    need(0 < size <= MAX_SCENE_BYTES, "scene_budget")
    if row["kind"] == "plain":
        need(hash_file(path, size, row["git_object"]) == row["sha256"], "scene_sha256_mismatch")
        yield path
        return
    need(row["kind"] == "split", "source_kind")
    safe(path, True)
    parts = row["parts"]
    need([p["name"] for p in parts] == [f"part-{i:05d}" for i in range(len(parts))] and len(parts) == 2, "chunk_order")
    need(sorted(p.name for p in path.iterdir() if p.name.startswith("part-")) == [p["name"] for p in parts], "chunk_population")
    need(sum(p["bytes"] for p in parts) == size, "chunk_size_total")
    target = tmp / f"level{row['level']}"
    try:
        with target.open("xb") as out:
            for p in parts:
                hash_file(path / p["name"], p["bytes"], p["blob"], out)
        need(hash_file(target, size) == row["sha256"], "joined_scene_sha256_mismatch")
        yield target
    finally:
        if target.is_file():
            target.unlink()

def int64(x):
    return type(x) is int and -(1 << 63) <= x < (1 << 63)

def kind(obj):
    t = getattr(obj, "type", None)
    return getattr(t, "name", None), getattr(t, "value", None)

def pointer(value, table, expected):
    if not isinstance(value, dict):
        return "unknown"
    f, p = value.get("m_FileID"), value.get("m_PathID")
    if type(f) is not int or not 0 <= f < (1 << 31) or not int64(p):
        return "unknown"
    if p == 0:
        return "null" if f == 0 else "unknown"
    if f:
        return "external_unverified"
    if p not in table:
        return "local_missing"
    name, cid = kind(table[p])
    if type(cid) is not int or not isinstance(name, str) or (name == expected[0]) != (cid == expected[1]):
        return "local_class_unknown"
    return "local_typed" if (name, cid) == expected else "local_wrong_class"

def tree(obj):
    try:
        d = obj.read_typetree(check_read=False)
        return d if isinstance(d, dict) else None
    except Exception:
        return None

def finite(x):
    return type(x) in (int, float) and math.isfinite(x)

def census(objects):
    need(len(objects) <= MAX_OBJECTS, "scene_object_budget")
    table = {}
    for obj in objects:
        pid = getattr(obj, "path_id", None)
        need(int64(pid) and pid != 0 and pid not in table, "bad_or_duplicate_object_id")
        table[pid] = obj
    c = Counter()
    c["object_headers"] = len(table)
    settings, assigned, render_settings = [], [], []
    for o in objects:
        name, cid = kind(o)
        if name == "LightmapSettings" or cid == 157:
            c["lightmap_settings_headers"] += 1
            d = tree(o) if (name, cid) == ("LightmapSettings",157) else None
            a = d.get("m_Lightmaps") if d is not None else None
            if not isinstance(a, list):
                c["lightmap_settings_unknown"] += 1
                settings.append(None)
            else:
                need(len(a) <= MAX_MAPS, "map_budget")
                settings.append(a)
            continue
        if name in RENDERERS:
            c["renderer_headers"] += 1
            d = tree(o)
            idx = d.get("m_LightmapIndex") if d is not None else None
            if type(idx) is not int:
                c["renderer_index_unknown"] += 1
            elif idx in (-1,65535):
                c["renderer_unassigned"] += 1
            elif idx == 65534:
                c["renderer_reserved_unverified"] += 1
            elif 0 <= idx < 65534:
                assigned.append(idx)
            else:
                c["renderer_index_unknown"] += 1
            continue
        if name == "Light" or cid == 108:
            c["light_headers"] += 1
            d = tree(o) if (name,cid) == ("Light",108) else None
            if d is None:
                c["light_typetree_unknown"] += 1
                continue
            c["light_decoded"] += 1
            en = d.get("m_Enabled")
            c["light_enabled_" + ("yes" if type(en) is int and en == 1 else "no" if type(en) is int and en == 0 else "unknown")] += 1
            owner = d.get("m_GameObject")
            state = pointer(owner, table, ("GameObject",1))
            c["light_owner_" + state] += 1
            if state == "local_typed":
                go = tree(table[owner["m_PathID"]])
                active = go.get("m_IsActive") if go is not None else None
                c["light_owner_self_active_" + ("yes" if type(active) is int and active == 1 else "no" if type(active) is int and active == 0 else "unknown")] += 1
            for k, label in (("m_Intensity","intensity"),("m_Range","range")):
                v = d.get(k)
                c["light_"+label+"_"+("positive" if finite(v) and v > 0 else "zero" if finite(v) and v == 0 else "negative" if finite(v) else "unknown")] += 1
            continue
        if name == "RenderSettings" or cid == 104:
            c["render_settings_headers"] += 1
            d = tree(o) if (name,cid) == ("RenderSettings",104) else None
            render_settings.append(d)
    c["renderer_assigned"] = len(assigned)
    local_complete = []
    if len(settings) == 1 and settings[0] is not None:
        c["unique_decoded_lightmap_settings"] = 1
        c["serialized_map_entries"] = len(settings[0])
        for entry in settings[0]:
            d = entry if isinstance(entry,dict) else {}
            states = {k: pointer(d.get(k),table,("Texture2D",28)) for k in FIELDS}
            for k, v in states.items():
                c[k+"_"+v] += 1
            local_complete.append(states[FIELDS[0]] == "local_typed" and all(states[k] in ("null","local_typed") for k in FIELDS[1:]))
        for idx in assigned:
            if idx >= len(local_complete):
                c["renderer_index_out_of_range"] += 1
            elif local_complete[idx]:
                c["renderer_complete_local_links"] += 1
            else:
                c["renderer_unresolved_map_links"] += 1
    else:
        c["lightmap_settings_ambiguous_or_absent"] = 1
        c["renderer_settings_unresolved"] = len(assigned)
    if len(render_settings) == 1 and render_settings[0] is not None:
        c["unique_decoded_render_settings"] = 1
        d = render_settings[0]
        c["render_settings_sun_"+pointer(d.get("m_Sun"),table,("Light",108))] += 1
        mode = d.get("m_AmbientMode")
        c["render_settings_ambient_mode_known" if type(mode) is int and mode in (0,1,3) else "render_settings_ambient_mode_unknown"] += 1
    else:
        c["render_settings_ambiguous_or_absent"] = 1
    no_baked = (c["unique_decoded_lightmap_settings"] == 1 and c["serialized_map_entries"] == 0
        and c["renderer_headers"] == c["renderer_unassigned"]
        and not c["renderer_index_unknown"] and not c["renderer_reserved_unverified"])
    return {"counts": dict(sorted(c.items())), "no_baked_lightmap_assignments_observed": no_baked}

def run(source, pins, output):
    import UnityPy
    source = safe(source, True)
    rows = load_pins(pins, source)
    out = {"source_commit":PIN,"scope":"level6..39; prior six separate", "unitypy_version":getattr(UnityPy,"__version__","unknown"),
        "scenes":{},"source_export_mapping_proven":False,"device_pixels_proven":False,"original_assets_modified":False}
    with tempfile.TemporaryDirectory(prefix="gt-scene-lighting-") as td, open(os.devnull,"w") as quiet:
        for row in rows:
            n = row["level"]
            item = {"bytes":row["bytes"],"sha256":row["sha256"],"kind":row["kind"],"source_verified":False,"status":"UNKNOWN"}
            try:
                with verified_scene(source,row,Path(td)) as path:
                    item["source_verified"] = True
                    # Never publish parser text, source object identifiers or raw values.
                    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                        env = UnityPy.load(str(path))
                        objmap = env.file.objects
                        need(len(objmap)<=MAX_OBJECTS,"scene_object_budget")
                        item.update(census(list(objmap.values())))
                        del objmap, env
                    item["status"] = "OBSERVED"
            except AuditError as e:
                item["reason"] = str(e)
            except Exception as e:
                # Type only, no source path/data and no stack trace.
                item["reason"] = "reader_" + type(e).__name__
            out["scenes"][str(n)] = item
    scenes = list(out["scenes"].values())
    observed = [x for x in scenes if x["status"] == "OBSERVED"]
    total = Counter()
    for item in observed:
        total.update(item["counts"])
    out.update(selected_scenes=len(scenes),source_verified_scenes=sum(x["source_verified"] for x in scenes),
        observed_scenes=len(observed),no_baked_assignment_scenes=sum(x["no_baked_lightmap_assignments_observed"] for x in observed),
        aggregate_counts=dict(sorted(total.items())),status="OBSERVED_ALL_SELECTED" if len(observed)==34 else "PARTIAL_INCONCLUSIVE")
    output.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("GT_REMAINING_SCENE_LIGHTING "+json.dumps(out,sort_keys=True,separators=(",",":")))
    return 0 if len(observed)==34 else 2

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--pins",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    raise SystemExit(run(a.source,a.pins,a.output))
