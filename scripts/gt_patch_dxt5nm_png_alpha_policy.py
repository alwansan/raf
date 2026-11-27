"""Opt-in V15 candidate on the exact pinned public TextureExportCollection.

V14 proved alphaIsTransparency dilates normal XY at zero alpha for authored
DXT5nm PNGs. Change only the converted PNG collection's final NormalMap
importer, after sprite processing; default off. No general importer or
production activation, no source bytes, no Android or lower-mip parity.
"""
import argparse
import hashlib
import json
from pathlib import Path

PIN="a5032c7cbf94ea096ded9bddf99976461612f90b"
PATH="Source/AssetRipper.Export.UnityProjects/Textures/TextureExportCollection.cs"
ENV="RAFT_GT_DXT5NM_PNG_ALPHA_POLICY"
ANCHOR=b"""\t\t\tAddSprites(container, importer, ((SpriteInformationObject?)Asset.MainAsset)!.Sprites);
\t\t\treturn importer;"""
REPLACEMENT=b"""\t\t\tAddSprites(container, importer, ((SpriteInformationObject?)Asset.MainAsset)!.Sprites);
\t\t\t// GT V14 authored evidence: alpha dilation corrupts packed normal XY.
\t\t\t// Opt in only for the tested converted PNG, non-sprite DXT5nm shape.
\t\t\tif (System.Environment.GetEnvironmentVariable("RAFT_GT_DXT5NM_PNG_ALPHA_POLICY") == "1"
\t\t\t\t&& ((TextureAssetExporter)AssetExporter).ImageExportFormat == ImageExportFormat.Png
\t\t\t\t&& texture.ClassID == 28 && texture.ImageCount_C28 == 1
\t\t\t\t&& texture.Format_C28E == TextureFormat.DXT5
\t\t\t\t&& texture.LightmapFormat_C28E == TextureUsageMode.NormalmapDXT5nm
\t\t\t\t&& texture.ColorSpace_C28E == ColorSpace.Gamma
\t\t\t\t&& importer.TextureTypeE == TextureImporterType.NormalMap
\t\t\t\t&& importer.TextureShapeE == TextureImporterShape.Texture2D
\t\t\t\t&& ((SpriteInformationObject?)Asset.MainAsset)!.Sprites.Count == 0)
\t\t\t{
\t\t\t\timporter.AlphaIsTransparency = 0;
\t\t\t}
\t\t\treturn importer;"""

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def repair(raw):
    if git_blob(raw)!=PIN:
        raise ValueError("pinned_TextureExportCollection_changed")
    if raw.count(ANCHOR)!=1:
        raise ValueError("ambiguous_DXT5nm_alpha_patch_anchor")
    fixed=raw.replace(ANCHOR,REPLACEMENT)
    if fixed.count(REPLACEMENT)!=1 or fixed.replace(REPLACEMENT,ANCHOR)!=raw:
        raise ValueError("non_candidate_source_bytes_changed")
    return fixed

def patch(root):
    p=root/PATH
    raw=p.read_bytes()
    fixed=repair(raw)
    p.write_bytes(fixed)
    return dict(status="PATCHED_PINNED_CONVERTED_DXT5NM_PNG_ALPHA_POLICY_OPT_IN",
        original_git_blob=git_blob(raw),original_sha256=hashlib.sha256(raw).hexdigest(),
        patched_sha256=hashlib.sha256(fixed).hexdigest(),patch_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        opt_in_environment=ENV,opt_in_value="1",default_behavior_changed=False,source_asset_bytes_modified=False,
        general_importer_factory_changed=False,production_activation=False)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tool-source",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(patch(a.tool_source),sort_keys=True))
