using System;
using System.IO;
using RaftAndroid.Platform;

// Executes the actual netstandard LocalProfileStore under Linux in cheap CI.
// These are synthetic files; no original Raft binary saves or game source.
internal static class ProfileLinkSafety
{
    private static int checks;

    private static void Verify(bool result, string message)
    {
        if (!result) throw new Exception(message);
        checks++;
    }

    private static void RejectRedirect(Action action)
    {
        try { action(); }
        catch (UnauthorizedAccessException) { checks++; return; }
        throw new Exception("Expected an explicit symlink redirect rejection");
    }

    private static string ProfilePath(string root) =>
        Path.Combine(root, "RaftAndroid", "profiles", "local", "profile.id");

    public static int Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "raft-profile-link-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            string normal = Path.Combine(root, "normal");
            var good = new LocalProfileStore(normal);
            string first = good.GetOrCreateProfileId();
            Verify(first.Length == 32 && first == new LocalProfileStore(normal).GetOrCreateProfileId(),
                "Normal durable identity unexpectedly changed");

            string external = Path.Combine(root, "external-profile.id");
            string validExternal = new string('a', 32);
            File.WriteAllText(external, validExternal);
            string linkedFileRoot = Path.Combine(root, "file-link-app");
            string fileLink = ProfilePath(linkedFileRoot);
            Directory.CreateDirectory(Path.GetDirectoryName(fileLink)!);
            File.CreateSymbolicLink(fileLink, external);
            RejectRedirect(() => new LocalProfileStore(linkedFileRoot).GetOrCreateProfileId());
            Verify(File.ReadAllText(external) == validExternal,
                "External identity was changed during file-link rejection");

            string outsideLocal = Path.Combine(root, "external-local");
            Directory.CreateDirectory(outsideLocal);
            File.WriteAllText(Path.Combine(outsideLocal, "profile.id"), validExternal);
            string linkedDirRoot = Path.Combine(root, "directory-link-app");
            string localDir = Path.GetDirectoryName(ProfilePath(linkedDirRoot))!;
            Directory.CreateDirectory(Path.GetDirectoryName(localDir)!);
            Directory.CreateSymbolicLink(localDir, outsideLocal);
            RejectRedirect(() => new LocalProfileStore(linkedDirRoot).GetOrCreateProfileId());
            Verify(File.ReadAllText(Path.Combine(outsideLocal, "profile.id")) == validExternal,
                "External identity was changed during parent-link rejection");

            string linkedAppRoot = Path.Combine(root, "app-link-app");
            Directory.CreateDirectory(linkedAppRoot);
            string outsideApp = Path.Combine(root, "external-app");
            Directory.CreateDirectory(Path.Combine(outsideApp, "profiles", "local"));
            File.WriteAllText(Path.Combine(outsideApp, "profiles", "local", "profile.id"), validExternal);
            Directory.CreateSymbolicLink(Path.Combine(linkedAppRoot, "RaftAndroid"), outsideApp);
            RejectRedirect(() => new LocalProfileStore(linkedAppRoot).GetOrCreateProfileId());
            Verify(File.ReadAllText(Path.Combine(outsideApp, "profiles", "local", "profile.id")) == validExternal,
                "External identity was changed during app-root-link rejection");

            Console.WriteLine("PROFILE_LINK_SAFETY_PASS checks=" + checks);
            return 0;
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); } catch (IOException) { }
        }
    }
}
