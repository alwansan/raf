#!/usr/bin/env python3
"""B02: stage an OPTIONAL Texture2D28 lineage capture in disposable exporter code.

The shared W1 RaftExportLineage.cs and ProjectExporter.cs are NEVER modified.
Input must match its exact reviewed Git blob. A fresh private trace shares the
same export_instance with the original W1 Material21/Shader48 trace if both
environment variables are set. Nothing captures game bytes or prints IDs.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

HELPER_BLOB_SHA1 = "4b84a325bb1766583adb4ba6cfd9a23225f23bb9"
PATH_ANCHOR = '        string? path = Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LINEAGE");'
RETURN_ANCHOR = "        if (string.IsNullOrEmpty(path))\n            return;"
GUID_ANCHOR = '        json.WriteString("export_instance", Guid.NewGuid().ToString("N"));'
METHOD_ANCHOR = "    private static void Identity(Utf8JsonWriter json, string key, IUnityObjectBase asset)"
# Reviewed W1 source revision adds optional Texture2DArray/tiled image
# source capture only under its explicit "1" opt-in; B02 uses a private path
# value rather than "1", preserving original 21/48 capture and adding its
# own read-only 28-only second trace. This filter is verified with blob SHA.
REVIEWED_SHADER_FILTER = """                if (asset.ClassID is not (21 or 48) &&
                    !(includeTextureObjects &&
                      asset.ClassID is (28 or 84 or 89 or 117 or 187)))"""


OPTIONAL_TRACE = """    private static void CaptureTextureObjects(
        ProjectAssetContainer container,
        IReadOnlyList<IExportCollection> collections,
        string path, string exportInstance)
    {
        // This file stays under runner private temp. Never upload it.
        using FileStream output = new(path, FileMode.CreateNew, FileAccess.Write);
        using Utf8JsonWriter json = new(output);
        json.WriteStartObject();
        json.WriteNumber("schema_version", 1);
        json.WriteString("export_instance", exportInstance);
        json.WriteStartArray("objects");
        var seen = new HashSet<(string Owner, long PathId)>();
        int nonExportable = 0;
        foreach (IExportCollection collection in collections)
        {
            container.CurrentCollection = collection;
            foreach (IUnityObjectBase asset in collection.Assets)
            {
                if (asset.ClassID != 28) // Exact Unity Texture2D class, no inference.
                    continue;
                if (!collection.Exportable)
                {
                    nonExportable++;
                    continue;
                }
                if (!seen.Add((asset.Collection.Name, asset.PathID)))
                    throw new InvalidOperationException("Ambiguous Texture2D source identity in export");
                json.WriteStartObject();
                json.WriteNumber("class_id", 28);
                Identity(json, "source", asset);
                Pointer(json, "export", collection.CreateExportPointer(container, asset, false));
                json.WriteEndObject();
            }
        }
        json.WriteEndArray();
        json.WriteNumber("nonexportable_texture_objects_skipped", nonExportable);
        json.WriteEndObject();
        json.Flush();
    }

"""


def git_blob_sha1(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def render(base: bytes) -> bytes:
    if git_blob_sha1(base) != HELPER_BLOB_SHA1:
        raise ValueError("untrusted W1 helper Git blob; refuse stale instrumenter patch")
    source = base.decode("utf-8-sig")
    for anchor in (PATH_ANCHOR, RETURN_ANCHOR, GUID_ANCHOR, METHOD_ANCHOR):
        if source.count(anchor) != 1:
            raise ValueError("ambiguous original exporter capture anchor")

    source = source.replace(PATH_ANCHOR, PATH_ANCHOR + '\n'
        + '        string? texturePath = Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE");')
    source = source.replace(RETURN_ANCHOR,
        '        if (string.IsNullOrEmpty(path) && string.IsNullOrEmpty(texturePath))\n'
        '            return;\n'
        '        string exportInstance = Guid.NewGuid().ToString("N");\n'
        '        if (!string.IsNullOrEmpty(texturePath))\n'
        '            CaptureTextureObjects(container, collections, texturePath, exportInstance);\n'
        '        if (string.IsNullOrEmpty(path))\n'
        '            return;')
    source = source.replace(GUID_ANCHOR, '        json.WriteString("export_instance", exportInstance);')
    source = source.replace(METHOD_ANCHOR, OPTIONAL_TRACE + METHOD_ANCHOR)
    if (source.count("CaptureTextureObjects(") != 2
            or source.count('json.WriteString("export_instance", exportInstance);') != 2
            or source.count(REVIEWED_SHADER_FILTER) != 1
            or source.count('Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE") == "1"') != 1):
        raise ValueError("unsafe W1+Texture2D capture composition")
    return source.encode("utf-8")


def stage(source: Path, destination: Path) -> dict:
    if source.is_symlink() or not source.is_file():
        raise ValueError("source helper missing or symlinked")
    if destination.is_symlink() or destination.exists():
        raise ValueError("destination exists or is linked")
    if not destination.parent.is_dir() or destination.parent.is_symlink():
        raise ValueError("destination staging parent absent/linked")
    if source.resolve() == destination.resolve():
        raise ValueError("cannot overwrite shared helper")
    original = source.read_bytes()
    staged = render(original)
    try:
        with destination.open("xb") as out:
            out.write(staged)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return {
        "source_git_blob_verified": True,
        "staged_helper_sha256": hashlib.sha256(staged).hexdigest(),
        "optional_texture_class_id": 28,
        "shared_w1_material_shader_filter_preserved": True,
        "same_export_instance_for_two_private_traces": True,
        "modified_shared_source": False,
        "texture_pixels_or_android_verified": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-helper", type=Path, required=True)
    ap.add_argument("--destination", type=Path, required=True)
    args = ap.parse_args()
    report = stage(args.base_helper, args.destination)
    # Never emit raw original texture identifiers or per-object export GUIDs.
    print("RAFT_B02_TEXTURE_LINEAGE_STAGE " + str(report))


if __name__ == "__main__":
    main()
