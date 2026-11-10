using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using UnityEngine;

namespace RaftGraphicsLab
{
    /// <summary>
    /// Creates a ZIP of all recorded lab sessions and publishes it into the exact
    /// user-requested public Downloads subfolder on Android via MediaStore.
    /// Failing the scoped-storage transfer never discards the private ZIP.
    /// </summary>
    public static class GfxDownloadsZipExporter
    {
        public const string RelativeDownloadDirectory="Download/Games/cl/test/g/";
        public const string ExpectedPublicDirectory="/storage/emulated/0/Download/Games/cl/test/g/";

        private static void AddFile(ZipArchive zip,string path,string entryName)
        {
            if(!File.Exists(path))return;
            var entry=zip.CreateEntry(entryName,CompressionLevel.Optimal);
            using(var input=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite))
            using(var output=entry.Open())
                input.CopyTo(output);
        }

        private static string MakePrivateZip(string root,string session,string name)
        {
            string archives=Path.Combine(root,"exports");
            Directory.CreateDirectory(archives);
            string zipPath=Path.Combine(archives,name);
            string sessions=Path.Combine(root,"sessions");
            if(!Directory.Exists(sessions))
                throw new IOException("NO_RECORDED_TEST_SESSIONS");

            // Do not include previous ZIPs in the next ZIP (unbounded growth).
            string[] files=Directory.GetFiles(sessions,"*",SearchOption.AllDirectories);
            if(files.Length==0)
                throw new IOException("NO_TEST_EVENT_FILES");
            int added=0;
            using(var output=new FileStream(zipPath,FileMode.CreateNew,FileAccess.Write,FileShare.None))
            using(var zip=new ZipArchive(output,ZipArchiveMode.Create,false))
            {
                foreach(string path in files)
                {
                    // Only regular files inside the known app-private session directory.
                    string relative=path.Substring(sessions.Length).TrimStart(
                        Path.DirectorySeparatorChar,Path.AltDirectorySeparatorChar)
                        .Replace('\\','/');
                    if(string.IsNullOrEmpty(relative)||relative.Contains("../")||relative.StartsWith("/"))
                        throw new IOException("INVALID_PRIVATE_TEST_LOG_PATH");
                    AddFile(zip,path,"sessions/"+relative);
                    added++;
                }
                AddFile(zip,Path.Combine(root,"multi-report.json"),"latest/multi-report.json");
                var guide=zip.CreateEntry("README.txt",CompressionLevel.Optimal);
                using(var w=new StreamWriter(guide.Open(),new UTF8Encoding(false)))
                {
                    w.WriteLine("GFX-LAB automatic session diagnostics export v1");
                    w.WriteLine("Device diagnostics, not authentic Raft Shader48 or PC pixel parity.");
                    w.WriteLine("Session: "+session);
                    w.WriteLine("Created UTC: "+DateTime.UtcNow.ToString("o"));
                    w.WriteLine("Events and FULL Unity log stack traces: sessions/*/events.jsonl");
                    w.WriteLine("Every saved test state and camera/device/GPU data: sessions/*/snapshots.jsonl");
                    w.WriteLine("Per-session counts/errors: sessions/*/summary.json");
                    w.WriteLine("Last model/channel report: latest/multi-report.json");
                    w.WriteLine("Expected location: "+ExpectedPublicDirectory);
                    w.WriteLine("Captured log JSON is user-private; do not publish without reviewing it.");
                    w.WriteLine("Original Shader48 restored: false");
                }
            }
            if(added<2 || !File.Exists(zipPath) || new FileInfo(zipPath).Length<100)
                throw new IOException("EMPTY_OR_INCOMPLETE_TEST_LOG_ZIP");
            using(var input=new FileStream(zipPath,FileMode.Open,FileAccess.Read,FileShare.Read))
            using(var check=new ZipArchive(input,ZipArchiveMode.Read))
            {
                if(check.Entries.Count<added+1)
                    throw new IOException("TEST_LOG_ZIP_ENTRY_COUNT_FAILED");
                if(check.GetEntry("README.txt")==null)
                    throw new IOException("TEST_LOG_ZIP_README_MISSING");
            }
            return zipPath;
        }

        public static bool Export(string root,string session,out string publicPath,out string error)
        {
            publicPath="";
            error="";
            string zipName="GFXLAB-ALL-TEST-LOGS-"+
                DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff")+"-"+session+".zip";
            string privateZip="";
            try
            {
                privateZip=MakePrivateZip(root,session,zipName);
#if UNITY_ANDROID && !UNITY_EDITOR
                using(var unityPlayer=new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using(var activity=unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
                using(var bridge=new AndroidJavaClass("com.alwansan.gfxlab.GfxDownloadsBridge"))
                {
                    string uri=bridge.CallStatic<string>("exportZip",activity,privateZip,zipName);
                    if(string.IsNullOrEmpty(uri)||!uri.StartsWith("content://",StringComparison.Ordinal))
                        throw new IOException("MEDIASTORE_EXPORTED_URI_NOT_VERIFIED");
                    publicPath=ExpectedPublicDirectory+zipName;
                    return true;
                }
#else
                throw new PlatformNotSupportedException(
                    "Direct public Downloads export requires Android 10+");
#endif
            }
            catch(Exception ex)
            {
                error="DOWNLOADS_ZIP_EXPORT_FAILED: "+ex.GetType().Name+" "+ex.Message+
                    " | Private copy retained: "+privateZip;
                return false;
            }
        }
    }
}
