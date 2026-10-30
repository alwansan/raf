using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;
namespace RaftAndroid.Editor
{
    public sealed class ScriptBindingTarget
    {
        public string Guid { get; private set; }
        public long FileId { get; private set; }
        public ScriptBindingTarget(string guid, long fileId)
        {
            if (!Regex.IsMatch(guid ?? "", @"\A[0-9a-fA-F]{32}\z") ||
                guid == new string('0', 32) || fileId == 0)
                throw new ArgumentException("Invalid resolved MonoScript identity.");
            Guid = guid.ToLowerInvariant();
            FileId = fileId;
        }
    }
    public sealed class ScriptBindingRewrite
    {
        public string Text { get; private set; }
        public int SourceReferences { get; private set; }
        public int Changes { get; private set; }
        public IReadOnlyList<string> MissingTargets { get; private set; }
        public ScriptBindingRewrite(string text, int references, int changes, List<string> missing)
        {
            Text = text; SourceReferences = references; Changes = changes;
            MissingTargets = missing.AsReadOnly();
        }
    }
    // Caller validates all files before writing, and never passes .meta files here.
    public static class SdkScriptBindingCore
    {
        private static readonly Regex Script = new Regex(@"(?m)^[ \t]*m_Script:[ \t]*\{[^}\r\n]*\}");
        private static readonly Regex GuidField = new Regex(@"(\bguid:[ \t]*)([0-9a-fA-F]{32})\b");
        private static readonly Regex FileIdField = new Regex(@"(\bfileID:[ \t]*)(-?[0-9]+)\b");
        public static ScriptBindingRewrite Rewrite(string text, IEnumerable<string> sourceGuids,
            IReadOnlyDictionary<string, ScriptBindingTarget> targets)
        {
            var sources = new HashSet<string>(sourceGuids, StringComparer.OrdinalIgnoreCase);
            var normalized = new Dictionary<string, ScriptBindingTarget>(StringComparer.OrdinalIgnoreCase);
            foreach (var item in targets) normalized.Add(item.Key, item.Value);
            int references = 0, changes = 0;
            var missing = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            string updated = Script.Replace(text, match =>
            {
                string block = match.Value;
                Match guid = GuidField.Match(block);
                if (!guid.Success || !sources.Contains(guid.Groups[2].Value)) return block;
                references++;
                Match id = FileIdField.Match(block);
                if (!id.Success || id.Groups[2].Value != "11500000")
                    throw new InvalidOperationException("Unexpected source MonoScript fileID.");
                ScriptBindingTarget target;
                if (!normalized.TryGetValue(guid.Groups[2].Value, out target))
                {
                    missing.Add(guid.Groups[2].Value.ToLowerInvariant());
                    return block;
                }
                string mapped = FileIdField.Replace(block,
                    m => m.Groups[1].Value + target.FileId.ToString(CultureInfo.InvariantCulture), 1);
                mapped = GuidField.Replace(mapped, m => m.Groups[1].Value + target.Guid, 1);
                if (mapped != block) changes++;
                return mapped;
            });
            var missingSorted = new List<string>(missing);
            missingSorted.Sort(StringComparer.Ordinal);
            return new ScriptBindingRewrite(updated, references, changes, missingSorted);
        }
    }
}
