using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using System.Threading;

namespace RaftAndroid.Diagnostics
{
    // Managed-only sink. Background writes, bounded queue/files, explicit crash barriers.
    public sealed class PersistentDiagnosticLog : IDisposable
    {
        private readonly ConcurrentQueue<string> pending = new ConcurrentQueue<string>();
        private readonly AutoResetEvent wake = new AutoResetEvent(false);
        private readonly object ioGate = new object();
        private readonly string directory, session;
        private readonly long segmentBytes;
        private readonly int retainedFiles, queueLimit;
        private readonly Thread worker;
        private StreamWriter writer;
        private FileStream stream;
        private int count, segment;
        private long sequence, dropped;
        private long writtenBytes;
        private FileStream startup;
        private const long StartupLimit = 256 * 1024;
        private volatile bool stopping;
        public string LastError { get; private set; }
        public string DirectoryPath => directory;

        public PersistentDiagnosticLog(string directory, long segmentBytes = 4 * 1024 * 1024,
            int retainedFiles = 12, int queueLimit = 2048)
        {
            if (segmentBytes < 256 || retainedFiles < 2 || queueLimit < 1)
                throw new ArgumentException("Invalid diagnostic retention limits");
            this.directory = Path.GetFullPath(directory);
            this.segmentBytes = segmentBytes;
            this.retainedFiles = retainedFiles;
            this.queueLimit = queueLimit;
            Directory.CreateDirectory(this.directory);
            session = DateTime.UtcNow.ToString("yyyyMMddTHHmmssfff", CultureInfo.InvariantCulture) + "-" + Guid.NewGuid().ToString("N").Substring(0, 8);
            // Separate bounded evidence survives routine segment rotation. Keep four launches.
            string evidence = Path.Combine(this.directory, "startup");
            Directory.CreateDirectory(evidence);
            string startupPath = Path.Combine(evidence, "startup-" + session + ".jsonl");
            startup = new FileStream(startupPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            var launches = new DirectoryInfo(evidence).GetFiles("startup-*.jsonl");
            Array.Sort(launches, (a, b) => string.CompareOrdinal(a.Name, b.Name));
            int oldLaunches = launches.Length - 4;
            foreach (var launch in launches)
            {
                if (oldLaunches <= 0) break;
                if (launch.FullName == startupPath) continue;
                launch.Delete(); oldLaunches--;
            }
            OpenSegment();
            worker = new Thread(Run) { IsBackground = true, Name = "Raft diagnostic writer" };
            worker.Start();
        }

        public void Write(string area, string operation, string detail, bool critical = false)
        {
            if (stopping) return;
            if (Interlocked.Increment(ref count) > queueLimit)
            {
                Interlocked.Decrement(ref count);
                if (!critical) { Interlocked.Increment(ref dropped); return; }
                Flush();
                Interlocked.Increment(ref count);
            }
            long id = Interlocked.Increment(ref sequence);
            string line = "{\"utc\":" + Quote(DateTime.UtcNow.ToString("O", CultureInfo.InvariantCulture)) +
                ",\"session\":" + Quote(session) + ",\"sequence\":" + id.ToString(CultureInfo.InvariantCulture) +
                ",\"thread\":" + Thread.CurrentThread.ManagedThreadId.ToString(CultureInfo.InvariantCulture) +
                ",\"area\":" + Quote(area) + ",\"operation\":" + Quote(operation) +
                ",\"detail\":" + Quote(detail) + "}";
            pending.Enqueue(line);
            wake.Set();
            if (critical) Flush();
        }

        public void Flush()
        {
            lock (ioGate)
            {
                try { Drain(); writer.Flush(); stream.Flush(true); startup.Flush(true); }
                catch (Exception ex) { LastError = ex.GetType().Name + ": " + ex.Message; }
            }
        }

        private void Run()
        {
            while (!stopping)
            {
                wake.WaitOne(250);
                lock (ioGate)
                {
                    try { Drain(); writer.Flush(); }
                    catch (Exception ex) { LastError = ex.GetType().Name + ": " + ex.Message; }
                }
            }
        }

        private void Drain()
        {
            long lost = Interlocked.Exchange(ref dropped, 0);
            if (lost != 0) Append("{\"area\":\"logging\",\"operation\":\"queue_overflow\",\"dropped\":" + lost.ToString(CultureInfo.InvariantCulture) + "}");
            while (pending.TryDequeue(out string line))
            {
                Interlocked.Decrement(ref count);
                Append(line);
            }
        }

        private void Append(string line)
        {
            int bytes = Encoding.UTF8.GetByteCount(line) + 1;
            if (startup.Length + bytes <= StartupLimit)
            {
                byte[] copy = Encoding.UTF8.GetBytes(line + "\n");
                startup.Write(copy, 0, copy.Length);
            }
            if (writtenBytes != 0 && writtenBytes + bytes > segmentBytes)
            {
                writer.Dispose();
                OpenSegment();
            }
            writer.WriteLine(line);
            writtenBytes += bytes;
        }

        private void OpenSegment()
        {
            string path = Path.Combine(directory, "raft-" + session + "-" + (segment++).ToString("D4", CultureInfo.InvariantCulture) + ".jsonl");
            stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = false, NewLine = "\n" };
            writtenBytes = 0;
            var files = new DirectoryInfo(directory).GetFiles("raft-*.jsonl");
            Array.Sort(files, (a, b) => a.LastWriteTimeUtc.CompareTo(b.LastWriteTimeUtc));
            int remove = files.Length - retainedFiles;
            foreach (var file in files)
            {
                if (remove <= 0) break;
                if (file.FullName == path) continue;
                file.Delete();
                remove--;
            }
        }

        private static string Quote(string value)
        {
            value = value ?? "";
            if (value.Length > 8192) value = value.Substring(0, 8192) + " [truncated]";
            var text = new StringBuilder(value.Length + 2).Append('"');
            foreach (char ch in value)
            {
                switch (ch)
                {
                    case '"': text.Append("\\\""); break;
                    case '\\': text.Append("\\\\"); break;
                    case '\n': text.Append("\\n"); break;
                    case '\r': text.Append("\\r"); break;
                    case '\t': text.Append("\\t"); break;
                    default:
                        if (ch < 32) text.Append("\\u" + ((int)ch).ToString("x4", CultureInfo.InvariantCulture));
                        else text.Append(ch);
                        break;
                }
            }
            return text.Append('"').ToString();
        }

        public void Dispose()
        {
            if (stopping) return;
            stopping = true;
            wake.Set();
            worker.Join(2000);
            Flush();
            lock (ioGate) { writer.Dispose(); startup.Dispose(); }
            wake.Dispose();
        }
    }

    // Thread-safe, bounded identical-message grouping. First stack is always emitted.
    // Capacity overflow passes through rather than concealing unknown failures.
    public sealed class RepeatedDiagnosticMessages
    {
        private sealed class Entry
        {
            public long Repeated;
            public DateTime First, Last;
        }
        private readonly object gate = new object();
        private readonly Dictionary<string, Entry> entries = new Dictionary<string, Entry>(StringComparer.Ordinal);
        public bool First(string operation, string detail, DateTime now)
        {
            string key = operation + "\n" + detail;
            if (key.Length > 8192) return true;
            lock (gate)
            {
                if (entries.TryGetValue(key, out var entry))
                {
                    entry.Repeated++; entry.Last = now; return false;
                }
                if (entries.Count >= 128) return true;
                entries.Add(key, new Entry { First = now, Last = now });
                return true;
            }
        }
        public void Summarize(Action<string, string, string> write)
        {
            var summaries = new List<string>();
            lock (gate)
            {
                foreach (var pair in entries)
                {
                    var entry = pair.Value;
                    if (entry.Repeated == 0) continue;
                    summaries.Add("repeated=" + entry.Repeated.ToString(CultureInfo.InvariantCulture) +
                        "; first=" + entry.First.ToString("O", CultureInfo.InvariantCulture) +
                        "; last=" + entry.Last.ToString("O", CultureInfo.InvariantCulture) + "; original=" + pair.Key);
                    entry.Repeated = 0;
                }
            }
            foreach (string summary in summaries) write("unity", "repeat_summary", summary);
        }
    }
}
