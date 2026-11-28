"""Compose only a disposable, private B21-derived class104 same-instance trace."""
import argparse
import hashlib
from pathlib import Path
from scripts import b21_stage_light_lineage as b21
from scripts import b02_stage_texture_lineage as b02
from tools.gt_light_same_export.stage_trace import once

def render(raw):
    text=b21.render(raw).decode("utf8")
    text=once(text,'if (asset.ClassID is not (1 or 108)) // Native GameObject1 and Light108 only.',
              'if (asset.ClassID != 104 || asset.Collection.Name != "level24") // Exact RenderSettings only.')
    text=once(text,'int nonExportableGameObjects = 0;','')
    text=once(text,'if (asset.ClassID == 108) nonExportable++;\n                    else nonExportableGameObjects++;','nonExportable++;')
    text=once(text,'json.WriteNumber("nonexportable_light_objects_skipped", nonExportable);','json.WriteNumber("nonexportable_render_settings_skipped", nonExportable);')
    text=once(text,'json.WriteNumber("nonexportable_gameobjects_skipped", nonExportableGameObjects);','')
    text=once(text,'RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE','RAFT_PRIVATE_EXPORT_AMBIENT_LINEAGE')
    if text.count('json.WriteString("export_instance", exportInstance);')!=3 or text.count('FileMode.CreateNew')!=3 or text.count(b02.REVIEWED_SHADER_FILTER)!=1 or text.count('if (asset.ClassID != 28)')!=1:
        raise ValueError("ambient_capture_preservation")
    return text.encode("utf8")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base-helper",type=Path,required=True)
    p.add_argument("--destination",type=Path,required=True)
    x=p.parse_args()
    if x.base_helper.is_symlink() or x.destination.exists() or x.destination.is_symlink() or x.destination.parent.is_symlink():
        raise ValueError("unsafe_private_destination")
    out=render(x.base_helper.read_bytes())
    with x.destination.open("xb") as f:f.write(out)
    print("GT_AMBIENT_HELPER_SHA256="+hashlib.sha256(out).hexdigest())
