"""Instrument the pinned exporter and preserve unsigned YAML list bits.

Only the disposable public tool checkout is patched. Original game inputs and
exported assets are untouched. The trace is private and must never be uploaded.
"""
import argparse
import hashlib
from pathlib import Path
from scripts import b02_stage_texture_lineage as w1

PIN = '3f2400364e25332361f53737446ee69a534ca1e8fc9bae072d580fac1c617ed6'
YAML_HEX_PIN = 'bf380b726b0e25ca3489936aafce7b387ff0eb6932d9b45cec6a3ff320eff857'
YAML_HEX_PATH = 'Source/AssetRipper.Yaml/Extensions/ReverseHexString.cs'
ANCHOR = '\t\tProjectAssetContainer container = new ProjectAssetContainer(this, options, fileCollection.FetchAssets(), collections);'


MESH_CAPTURE = """    private static void CaptureMeshes(ProjectAssetContainer container,
        IReadOnlyList<IExportCollection> collections, string path, string instance)
    {
        using FileStream output = new(path, FileMode.CreateNew, FileAccess.Write);
        using Utf8JsonWriter json = new(output);
        json.WriteStartObject();
        json.WriteNumber("schema_version", 1);
        json.WriteString("export_instance", instance);
        json.WriteStartArray("meshes");
        foreach (IExportCollection collection in collections)
        {
            container.CurrentCollection = collection;
            foreach (IUnityObjectBase asset in collection.Assets)
            {
                if (asset.ClassID != 43)
                    continue;
                json.WriteStartObject();
                Identity(json, "source", asset);
                json.WriteBoolean("exportable", collection.Exportable);
                Pointer(json, "export", collection.CreateExportPointer(container, asset, false));
                json.WriteEndObject();
            }
        }
        json.WriteEndArray();
        json.WriteEndObject();
    }

"""


def add_mesh_lineage(raw):
    if w1.git_blob_sha1(raw) != w1.HELPER_BLOB_SHA1:
        raise ValueError('Pinned W1 helper changed; refusing Mesh trace composition')
    source = raw.decode('utf-8')
    for anchor in (w1.RETURN_ANCHOR, w1.GUID_ANCHOR, w1.METHOD_ANCHOR):
        if source.count(anchor) != 1:
            raise ValueError('Exporter Mesh trace hook is ambiguous')
    source = source.replace(w1.RETURN_ANCHOR, w1.RETURN_ANCHOR + """
        string instance = Guid.NewGuid().ToString("N");
        string? meshPath = Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_MESH_LINEAGE");
        if (!string.IsNullOrEmpty(meshPath))
            CaptureMeshes(container, collections, meshPath, instance);
""")
    source = source.replace(w1.GUID_ANCHOR, '        json.WriteString("export_instance", instance);')
    return source.replace(w1.METHOD_ANCHOR, MESH_CAPTURE + w1.METHOD_ANCHOR).encode('utf-8')


def repair_yaml_hex(raw):
    if hashlib.sha256(raw).hexdigest() != YAML_HEX_PIN:
        raise ValueError('Pinned YAML hex writer changed')
    # An arithmetic right shift sign-extends a high-bit value into a negative
    # nibble. Mask it just like the other nibbles to retain its four bits.
    return raw.replace(
        b'NybbleToLowercaseHexCharacter(x >> 28);',
        b'NybbleToLowercaseHexCharacter((x >> 28) & 0x0F);',
    ).replace(
        b'NybbleToLowercaseHexCharacter(x >> 60);',
        b'NybbleToLowercaseHexCharacter((x >> 60) & 0x0F);',
    )


def add_compute_lineage(raw):
    source = raw.decode('utf-8')
    anchor = '        foreach (IExportCollection collection in collections)'
    condition = 'asset.ClassID is not (21 or 48) &&'
    if source.count(condition) != 1:
        raise ValueError('Exporter ComputeShader trace hook is ambiguous')
    index = source.index(anchor)
    source = source[:index] + '''        bool includeComputeObjects = Environment.GetEnvironmentVariable(
            "RAFT_PRIVATE_EXPORT_COMPUTE_LINEAGE") == "1";
''' + source[index:]
    return source.replace(condition, condition + '''
                    !(includeComputeObjects && asset.ClassID == 72) &&''').encode('utf-8')


def patch(root, helper, *, mesh_lineage=False, native_texture_arrays=False, compute_lineage=False):
    directory = root / 'Source/AssetRipper.Export.UnityProjects'
    target = directory / 'ProjectExporter.cs'
    raw = target.read_bytes()
    yaml_target = root / YAML_HEX_PATH
    yaml_raw = yaml_target.read_bytes()
    yaml_fixed = repair_yaml_hex(yaml_raw)
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Pinned exporter source changed; refusing instrumentation')
    source = raw.decode('utf-8')
    if source.count(ANCHOR) != 1:
        raise ValueError('Exporter container hook is ambiguous')
    overrides = directory / 'ProjectExporter.Overrides.cs'
    if native_texture_arrays:
        override_raw = overrides.read_bytes()
        override_source = override_raw.decode('utf-8')
        registration = 'OverrideExporter<ITexture2DArray>(textureArrayExporter);'
        if override_source.count(registration) != 1:
            raise ValueError('Pinned Texture2DArray registration is ambiguous')
        override_source = override_source.replace(
            registration, 'OverrideExporter<ITexture2DArray>(streamedAssetExporter);')
    destination = directory / 'RaftExportLineage.cs'
    if destination.exists():
        raise FileExistsError('Trace source already exists')
    helper_raw = helper.read_bytes()
    if mesh_lineage:
        helper_raw = add_mesh_lineage(helper_raw)
    if compute_lineage:
        helper_raw = add_compute_lineage(helper_raw)
    destination.write_bytes(helper_raw)
    try:
        if native_texture_arrays:
            overrides.write_bytes(override_source.encode('utf-8'))
        yaml_target.write_bytes(yaml_fixed)
        target.write_bytes(source.replace(ANCHOR, ANCHOR + '\n\t\tRaftExportLineage.Capture(container, collections);').encode('utf-8'))
    except BaseException:
        if native_texture_arrays:
            overrides.write_bytes(override_raw)
        yaml_target.write_bytes(yaml_raw)
        target.write_bytes(raw)
        destination.unlink()
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-source', type=Path, required=True)
    p.add_argument('--helper', type=Path, required=True)
    p.add_argument('--mesh-lineage', action='store_true')
    p.add_argument('--native-texture-arrays', action='store_true')
    p.add_argument('--compute-lineage', action='store_true')
    a = p.parse_args()
    patch(a.tool_source, a.helper, mesh_lineage=a.mesh_lineage,
          native_texture_arrays=a.native_texture_arrays, compute_lineage=a.compute_lineage)
