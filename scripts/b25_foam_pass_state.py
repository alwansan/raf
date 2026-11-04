"""B25: original Foam pass-state authentication and private source staging.

No shader/HLSL/state values are published or installed into Unity.
"""
import argparse
import hashlib
import json
from pathlib import Path
from scripts.b24_original_foam_stage_translation import TARGET, OBJECT_ID, ORIGINAL_OBJECT_SHA256
from scripts.w1_depth_shaderlab import render_state
from scripts.w1_stage_zip2_owners import PINS, fingerprint

OWNER = "Raft_Data/sharedassets0.assets"

def inspect(parsed):
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Foam shader identity changed")
    subs = parsed.get("m_SubShaders")
    if not isinstance(subs, list) or len(subs) != 1:
        raise ValueError("Foam subshader topology changed")
    passes = subs[0].get("m_Passes")
    if not isinstance(passes, list) or len(passes) != 2:
        raise ValueError("Foam two-pass topology changed")
    texts = []
    for entry in passes:
        if entry.get("m_Type") != 0 or not isinstance(entry.get("m_State"), dict):
            raise ValueError("Foam pass kind or render state changed")
        text = render_state(entry["m_State"]) + "\n"
        if not 0 < len(text.encode("utf-8")) <= 65536:
            raise ValueError("Foam render-state bounds changed")
        texts.append(text)
    report = {"original_passes": 2,
              "states": [{"index": i, "sha256": hashlib.sha256(x.encode()).hexdigest(),
                          "bytes": len(x.encode())} for i, x in enumerate(texts)],
              "shaderlab_installed": False, "cb_resource_binding_verified": False,
              "device_verified": False, "state_source_published": False}
    return report, texts

def physical(path):
    return not any(x.is_symlink() for x in (path, *path.parents))

def save_private(private_dir, texts):
    if not private_dir.is_absolute() or not private_dir.is_dir() or not physical(private_dir):
        raise ValueError("Unsafe private output")
    files = [private_dir / ("foam-pass-%02d-state.txt" % i) for i in range(len(texts))]
    if any(x.exists() or x.is_symlink() for x in files):
        raise ValueError("Private output already exists")
    written = []
    try:
        for file, text in zip(files, texts):
            with file.open("xb") as out:
                written.append(file)
                out.write(text.encode())
            if file.read_text() != text:
                raise ValueError("Private output mismatch")
    except BaseException:
        for file in written:
            if not file.is_symlink() and file.is_file():
                file.unlink()
        raise

def probe(source, private_dir):
    path = source / OWNER
    if not physical(path) or not path.is_file() or fingerprint(path) != PINS[OWNER]:
        raise ValueError("Original ZIP2 provider SHA mismatch")
    import UnityPy
    env = UnityPy.load(str(path))
    objects = [o for o in env.file.objects.values() if
               o.type.name == "Shader" and int(o.path_id) == OBJECT_ID]
    if len(objects) != 1:
        raise ValueError("Original Foam object count changed")
    obj = objects[0]
    if hashlib.sha256(obj.get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original Foam object SHA mismatch")
    report, text = inspect(obj.read_typetree().get("m_ParsedForm"))
    save_private(private_dir, text)
    return {"status": "source_staged", "source_sha256": PINS[OWNER][1],
            "object_sha256": ORIGINAL_OBJECT_SHA256, **report}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        result, code = probe(args.source, args.private_dir), 0
    except Exception as exc:
        result, code = {"status": "incomplete", "reason_type": type(exc).__name__,
                        "state_source_published": False, "device_verified": False}, 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, sort_keys=True) + "\n")
    print("B25_FOAM_ORIGINAL_RENDER_STATE " + json.dumps(result, sort_keys=True))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
