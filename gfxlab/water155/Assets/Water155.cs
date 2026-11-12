using System;
using System.Collections;
using System.IO;
using System.IO.Compression;
using UnityEngine;

public sealed class Water155 : MonoBehaviour
{
    private const int Side = 33;
    private const int Count = Side * Side;
    private const float Tolerance = 0.00003f;

    public ComputeShader compute;
    public MeshFilter surface;

    [Serializable]
    private sealed class Result
    {
        public float time, amplitude, maximumError, maximumDelta;
        public int samples, invalidSamples;
        public bool passed;
    }

    [Serializable]
    private sealed class Report
    {
        public string experiment = "GFX155";
        public string unity, gpu, graphicsApi, driver, os, exportId, error;
        public int width, height, threadsX;
        public bool supportsCompute, passed, originalRaftData;
        public Result[] cases = new Result[4];
    }

    private Report report;
    private string status = "Preparing water test";
    private string zip;
    private Mesh mesh;
    private Vector3[] vertices;
    private readonly float[][] frames = new float[4][];

    private IEnumerator Start()
    {
        report = new Report
        {
            unity = Application.unityVersion,
            gpu = SystemInfo.graphicsDeviceName,
            graphicsApi = SystemInfo.graphicsDeviceType.ToString(),
            driver = SystemInfo.graphicsDeviceVersion,
            os = SystemInfo.operatingSystem,
            supportsCompute = SystemInfo.supportsComputeShaders,
            width = Screen.width,
            height = Screen.height,
            exportId = Guid.NewGuid().ToString("N")
        };
        yield return null;
        try
        {
            RunProbe();
            status = report.passed ? "PASS - synthetic GPU surface" : "FAIL - read report";
        }
        catch (Exception exception)
        {
            report.error = exception.ToString();
            status = "FAIL - " + exception.GetType().Name;
        }

        yield return new WaitForEndOfFrame();
        try
        {
            string name = "GFX155-ALL-TEST-LOGS-" + report.exportId + ".zip";
            zip = Path.Combine(Application.temporaryCachePath, name);
            using (var file = File.Create(zip))
            using (var archive = new ZipArchive(file, ZipArchiveMode.Create))
            {
                using (var writer = new StreamWriter(archive.CreateEntry("summary.json").Open()))
                    writer.Write(JsonUtility.ToJson(report, true));
                for (int index = 0; index < frames.Length; index++)
                {
                    if (frames[index] == null)
                        continue;
                    using (var writer = new BinaryWriter(archive.CreateEntry("heights-" + index + ".f32le").Open()))
                        foreach (float height in frames[index])
                            writer.Write(height);
                }
            }
            Export();
        }
        catch (Exception exception)
        {
            status += " | Export failed: " + exception.Message;
        }
    }

    private void RunProbe()
    {
        if (!report.supportsCompute)
            throw new NotSupportedException("Compute shaders unavailable on active backend");
        int kernel = compute.FindKernel("Height");
        compute.GetKernelThreadGroupSizes(kernel, out uint x, out uint y, out uint z);
        if (x != 64 || y != 1 || z != 1)
            throw new InvalidOperationException("Unexpected Height thread group");
        report.threadsX = (int)x;
        CreateSurface();

        float[] values = new float[Count];
        float[] previous = new float[Count];
        float[] times = { 0f, 0f, 0.75f, 1.5f };
        using (var buffer = new ComputeBuffer(Count, sizeof(float)))
        {
            compute.SetInt("Side", Side);
            compute.SetBuffer(kernel, "Heights", buffer);
            for (int step = 0; step < times.Length; step++)
            {
                float amplitude = step == 0 ? 0f : 1f;
                float time = times[step];
                // Poison each sample so a missed GPU write cannot reuse a previous result.
                for (int i = 0; i < Count; i++)
                    values[i] = float.NaN;
                buffer.SetData(values);
                compute.SetFloat("SampleTime", time);
                compute.SetFloat("WaveScale", amplitude);
                compute.Dispatch(kernel, (Count + (int)x - 1) / (int)x, 1, 1);
                buffer.GetData(values);
                var result = new Result { time = time, amplitude = amplitude, samples = Count };
                for (int i = 0; i < Count; i++)
                {
                    float value = values[i];
                    if (float.IsNaN(value) || float.IsInfinity(value))
                    {
                        result.invalidSamples++;
                        continue;
                    }

                    Vector3 vertex = vertices[i];
                    double expected = amplitude * (
                        0.43 * Math.Sin(1.7 * vertex.x + 0.6 * vertex.z - 1.9 * time) +
                        0.21 * Math.Sin(-0.4 * vertex.x + 2.2 * vertex.z - 2.7 * time));
                    result.maximumError = Mathf.Max(result.maximumError, (float)Math.Abs(value - expected));
                    if (step > 0 && !float.IsNaN(previous[i]) && !float.IsInfinity(previous[i]))
                        result.maximumDelta = Mathf.Max(result.maximumDelta, Mathf.Abs(value - previous[i]));
                    vertices[i].y = value;
                }
                result.passed = result.invalidSamples == 0 && result.maximumError <= Tolerance &&
                    (step == 0 || result.maximumDelta > 0.1f);
                report.cases[step] = result;
                Array.Copy(values, previous, Count);
                frames[step] = (float[])values.Clone();
            }
        }

        report.passed = Array.TrueForAll(report.cases, item => item.passed);
        if (report.passed)
            ApplySurface();
    }

    private void Update()
    {
        if (report == null || !report.passed)
            return;

        float phase = Mathf.PingPong(Time.unscaledTime / 0.75f, 2f);
        int frame = Mathf.Min((int)phase, 1);
        for (int i = 0; i < Count; i++)
            vertices[i].y = Mathf.Lerp(frames[frame + 1][i], frames[frame + 2][i], phase - frame);
        ApplySurface();
    }

    private void CreateSurface()
    {
        vertices = new Vector3[Count];
        var indices = new int[(Side - 1) * (Side - 1) * 6];
        int n = 0;
        for (int i = 0; i < Count; i++)
        {
            vertices[i] = new Vector3(i % Side * 0.25f - 4f, 0, i / Side * 0.25f - 4f);
            if (i % Side == Side - 1 || i / Side == Side - 1)
                continue;
            indices[n++] = i;
            indices[n++] = i + Side;
            indices[n++] = i + 1;
            indices[n++] = i + 1;
            indices[n++] = i + Side;
            indices[n++] = i + Side + 1;
        }

        mesh = new Mesh { name = "GFX155 analytic surface" };
        mesh.MarkDynamic();
        mesh.vertices = vertices;
        mesh.triangles = indices;
        surface.sharedMesh = mesh;
    }

    private void ApplySurface()
    {
        mesh.vertices = vertices;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
    }

    private void OnDestroy()
    {
        if (mesh != null)
            Destroy(mesh);
    }

    private void Export()
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
        using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
        using (var resolver = activity.Call<AndroidJavaObject>("getContentResolver"))
        using (var downloads = new AndroidJavaClass("android.provider.MediaStore$Downloads"))
        using (var collection = downloads.GetStatic<AndroidJavaObject>("EXTERNAL_CONTENT_URI"))
        using (var metadata = new AndroidJavaObject("android.content.ContentValues"))
        {
            metadata.Call("put", "_display_name", Path.GetFileName(zip));
            metadata.Call("put", "mime_type", "application/zip");
            metadata.Call("put", "relative_path", "Download/Games/cl/test/g/");
            using (var one = new AndroidJavaObject("java.lang.Integer", 1))
                metadata.Call("put", "is_pending", one);
            using (var uri = resolver.Call<AndroidJavaObject>("insert", collection, metadata))
            {
                if (uri == null)
                    throw new IOException("Downloads insert returned null");
                try
                {
                    using (var stream = resolver.Call<AndroidJavaObject>("openOutputStream", uri))
                    {
                        if (stream == null)
                            throw new IOException("Downloads stream unavailable");
                        try
                        {
                            // Java OutputStream.write requires a signed JNI byte array.
                            byte[] bytes = File.ReadAllBytes(zip);
                            sbyte[] signed = new sbyte[bytes.Length];
                            Buffer.BlockCopy(bytes, 0, signed, 0, bytes.Length);
                            stream.Call("write", signed);
                        }
                        finally { stream.Call("close"); }
                    }
                    metadata.Call("clear");
                    using (var zero = new AndroidJavaObject("java.lang.Integer", 0))
                        metadata.Call("put", "is_pending", zero);
                    if (resolver.Call<int>("update", uri, metadata, null, null) != 1)
                        throw new IOException("Downloads publication failed");
                }
                catch
                {
                    resolver.Call<int>("delete", uri, null, null);
                    throw;
                }
            }
        }
        status += " | ZIP exported to Download/Games/cl/test/g/";
#else
        status += " | ZIP: " + zip;
#endif
        zip = null;
    }

    private void OnGUI()
    {
        var label = new GUIStyle(GUI.skin.label) { fontSize = Mathf.Max(20, Screen.height / 26), wordWrap = true };
        GUI.Label(new Rect(24, 16, Screen.width - 48, Screen.height / 4), "GFX155  " + status, label);
        if (zip != null && GUI.Button(new Rect(24, Screen.height - 100, 240, 64), "Retry ZIP export"))
        {
            try { Export(); }
            catch (Exception error) { status = "Export failed: " + error.Message; }
        }
    }
}
