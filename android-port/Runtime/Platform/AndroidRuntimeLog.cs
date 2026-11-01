#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using System.IO;
using System.Diagnostics;
using UnityEngine;

namespace RaftAndroid.Diagnostics
{
    public static class AndroidRuntimeLog
    {
        private static PersistentDiagnosticLog sink;
        public static string LogDirectory { get; private set; }
        public static string StorageError { get; private set; }

        public static void Initialize()
        {
            if (sink != null || StorageError != null) return;
            try
            {
                LogDirectory = Path.Combine(Application.persistentDataPath, "raft-logs");
                sink = new PersistentDiagnosticLog(LogDirectory);
                Write("startup", "logger.ready", "version=" + Application.version + "; unity=" + Application.unityVersion +
                    "; package=" + Application.identifier + "; device=" + SystemInfo.deviceModel +
                    "; os=" + SystemInfo.operatingSystem + "; gpu=" + SystemInfo.graphicsDeviceName +
                    "; graphics=" + SystemInfo.graphicsDeviceType, true);
            }
            catch (Exception ex) { StorageError = ex.GetType().Name + ": " + ex.Message; }
        }

        public static void Write(string area, string operation, string detail = "", bool critical = false)
        {
            sink?.Write(area, operation, detail, critical);
        }

        public static void Stage(string operation, Action action)
        {
            Initialize();
            Write("audio", operation + ".begin", "", true);
            try { action(); Write("audio", operation + ".ok", "", true); }
            catch (Exception ex) { Write("audio", operation + ".failed", ex.ToString(), true); throw; }
        }

        public static void Flush() { sink?.Flush(); }
        public static long BeginOperation(string area, string operation, string detail)
        {
            Write(area, operation + ".enter", detail, true);
            return Stopwatch.GetTimestamp();
        }
        public static void EndOperation(string area, string operation, long started, bool failed)
        {
            double ms = (Stopwatch.GetTimestamp() - started) * 1000.0 / Stopwatch.Frequency;
            Write(area, operation + ".exit", "exceptionEscaped=" + failed + "; elapsed_ms=" +
                ms.ToString("F3", System.Globalization.CultureInfo.InvariantCulture), true);
        }
        public static string Status => StorageError ?? sink?.LastError ?? "ready";
        public static void Shutdown() { sink?.Dispose(); sink = null; }
    }
}
#endif
