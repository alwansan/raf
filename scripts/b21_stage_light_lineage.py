#!/usr/bin/env python3
"""B21 optional native class108 Light lineage for the same disposable AssetRipper export.

Derives exact SHA-locked B02 Texture2D + original W1 Material/Shader helper
in memory. Never mutates another agent's helper, an original game asset, or the
production exporter. The private trace contains identifiers: NEVER upload it.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from scripts import b02_stage_texture_lineage as texture_stage

# SHA256 of b02_stage_texture_lineage.render(exact_W1_helper), independently
# recorded after successful B02 CI41927712988. New B02 edits require review.
B02_RENDER_SHA256 = "c99c6e163ee20d9ff72e2180ed72ce94b5c608e20dc1095c3c81d3e678532c1e"
TEXTURE_PATH = '        string? texturePath = Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE");'
EARLY_RETURN = '        if (string.IsNullOrEmpty(path) && string.IsNullOrEmpty(texturePath))'
EXPORT_INSTANCE = '        string exportInstance = Guid.NewGuid().ToString("N");'
METHOD_ANCHOR = "    private static void Identity(Utf8JsonWriter json, string key, IUnityObjectBase asset)"

LIGHT_CAPTURE = """    private static void CaptureLightObjects(
        ProjectAssetContainer container,
        IReadOnlyList<IExportCollection> collections,
        string path, string exportInstance)
    {
        // Identifiers are private source->export pointers, not public artifacts.
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
                if (asset.ClassID != 108) // Unity native Light; no name guess.
                    continue;
                if (!seen.Add((asset.Collection.Name, asset.PathID)))
                    throw new InvalidOperationException("Ambiguous Light source identity in export");
                if (!collection.Exportable)
                {
                    nonExportable++;
                    continue;
                }
                json.WriteStartObject();
                json.WriteNumber("class_id", 108);
                Identity(json, "source", asset);
                json.WriteString("collection_type", collection.GetType().FullName);
                Pointer(json, "export", collection.CreateExportPointer(container, asset, false));
                json.WriteEndObject();
            }
        }
        json.WriteEndArray();
        json.WriteNumber("nonexportable_light_objects_skipped", nonExportable);
        json.WriteEndObject();
        json.Flush();
    }

"""


def render(base: bytes) -> bytes:
    """Fail closed on wrong W1/B02 revisions or ambiguous C# syntax anchors."""
    original = texture_stage.render(base)  # pinned original W1 by Git blob SHA
    if hashlib.sha256(original).hexdigest() != B02_RENDER_SHA256:
        raise ValueError("Unreviewed B02 helper composition")
    text = original.decode("utf-8")
    for anchor in (TEXTURE_PATH, EARLY_RETURN, EXPORT_INSTANCE, METHOD_ANCHOR):
        if text.count(anchor) != 1:
            raise ValueError("Ambiguous Light capture anchor")
    text = text.replace(TEXTURE_PATH, TEXTURE_PATH + '\n'
                        + '        string? lightPath = Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE");')
    text = text.replace(EARLY_RETURN, '        if (string.IsNullOrEmpty(path) && string.IsNullOrEmpty(texturePath) && string.IsNullOrEmpty(lightPath))')
    text = text.replace(EXPORT_INSTANCE, EXPORT_INSTANCE
                        + '\n        if (!string.IsNullOrEmpty(lightPath))'
                        + '\n            CaptureLightObjects(container, collections, lightPath, exportInstance);')
    text = text.replace(METHOD_ANCHOR, LIGHT_CAPTURE + METHOD_ANCHOR)
    if (text.count('if (asset.ClassID is not (21 or 48))') != 1
        or text.count('if (asset.ClassID != 28)') != 1
        or text.count('if (asset.ClassID != 108)') != 1
        or text.count('CaptureLightObjects(') != 2
        or text.count('json.WriteString("export_instance", exportInstance);') != 3
        or text.count('FileMode.CreateNew') != 3):
        raise ValueError("Unsafe optional Light/Texture/W1 capture composition")
    return text.encode("utf-8")


def stage(source: Path, destination: Path) -> dict:
    if source.is_symlink() or not source.is_file():
        raise ValueError("Untrusted W1 helper path")
    if destination.is_symlink() or destination.exists() or not destination.parent.is_dir() or destination.parent.is_symlink():
        raise ValueError("Unsafe or occupied private staging destination")
    if source.resolve() == destination.resolve():
        raise ValueError("Refusing to overwrite W1 helper")
    raw = source.read_bytes()
    staged = render(raw)
    with destination.open("xb") as output:
        output.write(staged)
    return {
        "original_w1_helper_sha1_verified": texture_stage.git_blob_sha1(raw) == texture_stage.HELPER_BLOB_SHA1,
        "b02_composed_helper_sha256_verified": True,
        "b21_composed_sha256": hashlib.sha256(staged).hexdigest(),
        "native_light_class_id": 108,
        "same_export_instance_with_w1_and_b02": True,
        "shared_helpers_modified": False,
        "actual_raft_light_export_captured": False,
        "unity_or_adreno_light_pixels_verified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--base-helper", required=True, type=Path)
    p.add_argument("--destination", required=True, type=Path)
    a = p.parse_args()
    report = stage(a.base_helper, a.destination)
    # Only aggregate source-free facts, never game object identifiers or GUIDs.
    print("RAFT_B21_STAGED_PRIVATE_LIGHT_TRACE " + str(report))


if __name__ == "__main__":
    main()
