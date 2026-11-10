using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace RaftGraphicsLab
{
    /// <summary>
    /// Append-only diagnostic session. Records every change in the model/channel
    /// inspector, periodic state, and every Unity message/exception with full stack.
    /// Session files stay private until the owner presses EXPORT ZIP.
    /// </summary>
    public sealed class GfxSessionRecorder : MonoBehaviour
    {
        [Serializable] private sealed class EventRow
        {
            public string utc;
            public string session;
            public string kind;
            public string message;
            public string stackTrace;
            public string stateJson;
            public int frame;
            public long sequence;
            public float realtime;
        }

        [Serializable] private sealed class SessionSummary
        {
            public string schema;
            public string session;
            public string startUtc;
            public string lastUtc;
            public string unity;
            public string device;
            public string graphicsApi;
            public string graphicsDevice;
            public string colorSpace;
            public string persistentDirectory;
            public string intendedExportDirectory;
            public bool originalShaderRestored;
            public bool devicePixelParityVerified;
            public long eventsWritten;
            public long snapshotsWritten;
            public long unityErrors;
            public long unityWarnings;
            public long messagesDropped;
            public string writeFailure;
        }

        private struct PendingUnityLog
        {
            public string message;
            public string stackTrace;
            public LogType type;
            public string utc;
        }

        private readonly object queueGate=new object();
        private readonly Queue<PendingUnityLog> pending=new Queue<PendingUnityLog>();
        private StreamWriter eventWriter;
        private StreamWriter snapshotWriter;
        private string root;
        private string session;
        private string sessionFolder;
        private string startedUtc;
        private string writeFailure="";
        private long sequence;
        private long eventsWritten;
        private long snapshotsWritten;
        private long unityErrors;
        private long unityWarnings;
        private long messagesDropped;
        private float lastFlush;
        private bool recorderReady;

        public string RootDirectory { get { return root; } }
        public string SessionId { get { return session; } }
        public string Failure { get { return writeFailure; } }
        public long RecordedSnapshots { get { return snapshotsWritten; } }

        private static string UtcNow()
        {
            return DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");
        }
        private void Awake()
        {
            startedUtc=UtcNow();
            session=DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff")+"-"+Guid.NewGuid().ToString("N").Substring(0,8);
            root=Path.Combine(Application.persistentDataPath,"gfxlab");
            sessionFolder=Path.Combine(root,"sessions",session);
            try
            {
                Directory.CreateDirectory(sessionFolder);
                eventWriter=new StreamWriter(new FileStream(
                    Path.Combine(sessionFolder,"events.jsonl"),FileMode.Append,FileAccess.Write,FileShare.Read),
                    new System.Text.UTF8Encoding(false));
                snapshotWriter=new StreamWriter(new FileStream(
                    Path.Combine(sessionFolder,"snapshots.jsonl"),FileMode.Append,FileAccess.Write,FileShare.Read),
                    new System.Text.UTF8Encoding(false));
                recorderReady=true;
                Application.logMessageReceivedThreaded+=OnUnityLogThreaded;
                WriteEvent("session_start","Automatic events, state snapshots, stacktraces and export enabled","","");
                SaveSummary();
                Flush();
            }
            catch(Exception ex)
            {
                writeFailure="RECORDER_START_FAILED "+ex.GetType().Name+" "+ex.Message;
                recorderReady=false;
                try { if(eventWriter!=null)eventWriter.Dispose(); } catch {}
                try { if(snapshotWriter!=null)snapshotWriter.Dispose(); } catch {}
                eventWriter=null; snapshotWriter=null;
                Debug.LogError(writeFailure);
            }
        }

        private void OnUnityLogThreaded(string message,string stackTrace,LogType type)
        {
            // Unity callback is sometimes invoked on a worker thread. Never touch
            // Unity API, StreamWriter, or the current scene from this callback.
            lock(queueGate)
            {
                if(pending.Count>=50000)
                {
                    messagesDropped++;
                    return;
                }
                pending.Enqueue(new PendingUnityLog {
                    message=message,stackTrace=stackTrace,type=type,utc=UtcNow()
                });
            }
        }

        private void WriteEvent(string kind,string message,string stack,string state)
        {
            if(!recorderReady||eventWriter==null)return;
            try
            {
                var row=new EventRow {
                    utc=UtcNow(),session=session,kind=kind,
                    message=message??"",stackTrace=stack??"",
                    stateJson=state??"",frame=Time.frameCount,
                    realtime=Time.realtimeSinceStartup,sequence=++sequence
                };
                eventWriter.WriteLine(JsonUtility.ToJson(row,false));
                eventsWritten++;
            }
            catch(Exception ex)
            {
                writeFailure="EVENT_WRITE_FAILED "+ex.GetType().Name+" "+ex.Message;
            }
        }

        public void RecordState(string reason,string json)
        {
            if(!recorderReady)return;
            if(string.IsNullOrEmpty(json))json="{}";
            // This file contains one complete, reason-tagged original DeviceLog
            // JSON string per transition; no more manual clipboard exports.
            try
            {
                var row=new EventRow {
                    utc=UtcNow(),session=session,kind="state_snapshot",
                    message=reason??"state_change",stackTrace="",
                    stateJson=json,frame=Time.frameCount,
                    realtime=Time.realtimeSinceStartup,sequence=++sequence
                };
                snapshotWriter.WriteLine(JsonUtility.ToJson(row,false));
                snapshotsWritten++;
                WriteEvent("ui_state_change",reason??"state_change","",json);
            }
            catch(Exception ex)
            {
                writeFailure="SNAPSHOT_WRITE_FAILED "+ex.GetType().Name+" "+ex.Message;
            }
        }

        public void RecordAction(string action)
        {
            WriteEvent("user_action",action,"","");
        }

        private void DrainMessages()
        {
            int processed=0;
            while(processed<2048)
            {
                PendingUnityLog item;
                lock(queueGate)
                {
                    if(pending.Count==0)break;
                    item=pending.Dequeue();
                }
                if(item.type==LogType.Error||item.type==LogType.Exception||item.type==LogType.Assert)
                    unityErrors++;
                if(item.type==LogType.Warning)unityWarnings++;
                WriteEvent("unity_"+item.type.ToString(),item.message,item.stackTrace,"");
                processed++;
            }
        }

        private void Update()
        {
            if(!recorderReady)return;
            DrainMessages();
            if(Time.unscaledTime-lastFlush>=2f)
            {
                Flush();
                lastFlush=Time.unscaledTime;
            }
        }

        public void Flush()
        {
            if(!recorderReady)return;
            DrainMessages();
            try
            {
                eventWriter.Flush();
                snapshotWriter.Flush();
                SaveSummary();
            }
            catch(Exception ex)
            {
                writeFailure="LOG_FLUSH_FAILED "+ex.GetType().Name+" "+ex.Message;
            }
        }

        private void SaveSummary()
        {
            var report=new SessionSummary {
                schema="gfxlab-session-v1",session=session,startUtc=startedUtc,lastUtc=UtcNow(),
                unity=Application.unityVersion,device=SystemInfo.deviceModel,
                graphicsApi=SystemInfo.graphicsDeviceType.ToString(),
                graphicsDevice=SystemInfo.graphicsDeviceName,
                colorSpace=QualitySettings.activeColorSpace.ToString(),
                persistentDirectory=root,
                intendedExportDirectory="/storage/emulated/0/Download/Games/cl/test/g/",
                originalShaderRestored=false,devicePixelParityVerified=false,
                eventsWritten=eventsWritten,snapshotsWritten=snapshotsWritten,
                unityErrors=unityErrors,unityWarnings=unityWarnings,
                messagesDropped=messagesDropped,writeFailure=writeFailure
            };
            File.WriteAllText(Path.Combine(sessionFolder,"summary.json"),
                JsonUtility.ToJson(report,true));
        }

        public bool ExportAll(out string publicPath,out string error)
        {
            publicPath="";
            error="";
            try
            {
                RecordAction("EXPORT_ALL_LOGS_REQUESTED");
                Flush();
                if(!recorderReady)
                    throw new IOException("Recorder unavailable: "+writeFailure);
                return GfxDownloadsZipExporter.Export(root,session,out publicPath,out error);
            }
            catch(Exception ex)
            {
                error=ex.GetType().Name+" "+ex.Message;
                RecordAction("EXPORT_ALL_LOGS_FAILED: "+error);
                return false;
            }
        }

        public void RecordExportResult(bool success,string text)
        {
            RecordAction((success?"EXPORT_ALL_LOGS_COMPLETE ":"EXPORT_ALL_LOGS_FAILED ")+text);
            Flush();
        }

        private void OnApplicationPause(bool paused)
        {
            if(paused)Flush();
        }
        private void OnApplicationFocus(bool focused)
        {
            if(!focused)Flush();
        }
        private void OnApplicationQuit()
        {
            Flush();
            DisposeWriters();
        }
        private void OnDestroy()
        {
            Flush();
            DisposeWriters();
        }
        private void DisposeWriters()
        {
            Application.logMessageReceivedThreaded-=OnUnityLogThreaded;
            recorderReady=false;
            try { if(eventWriter!=null)eventWriter.Dispose(); } catch {}
            try { if(snapshotWriter!=null)snapshotWriter.Dispose(); } catch {}
            eventWriter=null;
            snapshotWriter=null;
        }
    }
}
