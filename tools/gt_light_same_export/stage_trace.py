"""Stage optional B21 hierarchy capture in a disposable public exporter only."""
import argparse
from pathlib import Path
import hashlib
from scripts import b21_stage_light_lineage as b21
from scripts import b02_stage_texture_lineage as b02

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("hierarchy_capture_anchor")
    return text.replace(old, new)

def render(base):
    text = b21.render(base).decode("utf8")
    text = once(text, 'if (asset.ClassID is not (1 or 108)) // Native GameObject1 and Light108 only.',
                'if (asset.ClassID is not (1 or 4 or 108 or 224) || asset.Collection.Name != "level38") // Selected native scene only.')
    text = once(text, 'int nonExportableGameObjects = 0;', 'int nonExportableGameObjects = 0;\n        int nonExportableTransforms = 0;')
    text = once(text, 'else nonExportableGameObjects++;',
                'else if (asset.ClassID == 1) nonExportableGameObjects++;\n                    else nonExportableTransforms++;')
    text = once(text, 'json.WriteNumber("nonexportable_gameobjects_skipped", nonExportableGameObjects);',
                'json.WriteNumber("nonexportable_gameobjects_skipped", nonExportableGameObjects);\n        json.WriteNumber("nonexportable_transforms_skipped", nonExportableTransforms);')
    if (text.count('json.WriteString("export_instance", exportInstance);') != 3 or
        text.count('FileMode.CreateNew') != 3 or text.count(b02.REVIEWED_SHADER_FILTER) != 1 or
        text.count('if (asset.ClassID != 28)') != 1):
        raise ValueError("hierarchy_capture_preservation")
    return text.encode("utf8")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base-helper", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    a=p.parse_args()
    if a.base_helper.is_symlink() or a.destination.is_symlink() or a.destination.exists() or a.destination.parent.is_symlink():
        raise ValueError("private_stage_path")
    raw=render(a.base_helper.read_bytes())
    with a.destination.open("xb") as out:
        out.write(raw)
    print("GT_LIGHT_HIERARCHY_STAGED_SHA256="+hashlib.sha256(raw).hexdigest())
