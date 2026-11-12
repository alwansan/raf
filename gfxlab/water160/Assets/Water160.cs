using System;
using System.Collections;
using System.IO;
using System.IO.Compression;
using UnityEngine;

public sealed class Water160 : MonoBehaviour
{
    private const int Side = 32;
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
        public string experiment = "GFX160";
        public string unity, gpu, graphicsApi, driver, os, exportId, error;
        public int width, height, threadsX;
        public int horizontalKernel, verticalKernel, readbackKernel;
        public float maxImaginary;
        public string intermediateFormat;
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
            status = report.passed ? "PASS - inverse FFT texture chain" : "FAIL - read report";
        }
        catch (Exception exception)
        {
            report.error = exception.ToString();
            status = "FAIL - " + exception.GetType().Name;
        }

        yield return new WaitForEndOfFrame();
        try
        {
            string name = "GFX160-ALL-TEST-LOGS-" + report.exportId + ".zip";
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

    private int FindKernel(string name, uint expectedX)
    {
        if (!compute.HasKernel(name))
            throw new InvalidOperationException("Missing kernel: " + name);
        int kernel = compute.FindKernel(name);
        compute.GetKernelThreadGroupSizes(kernel, out uint x, out uint y, out uint z);
        if (x != expectedX || y != 1 || z != 1)
            throw new InvalidOperationException("Unexpected workgroup: " + name);
        return kernel;
    }

    private static void Seed(Vector2[] spectrum, int kx, int kz, double phase, double amplitude)
    {
        double scale = amplitude * Count / 2;
        var coefficient = new Vector2((float)(scale * Math.Cos(phase)), (float)(scale * Math.Sin(phase)));
        spectrum[kz * Side + kx] = coefficient;
        spectrum[(Side - kz) * Side + Side - kx] = new Vector2(coefficient.x, -coefficient.y);
    }

    private static RenderTexture CreateTarget()
    {
        return new RenderTexture(Side, Side, 0, RenderTextureFormat.RGFloat, RenderTextureReadWrite.Linear)
        {
            enableRandomWrite = true,
            filterMode = FilterMode.Point,
            useMipMap = false
        };
    }

    private void RunProbe()
    {
        if (!report.supportsCompute || !SystemInfo.SupportsRandomWriteOnRenderTextureFormat(RenderTextureFormat.RGFloat))
            throw new NotSupportedException("RGFloat storage images or compute shaders unavailable");
        int horizontal = FindKernel("Horizontal", 32);
        int vertical = FindKernel("Vertical", 32);
        int readback = FindKernel("Readback", 64);
        report.horizontalKernel = horizontal;
        report.verticalKernel = vertical;
        report.readbackKernel = readback;
        report.threadsX = 32;
        CreateSurface();

        var intermediate = CreateTarget();
        var output = CreateTarget();
        try
        {
            if (!intermediate.Create() || !output.Create())
                throw new InvalidOperationException("Storage image creation failed");
            report.intermediateFormat = intermediate.graphicsFormat.ToString();
            if (intermediate.graphicsFormat != UnityEngine.Experimental.Rendering.GraphicsFormat.R32G32_SFloat ||
                output.graphicsFormat != intermediate.graphicsFormat)
                throw new InvalidOperationException("Storage image format changed");
            var spectrum = new Vector2[Count];
            var values = new Vector2[Count];
            var previous = new float[Count];
            float[] times = { 0f, 0f, 0.75f, 1.5f };
            using (var input = new ComputeBuffer(Count, 8))
            using (var destination = new ComputeBuffer(Count, 8))
            {
                compute.SetBuffer(horizontal, "Spectrum", input);
                compute.SetTexture(horizontal, "Intermediate", intermediate);
                compute.SetTexture(vertical, "Intermediate", intermediate);
                compute.SetTexture(vertical, "OutputMap", output);
                compute.SetTexture(readback, "OutputMap", output);
                compute.SetBuffer(readback, "Heights", destination);
                for (int step = 0; step < times.Length; step++)
                {
                    float amplitude = step == 0 ? 0f : 1f;
                    float time = times[step];
                    Seed(spectrum, 2, 1, -1.9 * time, 0.43 * amplitude);
                    Seed(spectrum, 1, 3, -2.7 * time, 0.21 * amplitude);
                    input.SetData(spectrum);
                    for (int i = 0; i < Count; i++)
                        values[i] = new Vector2(float.NaN, float.NaN);
                    destination.SetData(values);
                    compute.Dispatch(horizontal, Side, 1, 1);
                    compute.Dispatch(vertical, Side, 1, 1);
                    compute.Dispatch(readback, Count / 64, 1, 1);
                    destination.GetData(values);
                    var result = new Result { time = time, amplitude = amplitude, samples = Count };
                    frames[step] = new float[Count];
                    for (int i = 0; i < Count; i++)
                    {
                        float value = values[i].x;
                        float imaginary = values[i].y;
                        frames[step][i] = value;
                        if (float.IsNaN(value) || float.IsInfinity(value) ||
                            float.IsNaN(imaginary) || float.IsInfinity(imaginary))
                        {
                            result.invalidSamples++;
                            continue;
                        }
                        int x = i % Side;
                        int z = i / Side;
                        double angle = 2 * Math.PI / Side;
                        double expected = amplitude * (0.43 * Math.Cos(angle * (2 * x + z) - 1.9 * time)
                            + 0.21 * Math.Cos(angle * (x + 3 * z) - 2.7 * time));
                        result.maximumError = Mathf.Max(result.maximumError, (float)Math.Abs(value - expected));
                        report.maxImaginary = Mathf.Max(report.maxImaginary, Mathf.Abs(imaginary));
                        result.maximumDelta = Mathf.Max(result.maximumDelta, Mathf.Abs(value - previous[i]));
                        previous[i] = value;
                        vertices[i].y = value;
                    }
                    result.passed = result.invalidSamples == 0 && result.maximumError <= Tolerance &&
                        (step == 0 || result.maximumDelta > 0.1f);
                    report.cases[step] = result;
                }
            }
        }
        finally
        {
            intermediate.Release();
            output.Release();
            Destroy(intermediate);
            Destroy(output);
        }

        report.passed = Array.TrueForAll(report.cases, item => item.passed) && report.maxImaginary <= Tolerance;
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

        mesh = new Mesh { name = "GFX160 analytic surface" };
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
        GUI.Label(new Rect(24, 16, Screen.width - 48, Screen.height / 4), "GFX160  " + status, label);
        if (zip != null && GUI.Button(new Rect(24, Screen.height - 100, 240, 64), "Retry ZIP export"))
        {
            try { Export(); }
            catch (Exception error) { status = "Export failed: " + error.Message; }
        }
    }
}
