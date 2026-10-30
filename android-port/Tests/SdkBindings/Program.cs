using System;
using System.Collections.Generic;
using RaftAndroid.Editor;
internal static class Program
{
    private const string Source = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    private const string Target = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
    private static int count;
    private static void Check(bool value, string message)
    {
        if (!value) throw new Exception(message);
        count++;
    }
    private static void Main()
    {
        var map = new Dictionary<string, ScriptBindingTarget>
        {
            { Source, new ScriptBindingTarget(Target, -1508123456) }
        };
        string script = "  m_Script: {fileID: 11500000, guid: " + Source + ", type: 3}";
        string other = "  m_Mesh: {fileID: 11500000, guid: " + Source + ", type: 3}";
        string text = "%YAML 1.1\n" + script + "\n" + other + "\n";
        var result = SdkScriptBindingCore.Rewrite(text, new[] {Source}, map);
        Check(result.Text == "%YAML 1.1\n  m_Script: {fileID: -1508123456, guid: " + Target +
              ", type: 3}\n" + other + "\n", "Changed unrelated serialized content.");
        Check(result.Changes == 1 && result.SourceReferences == 1 &&
              result.MissingTargets.Count == 0, "Wrong reference accounting.");
        var second = SdkScriptBindingCore.Rewrite(result.Text, new[] {Source}, map);
        Check(second.Text == result.Text && second.Changes == 0, "Rewrite is not idempotent.");
        var absent = SdkScriptBindingCore.Rewrite(text, new[] {Source},
            new Dictionary<string, ScriptBindingTarget>());
        Check(absent.Text == text && absent.MissingTargets.Count == 1 &&
              absent.MissingTargets[0] == Source, "Unresolved targets must preserve data.");
        var unknown = SdkScriptBindingCore.Rewrite(text, new[] {Target}, map);
        Check(unknown.Text == text && unknown.SourceReferences == 0, "Non-SDK script modified.");
        var upper = SdkScriptBindingCore.Rewrite(script.ToUpperInvariant().Replace("M_SCRIPT","m_Script")
            .Replace("FILEID","fileID").Replace("GUID","guid"), new[] {Source}, map);
        Check(upper.Changes == 1, "GUID comparison must be case-insensitive.");
        bool refused = false;
        try { SdkScriptBindingCore.Rewrite(script.Replace("11500000","0"), new[] {Source}, map); }
        catch (InvalidOperationException) { refused = true; }
        Check(refused, "Unexpected source fileID was accepted.");
        refused = false;
        try { new ScriptBindingTarget("not-a-guid", 11500000); }
        catch (ArgumentException) { refused = true; }
        Check(refused, "Invalid target GUID was accepted.");
        Console.WriteLine("SDK binding core: " + count + " checks passed");
    }
}
