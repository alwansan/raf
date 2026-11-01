#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace RaftAndroid.Platform
{
    // Local-only report UI for the first device experiments. Nothing is uploaded.
    public sealed class AndroidTestDiagnostics : MonoBehaviour
    {
        private static readonly Queue<string> events = new Queue<string>();
        private static readonly object gate = new object();
        private bool opened;
        private Vector2 scroll;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void StartDiagnostics()
        {
            Application.logMessageReceivedThreaded -= Capture;
            Application.logMessageReceivedThreaded += Capture;
            var host = new GameObject("RaftAndroidTestDiagnostics");
            DontDestroyOnLoad(host);
            host.AddComponent<AndroidTestDiagnostics>();
            Debug.Log("RAFT_ANDROID_DEVICE_TEST earlyStartupCandidate=true gameplayVerified=false");
        }

        private static void Capture(string message, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert &&
                !message.StartsWith("RAFT_", StringComparison.Ordinal)) return;
            string entry = DateTime.UtcNow.ToString("O") + " " + type + " " + message + "\n" + stack;
            if (entry.Length > 3000) entry = entry.Substring(0, 3000);
            lock (gate)
            {
                events.Enqueue(entry);
                while (events.Count > 48) events.Dequeue();
            }
        }

        private string Report()
        {
            var text = new StringBuilder();
            text.AppendLine("Raft Android early device test");
            text.AppendLine("Unity " + Application.unityVersion + "; scene " + SceneManager.GetActiveScene().name);
            text.AppendLine(SystemInfo.deviceModel + "; " + SystemInfo.operatingSystem);
            text.AppendLine(SystemInfo.graphicsDeviceName + "; " + SystemInfo.graphicsDeviceType);
            text.AppendLine("This report does not verify gameplay, sound or save/load.");
            lock (gate) foreach (string entry in events) text.AppendLine(entry);
            return text.ToString();
        }

        private void OnGUI()
        {
            float scale = Mathf.Max(1f, Screen.height / 720f);
            Matrix4x4 previous = GUI.matrix;
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1));
            if (GUI.Button(new Rect(8, 8, 145, 44), opened ? "Close test report" : "Test report")) opened = !opened;
            if (opened)
            {
                float width = Screen.width / scale - 16;
                float height = Screen.height / scale - 70;
                GUILayout.BeginArea(new Rect(8, 60, width, height), GUI.skin.box);
                GUILayout.Label("Early Android test: startup and diagnostics. Singleplayer and touch controls are still being integrated.");
                if (GUILayout.Button("Copy test report", GUILayout.Height(44))) GUIUtility.systemCopyBuffer = Report();
                scroll = GUILayout.BeginScrollView(scroll);
                GUILayout.Label(Report());
                GUILayout.EndScrollView();
                GUILayout.EndArea();
            }
            GUI.matrix = previous;
        }
    }
}
#endif
