#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace RaftAndroid.Editor
{
    // Resolve real provider MonoScripts first. Never delete original script assets
    // or write a partial set of asset changes when a used SDK identity is unresolved.
    public static class SdkScriptBindingResolver
    {
        [Serializable] private sealed class Statistics { public int sdk_references; }
        [Serializable] private sealed class Manifest { public Identity[] scripts; public Statistics statistics; public OriginalOrphan[] preservedOriginalOrphans; }
        [Serializable] private sealed class OriginalOrphan { public string sourceGuid; public string usagePath; public string originalFile; public long originalScriptPathId; public long originalObjectPathId; }
        [Serializable] private sealed class Identity
        {
            public string sourceGuid;
            public string assemblyName;
            public string fullTypeName;
            public string simpleTypeName;
            public string sourcePath;
            public int references;
        }
        private sealed class Candidate
        {
            public string Assembly;
            public string FullName;
            public string SimpleName;
            public string Guid;
            public long FileId;
        }
        private sealed class Edit { public string Path; public string Text; }

        public static void Rebind(string manifestPath)
        {
            if (!File.Exists(manifestPath))
                throw new BuildFailedException("SDK source identity manifest is missing.");
            Manifest manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            if (manifest == null || manifest.scripts == null || manifest.scripts.Length == 0)
                throw new BuildFailedException("SDK source identity manifest is empty.");

            var identities = new Dictionary<string, Identity>(StringComparer.OrdinalIgnoreCase);
            foreach (Identity row in manifest.scripts)
            {
                if (row == null || !Regex.IsMatch(row.sourceGuid ?? "", @"\A[0-9a-fA-F]{32}\z") ||
                    string.IsNullOrEmpty(row.assemblyName))
                    throw new BuildFailedException("Invalid source SDK identity.");
                identities.Add(row.sourceGuid, row);
            }
            var originalOrphans = new Dictionary<string, OriginalOrphan>(StringComparer.OrdinalIgnoreCase);
            foreach (OriginalOrphan orphan in manifest.preservedOriginalOrphans ?? new OriginalOrphan[0])
            {
                Identity row;
                if (orphan == null || !identities.TryGetValue(orphan.sourceGuid ?? "", out row) ||
                    row.assemblyName != "Sirenix.Serialization.Config" || row.references != 1 ||
                    (row.fullTypeName != "GlobalSerializationConfig" &&
                     row.fullTypeName != "Sirenix.Serialization.GlobalSerializationConfig") ||
                    System.IO.Path.GetFileName(orphan.usagePath ?? "") != "GlobalSerializationConfig.asset" ||
                    orphan.originalFile != "resources.assets" || orphan.originalScriptPathId != 934 ||
                    orphan.originalObjectPathId != 6381 ||
                    File.Exists(System.IO.Path.Combine(Application.dataPath,
                        "Plugins/RaftManagedReferences/Sirenix.Serialization.Config.dll")))
                    throw new BuildFailedException("Invalid pre-existing original unresolved configuration record.");
                originalOrphans.Add(orphan.sourceGuid, orphan);
            }
            int preservedOrphanReferences = 0;
            var wanted = new HashSet<string>(manifest.scripts.Select(r => r.assemblyName), StringComparer.Ordinal);
            var candidates = new List<Candidate>();
            var unique = new HashSet<string>(StringComparer.Ordinal);
            foreach (string path in AssetDatabase.GetAllAssetPaths())
            {
                if (path.StartsWith("Packages/", StringComparison.Ordinal) &&
                    path.EndsWith(".cs", StringComparison.OrdinalIgnoreCase))
                {
                    Register(AssetDatabase.LoadAssetAtPath<MonoScript>(path), wanted, unique, candidates);
                }
                else if (path.StartsWith("Assets/Plugins/RaftManagedReferences/", StringComparison.Ordinal) &&
                         path.EndsWith(".dll", StringComparison.OrdinalIgnoreCase))
                {
                    foreach (UnityEngine.Object asset in AssetDatabase.LoadAllAssetsAtPath(path))
                        Register(asset as MonoScript, wanted, unique, candidates);
                }
            }

            var targets = new Dictionary<string, ScriptBindingTarget>(StringComparer.OrdinalIgnoreCase);
            int namespaceFallbacks = 0;
            foreach (Identity row in manifest.scripts)
            {
                List<Candidate> matches = candidates.Where(c => c.Assembly == row.assemblyName &&
                    c.FullName == row.fullTypeName).ToList();
                // Only an unqualified exported type can use a unique simple-name
                // match within the exact original provider assembly.
                if (matches.Count == 0 && !string.IsNullOrEmpty(row.simpleTypeName) &&
                    row.fullTypeName == row.simpleTypeName)
                {
                    matches = candidates.Where(c => c.Assembly == row.assemblyName &&
                        c.SimpleName == row.simpleTypeName).ToList();
                    if (matches.Count == 1) namespaceFallbacks++;
                }
                if (matches.Count == 1)
                    targets.Add(row.sourceGuid, new ScriptBindingTarget(matches[0].Guid, matches[0].FileId));
            }

            if (manifest.statistics == null)
                throw new BuildFailedException("SDK manifest reference accounting is missing.");
            string beforeMetaHash = ScriptMetaHash();
            var edits = new List<Edit>();
            var missing = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            int refs = 0, changes = 0;
            foreach (string path in Directory.GetFiles(Application.dataPath, "*", SearchOption.AllDirectories))
            {
                string extension = System.IO.Path.GetExtension(path);
                if (extension != ".unity" && extension != ".prefab" && extension != ".asset") continue;
                string text = File.ReadAllText(path);
                if (!text.TrimStart('\ufeff').StartsWith("%YAML", StringComparison.Ordinal))
                {
                    string assetPath = "Assets/" + path.Substring(Application.dataPath.Length + 1)
                        .Replace(System.IO.Path.DirectorySeparatorChar, '/');
                    foreach (string dependency in AssetDatabase.GetDependencies(assetPath, false))
                        if (identities.ContainsKey(AssetDatabase.AssetPathToGUID(dependency)))
                            throw new BuildFailedException("Binary asset has an unresolved SDK source dependency: " + assetPath);
                    continue;
                }
                ScriptBindingRewrite result = SdkScriptBindingCore.Rewrite(text, identities.Keys, targets);
                refs += result.SourceReferences;
                changes += result.Changes;
                foreach (string guid in result.MissingTargets)
                {
                    OriginalOrphan orphan;
                    if (!originalOrphans.TryGetValue(guid, out orphan)) { missing.Add(guid); continue; }
                    string relative = path.Substring(Application.dataPath.Length + 1)
                        .Replace(System.IO.Path.DirectorySeparatorChar, '/');
                    if (relative != orphan.usagePath)
                        throw new BuildFailedException("Original unresolved configuration appeared at an unexpected path.");
                    preservedOrphanReferences += Regex.Matches(text,
                        @"(?m)^[ \t]*m_Script:[ \t]*\{[^}\r\n]*\bguid:[ \t]*" + Regex.Escape(guid),
                        RegexOptions.IgnoreCase).Count;
                }
                if (result.Changes != 0) edits.Add(new Edit {Path = path, Text = result.Text});
            }
            if (preservedOrphanReferences != originalOrphans.Count)
                throw new BuildFailedException("Original unresolved configuration reference accounting changed.");
            if (refs != manifest.statistics.sdk_references)
                throw new BuildFailedException("SDK source reference count changed since identity audit; no changes written.");
            if (missing.Count != 0)
            {
                foreach (string guid in missing.OrderBy(g => g, StringComparer.Ordinal).Take(30))
                {
                    Identity row = identities[guid];
                    Debug.LogError("RAFT_SDK_BINDING_UNRESOLVED assembly=" + row.assemblyName +
                                   " type=" + row.fullTypeName + " source=" + row.sourcePath);
                }
                throw new BuildFailedException("Used SDK source identities unresolved: " + missing.Count +
                                               ". No serialized binding changes were written.");
            }
            foreach (OriginalOrphan orphan in originalOrphans.Values)
                Debug.LogWarning("RAFT_ORIGINAL_UNRESOLVED_CONFIG_PRESERVED source=resources.assets scriptPathId=934 objectPathId=6381 asset=" +
                    orphan.usagePath + " originalPointerUnchanged=true runtimeImplementationNotFabricated=true");
            foreach (Edit edit in edits) File.WriteAllText(edit.Path, edit.Text, new UTF8Encoding(false));
            edits.Clear();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            if (beforeMetaHash != ScriptMetaHash())
                throw new BuildFailedException("Original source script metadata changed during SDK binding.");
            Debug.Log("RAFT_SDK_BINDINGS sourceReferences=" + refs + " rewrittenReferences=" + changes +
                      " resolvedTypes=" + targets.Count + " namespaceFallbacks=" + namespaceFallbacks +
                      " unresolvedRequiredSdkTypes=0 preservedOriginalUnresolvedConfigs=" + preservedOrphanReferences + " originalScriptMetaUnchanged=true");
        }

        private static void Register(MonoScript script, HashSet<string> wanted, HashSet<string> unique,
            List<Candidate> candidates)
        {
            if (script == null) return;
            Type type = script.GetClass();
            if (type == null || type.IsAbstract || type.ContainsGenericParameters ||
                (!typeof(MonoBehaviour).IsAssignableFrom(type) &&
                 !typeof(ScriptableObject).IsAssignableFrom(type))) return;
            string assembly = type.Assembly.GetName().Name;
            if (!wanted.Contains(assembly)) return;
            string guid;
            long fileId;
            if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(script, out guid, out fileId) || fileId == 0) return;
            string key = assembly + "\n" + type.FullName + "\n" + guid + "\n" +
                         fileId.ToString(CultureInfo.InvariantCulture);
            if (!unique.Add(key)) return;
            candidates.Add(new Candidate {Assembly = assembly, FullName = type.FullName,
                SimpleName = type.Name, Guid = guid, FileId = fileId});
        }

        private static string ScriptMetaHash()
        {
            string root = System.IO.Path.Combine(Application.dataPath, "Scripts");
            using (var data = new MemoryStream())
            {
                foreach (string path in Directory.GetFiles(root, "*.cs.meta", SearchOption.AllDirectories)
                                                .OrderBy(p => p, StringComparer.Ordinal))
                {
                    byte[] name = Encoding.UTF8.GetBytes(path.Substring(root.Length));
                    data.Write(name, 0, name.Length);
                    data.WriteByte(0);
                    byte[] bytes = File.ReadAllBytes(path);
                    data.Write(bytes, 0, bytes.Length);
                    data.WriteByte(0);
                }
                data.Position = 0;
                using (SHA256 hash = SHA256.Create())
                    return BitConverter.ToString(hash.ComputeHash(data));
            }
        }
    }
}
#endif
