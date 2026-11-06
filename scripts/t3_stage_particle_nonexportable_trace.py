#!/usr/bin/env python3
"""T3 private B02 class28 non-exportable source classification instrumenter.

Only touches a SHA-authenticated *disposable* W1+B02+B21 helper copied into
GitHub runner temp, not the repository's shared exporter/AssetRipper, and
does not change export behavior. It appends private, unuploaded original
Texture2D source owner/pathID records for collection.Exportable == false.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from scripts import b21_stage_light_lineage as b21

TEXTURE_METHOD="    private static void CaptureTextureObjects("
LIGHT_METHOD="    private static void CaptureLightObjects("
SOURCE_ANCHOR="        int nonExportable = 0;\n"
SKIP_ANCHOR="""                if (!collection.Exportable)
                {
                    nonExportable++;
                    continue;
                }
"""
END_ANCHOR="""        json.WriteEndArray();
        json.WriteNumber("nonexportable_texture_objects_skipped", nonExportable);
"""

def annotate(source:bytes)->bytes:
    if not isinstance(source,bytes):
        raise ValueError("invalid_disposable_exporter_source_type")
    text=source.decode("utf8")
    if (text.count(TEXTURE_METHOD)!=1
        or text.count(LIGHT_METHOD)!=1):
        raise ValueError("missing_expected_B02_B21_optional_helper_methods")
    before,tail=text.split(TEXTURE_METHOD)
    body,after=tail.split(LIGHT_METHOD)
    for a in (SOURCE_ANCHOR,SKIP_ANCHOR,END_ANCHOR):
        if body.count(a)!=1:
            raise ValueError("disposable_B02_trace_source_anchor_drift")
    body=body.replace(SOURCE_ANCHOR,
        SOURCE_ANCHOR+"        var nonExportableSourceObjects = new List<IUnityObjectBase>();\n")
    body=body.replace(SKIP_ANCHOR,SKIP_ANCHOR.replace(
        "                    nonExportable++;\n",
        "                    nonExportable++;\n                    nonExportableSourceObjects.Add(asset);\n"))
    body=body.replace(END_ANCHOR, """        json.WriteEndArray();
        // Private ONLY: never upload this source identity array.
        json.WriteStartArray("nonexportable_texture_sources");
        foreach (IUnityObjectBase asset in nonExportableSourceObjects)
        {
            json.WriteStartObject();
            Identity(json, "source", asset);
            // A private, read-only diagnostic of the exact pointer AssetRipper
            // resolves through the same instance's container. DO NOT force
            // collection.Exportable=true or export any missing source texture.
            try
            {
                Pointer(json, "container_export", container.CreateExportPointer(asset));
                json.WriteBoolean("container_export_pointer_captured", true);
            }
            catch (Exception)
            {
                // Never serialize private AssetRipper exception text.
                json.WriteNull("container_export");
                json.WriteBoolean("container_export_pointer_captured", false);
            }
            json.WriteEndObject();
        }
        json.WriteEndArray();
        json.WriteNumber("nonexportable_texture_objects_skipped", nonExportable);
""")
    result=(before+TEXTURE_METHOD+body+LIGHT_METHOD+after).encode("utf8")
    if (result.count(b'nonexportable_texture_sources')!=1
        or result.count(b'nonExportableSourceObjects')!=3
        or result.count(b'container.CreateExportPointer(asset)')!=1
        or result.count(b'container_export_pointer_captured')!=2
        or result.count(b'json.WriteString("export_instance", exportInstance);')!=3
        or result.count(b'if (asset.ClassID is not (21 or 48))')!=1):
        raise ValueError("unsafe_original_B02_nonexportable_trace_instrumentation")
    return result


def stage(base:Path,staged:Path):
    if (base.is_symlink() or not base.is_file()
        or staged.is_symlink() or not staged.is_file()
        or staged.resolve()==base.resolve()
        or staged.parent.resolve()==base.parent.resolve()):
        raise ValueError("non_disposable_or_missing_optional_B02_helper")
    expected=b21.render(base.read_bytes())  # W1 source + B02/B21 exact SHA pins.
    actual=staged.read_bytes()
    if actual!=expected:
        raise ValueError("disposable_helper_drifted_from_pinned_B21_composition")
    changed=annotate(actual)
    staged.write_bytes(changed)
    return {"schema_version":1,"status":"T3_PRIVATE_B02_NONEXPORTABLE_SOURCE_CATEGORIES_STAGED",
        "original_W1_B02_B21_source_authentic":True,
        "only_disposable_helper_modified":True,
        "private_source_IDs_published":False,
        "exporter_selection_or_asset_import_behavior_changed":False,
        "annotated_helper_sha256":hashlib.sha256(changed).hexdigest()}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-helper",type=Path,required=True)
    ap.add_argument("--staged-helper",type=Path,required=True)
    args=ap.parse_args(argv)
    report=stage(args.base_helper,args.staged_helper)
    # Source-only synthetic helper digest is not proprietary; no paths/IDs.
    print("RAFT_T3_DISPOSABLE_B02_NONEXPORTABLE_SOURCE_AUDIT "+
          "staged=true exact_w1_b02_b21=true game_assets_modified=false")

if __name__=="__main__":
    main()
