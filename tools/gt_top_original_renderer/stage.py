"""Derive a private native MeshRenderer/MeshFilter/Mesh trace without changing W1/B02/B21."""
import argparse
import hashlib
from pathlib import Path
from scripts.b21_stage_light_lineage import render as b21_render

B21_SHA = "afc8c03f4ca838df3365a0387859100baf7f40e25d268f8c47910056ae60af07"

def render(base):
    raw = b21_render(base)
    if hashlib.sha256(raw).hexdigest() != B21_SHA:
        raise ValueError("unreviewed_B21_composition")
    text = raw.decode("utf-8")
    changes = {
        "RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE": "RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE",
        "lightPath": "rendererPath",
        "CaptureLightObjects": "CaptureRendererObjects",
        "if (asset.ClassID is not (1 or 108)) // Native GameObject1 and Light108 only.":
            "if (asset.ClassID is not (23 or 33 or 43)) // Native MeshRenderer23, MeshFilter33, Mesh43 only.",
        "if (asset.ClassID == 108) nonExportable++;": "if (asset.ClassID == 23) nonExportable++;",
        "nonExportableGameObjects": "nonExportableDependencies",
        "nonexportable_light_objects_skipped": "nonexportable_renderer_objects_skipped",
        "nonexportable_gameobjects_skipped": "nonexportable_mesh_dependencies_skipped",
    }
    for old, new in changes.items():
        if old not in text:
            raise ValueError("missing_private_trace_anchor")
        text = text.replace(old, new)
    if text.count("CaptureRendererObjects(") != 2 or text.count('json.WriteString("export_instance", exportInstance);') != 3:
        raise ValueError("unexpected_private_capture_shape")
    return text.encode("utf-8")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-helper", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    a = p.parse_args()
    if a.base_helper.is_symlink() or a.destination.exists() or a.destination.is_symlink():
        raise ValueError("unsafe_staging_path")
    with a.destination.open("xb") as f:
        f.write(render(a.base_helper.read_bytes()))
    print("GT_TOP_RENDERER_PRIVATE_TRACE_STAGED=true")

if __name__ == "__main__":
    main()
