// Public tool packages only. Engine dataset stays private; publish counts/hashes.
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using AssetRipper.Primitives;
using AssetRipper.SourceGenerated;
using AssetRipper.Tpk;
using AssetRipper.Tpk.EngineAssets;
using AssetRipper.Mining.PredefinedAssets;

static bool CopiesParsedName(MethodInfo method)
{
    byte[] bytes = method.GetMethodBody()?.GetILAsByteArray() ?? [];
    if (bytes.Length < 18) return false;
    ReadOnlySpan<byte> tail = bytes.AsSpan(bytes.Length - 18);
    if (tail[0] != 0x02 || tail[1] != 0x02 || tail[2] != 0x7b ||
        tail[7] != 0x7b || tail[12] != 0x7d || tail[17] != 0x2a) return false;
    return method.Module.ResolveField(BitConverter.ToInt32(tail.Slice(3, 4)))?.Name == "m_ParsedForm"
        && method.Module.ResolveField(BitConverter.ToInt32(tail.Slice(8, 4)))?.Name == "m_Name"
        && method.Module.ResolveField(BitConverter.ToInt32(tail.Slice(13, 4)))?.Name == "m_Name";
}

if (args.Length != 2) throw new ArgumentException("Private dataset and summary destinations required");
var version = UnityVersion.Parse("2021.3.45f2");
var generated = typeof(AssetFactory).Assembly;
// Select the actual generated Unity2021.3.45f2 type through its public factory.
Type factory = generated.GetType("AssetRipper.SourceGenerated.Classes.ClassID_48.Shader")
    ?? throw new InvalidOperationException("Pinned shader factory missing");
MethodInfo create = factory.GetMethods(BindingFlags.Public | BindingFlags.Static)
    .Single(m => m.Name == "Create" && m.GetParameters().Any(p => p.ParameterType == typeof(UnityVersion)));
object?[] parameters = create.GetParameters().Select(p => p.ParameterType == typeof(UnityVersion)
    ? (object)version : p.ParameterType.IsValueType ? Activator.CreateInstance(p.ParameterType) : null).ToArray();
object instance = create.Invoke(null, parameters) ?? throw new InvalidOperationException("Pinned shader type not selected");
Type selectedType = instance.GetType();
MethodInfo release = selectedType.GetMethod("ReadRelease") ?? throw new InvalidOperationException("ReadRelease missing");
MethodInfo editor = selectedType.GetMethod("ReadEditor") ?? throw new InvalidOperationException("ReadEditor missing");
bool releaseCopy = CopiesParsedName(release), editorCopy = CopiesParsedName(editor);
if (!releaseCopy || !editorCopy) throw new InvalidOperationException("Exact generated name-copy contract not verified");

Type tpkType = generated.GetTypes().Single(t => t.Name == "EngineAssetsTpk");
using var input = (Stream)(tpkType.GetMethod("GetStream", BindingFlags.Static | BindingFlags.Public)
    ?.Invoke(null, null) ?? throw new InvalidOperationException("Embedded engine data stream missing"));
using var raw = new MemoryStream();
input.CopyTo(raw);
byte[] tpkBytes = raw.ToArray();
using var tpkInput = new MemoryStream(tpkBytes);
var blob = (TpkEngineAssetsBlob)TpkFile.FromStream(tpkInput).GetDataBlob();
if (blob.Data.Count == 0) throw new InvalidOperationException("Empty exact engine dataset");
int index = 0;
if (version > blob.Data[0].Key)
{
    index = blob.Data.Count - 1;
    for (int i = 1; i < blob.Data.Count; i++)
        if (version <= blob.Data[i].Key) { index = i - 1; break; }
}
string json = blob.Data[index].Value;
var data = EngineResourceData.FromJson(json);
var records = new List<object>();
int defaultShaders = 0, extraShaders = 0;
void Add(Dictionary<long, AssetRipper.Mining.PredefinedAssets.Object> entries, string kind)
{
    foreach (var pair in entries)
        if (pair.Value is AssetRipper.Mining.PredefinedAssets.Shader shader)
        {
            records.Add(new { name = shader.Name, properties = shader.PropertyNames,
                file_id = pair.Key, engine_kind = kind });
            if (kind == "default") defaultShaders++; else extraShaders++;
        }
}
Add(data.DefaultResources, "default");
Add(data.ExtraResources, "extra");
// Never upload this file or print original names/IDs.
File.WriteAllText(args[0], JsonSerializer.Serialize(records));
var summary = new {
    sourcegenerated_version = generated.GetName().Version?.ToString(),
    generated_assembly_sha256 = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(generated.Location))).ToLowerInvariant(),
    selected_shader_type = selectedType.FullName,
    selected_unity_version = version.ToString(), release_name_copy_verified = releaseCopy,
    editor_name_copy_verified = editorCopy, engine_dataset_version = blob.Data[index].Key.ToString(),
    tpk_sha256 = Convert.ToHexString(SHA256.HashData(tpkBytes)).ToLowerInvariant(),
    dataset_json_sha256 = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(json))).ToLowerInvariant(),
    default_shader_records = defaultShaders, extra_shader_records = extraShaders,
    actual_export_material_refs_verified = false, unity_or_android_executed = false
};
string result = JsonSerializer.Serialize(summary);
File.WriteAllText(args[1], result + "\n");
Console.WriteLine("RAFT_W1_EXACT_ENGINE_DATABASE " + result);
