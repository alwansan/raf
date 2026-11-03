using System;
using System.IO;
using RaftAndroid.Platform;

// Pure managed source fixture: no original Raft assets, Unity or device.
internal static class Program
{
    private static int checks;
    private static void Require(bool value, string description)
    {
        if (!value) throw new Exception("OFFLINE_SESSION_IDENTITY_FAIL: " + description);
        checks++;
    }

    private static void InvalidIdentityMustFail(string? identity, string label)
    {
        bool rejected = false;
        try { _ = new OfflineSession(identity!); }
        catch (ArgumentException) { rejected = true; }
        Require(rejected, "invalid profile was accepted: " + label);
    }

    public static int Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "raft-a9-identity-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            string canonical = new LocalProfileStore(root).GetOrCreateProfileId();
            var session = new OfflineSession(canonical);
            Require(session.LocalProfileId == canonical && canonical.Length == 32,
                "normal generated ID must remain unchanged");
            Require(session.IsConnected && session.IsHost && session.IsSinglePlayer &&
                session.ConnectedPlayerCount == 1 && !session.UsesSteam && !session.UsesInternet,
                "valid local-only host semantics must remain unchanged");
            Require(LocalPlayerIdentity.FromProfile(canonical) > 0 &&
                LocalPlayerIdentity.FromProfile(canonical) == LocalPlayerIdentity.FromProfile(session.LocalProfileId),
                "original stable profile-derived ID must remain unchanged");
            Require(new LocalSavePaths(root, session.LocalProfileId).GetWorldDirectory("world_01")
                .Contains("world_01"), "valid local world path must remain available");

            InvalidIdentityMustFail(null, "null");
            InvalidIdentityMustFail("", "empty");
            InvalidIdentityMustFail("ab", "short");
            InvalidIdentityMustFail(new string('a', 31), "31 hex");
            InvalidIdentityMustFail(new string('a', 33), "33 hex");
            InvalidIdentityMustFail(new string('A', 32), "uppercase hex");
            InvalidIdentityMustFail(new string('g', 32), "nonhex");
            InvalidIdentityMustFail("../external", "path traversal");
            InvalidIdentityMustFail(new string('a', 31) + "/", "path separator");
            InvalidIdentityMustFail("local", "would be accepted by old prototype but not original profile store");
            Console.WriteLine("A9_OFFLINE_SESSION_IDENTITY_PASS checks=" + checks);
            return 0;
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); } catch (IOException) { }
        }
    }
}
