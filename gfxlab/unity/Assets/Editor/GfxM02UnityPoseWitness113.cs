using System;
using System.IO;
using UnityEngine;

namespace RaftGraphicsLabEditor
{
    public static class GfxM02UnityPoseWitness113
    {
        [Serializable] private class Inputs { public Clip[] clips; }
        [Serializable] private class Clip
        {
            public float start, stop;
            public Node[] nodes;
            public int[] bones;
            public Binding[] bindings;
            public float[] constants;
            public Curve[] curves;
            public Matrix[] bindposes;
        }
        [Serializable] private class Node
        {
            public int parent;
            public Vector3 position, scale;
            public Quaternion rotation;
        }
        [Serializable] private class Binding { public int node, field, width; }
        [Serializable] private class Curve { public Key[] keys; }
        [Serializable] private class Key { public float time; public float[] coeff; }
        [Serializable] private class Matrix { public float[] values; }
        [Serializable] private class Report
        {
            public string experiment = "GFX113";
            public int poses, positions, failingVertices;
            public float maxAbsoluteError;
            public bool originalClipPlaybackVerified, nativeBakeMeshInvoked, phase_closed;
        }

        public static void Build()
        {
            string inputPath = Path.Combine(Application.dataPath, "../private-inputs");
            Inputs input = JsonUtility.FromJson<Inputs>(File.ReadAllText(Path.Combine(inputPath, "clips.json")));
            if (input.clips.Length != 3) throw new InvalidDataException("Expected three clips");
            Report report = new Report();
            for (int clipIndex = 0; clipIndex < input.clips.Length; clipIndex++)
            {
                Clip clip = input.clips[clipIndex];
                for (int step = 0; step < 5; step++)
                {
                    float time = (float)((double)clip.start + ((double)clip.stop - clip.start) * step / 4);
                    Matrix4x4[] palette = Evaluate(clip, time);
                    Compare(Path.Combine(inputPath, $"C{clipIndex}P{step}.bin"), palette, report);
                    report.poses++;
                }
            }
            if (report.poses != 15 || report.positions != 24990) throw new InvalidDataException("Pose coverage changed");
            string safe = JsonUtility.ToJson(report, true);
            File.WriteAllText(Path.Combine(Application.dataPath, "../gfx113-safe.json"), safe);
            Debug.Log("GFX113_SAFE " + JsonUtility.ToJson(report));
        }

        public static void BuildNativeBake()
        {
            string root = Path.Combine(Application.dataPath, "../private-inputs");
            Inputs input = JsonUtility.FromJson<Inputs>(File.ReadAllText(Path.Combine(root, "clips.json")));
            if (input.clips.Length != 3) throw new InvalidDataException("Expected three clips");
            var triangles = new int[2388 * 3];
            using (var indices = new BinaryReader(File.OpenRead(Path.Combine(root, "indices.bin"))))
            {
                for (int i = 0; i < triangles.Length; i++)
                    triangles[i] = indices.ReadUInt16();
                if (indices.BaseStream.Position != indices.BaseStream.Length)
                    throw new InvalidDataException("Unexpected source index data");
            }
            var report = new Report {experiment="GFX150", nativeBakeMeshInvoked=true};
            for (int c = 0; c < input.clips.Length; c++)
                BakeClip(input.clips[c], c, root, triangles, report);
            if (report.poses != 15 || report.positions != 24990)
                throw new InvalidDataException("Native pose coverage changed");
            File.WriteAllText(Path.Combine(Application.dataPath, "../gfx150-safe.json"), JsonUtility.ToJson(report,true));
            Debug.Log("GFX150_SAFE " + JsonUtility.ToJson(report));
        }

        private static void BakeClip(Clip clip, int clipIndex, string root, int[] triangles, Report report)
        {
            var holder = new GameObject("GfxBakeRoot");
            var mesh = new Mesh();
            var baked = new Mesh();
            try
            {
                var transforms = new Transform[clip.nodes.Length];
                for (int i = 0; i < transforms.Length; i++)
                {
                    transforms[i] = new GameObject("Node").transform;
                    int parent = clip.nodes[i].parent;
                    transforms[i].SetParent(parent < 0 ? holder.transform : transforms[parent], false);
                }
                var bones = new Transform[clip.bones.Length];
                var bindposes = new Matrix4x4[bones.Length];
                for (int i = 0; i < bones.Length; i++)
                {
                    bones[i] = transforms[clip.bones[i]];
                    for (int row = 0; row < 4; row++)
                        for (int col = 0; col < 4; col++)
                            bindposes[i][row, col] = clip.bindposes[i].values[4 * row + col];
                }
                var renderer = holder.AddComponent<SkinnedMeshRenderer>();
                renderer.bones = bones;
                renderer.quality = SkinQuality.Bone4;
                renderer.updateWhenOffscreen = true;
                for (int step = 0; step < 5; step++)
                {
                    string path = Path.Combine(root, $"C{clipIndex}P{step}.bin");
                    var reference = new Vector3[1666];
                    using (var reader = new BinaryReader(File.OpenRead(path)))
                    {
                        if (reader.ReadUInt32() != 0x39303147 || reader.ReadInt32() != reference.Length ||
                            reader.ReadInt32() != bones.Length) throw new InvalidDataException("Wrong source pose");
                        reader.BaseStream.Seek(bones.Length * 64, SeekOrigin.Current);
                        var positions = new Vector3[reference.Length];
                        var weights = new BoneWeight[reference.Length];
                        for (int i = 0; i < positions.Length; i++)
                        {
                            positions[i] = ReadVector(reader);
                            weights[i] = new BoneWeight {
                                weight0=reader.ReadSingle(), weight1=reader.ReadSingle(),
                                weight2=reader.ReadSingle(), weight3=reader.ReadSingle(),
                                boneIndex0=reader.ReadInt32(), boneIndex1=reader.ReadInt32(),
                                boneIndex2=reader.ReadInt32(), boneIndex3=reader.ReadInt32()
                            };
                            reference[i] = ReadVector(reader);
                        }
                        mesh.vertices = positions;
                        mesh.triangles = triangles;
                        mesh.bindposes = bindposes;
                        mesh.boneWeights = weights;
                    }
                    renderer.sharedMesh = mesh;
                    float time = (float)((double)clip.start + ((double)clip.stop - clip.start) * step / 4);
                    Evaluate(clip, time, transforms);
                    renderer.BakeMesh(baked);
                    Vector3[] actual = baked.vertices;
                    if (actual.Length != reference.Length) throw new InvalidDataException("Native vertex count differs");
                    for (int i = 0; i < actual.Length; i++)
                    {
                        bool passed = true;
                        for (int axis = 0; axis < 3; axis++)
                        {
                            float delta = Mathf.Abs(actual[i][axis] - reference[i][axis]);
                            if (float.IsNaN(delta) || float.IsInfinity(delta))
                                throw new InvalidDataException("Nonfinite native skin position");
                            report.maxAbsoluteError = Mathf.Max(report.maxAbsoluteError, delta);
                            passed &= delta <= 0.0001f + 0.000001f * Mathf.Abs(reference[i][axis]);
                        }
                        if (!passed) report.failingVertices++;
                        report.positions++;
                    }
                    report.poses++;
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(holder);
                UnityEngine.Object.DestroyImmediate(baked);
                UnityEngine.Object.DestroyImmediate(mesh);
            }
        }

        private static Vector3 ReadVector(BinaryReader reader)
        {
            return new Vector3(reader.ReadSingle(), reader.ReadSingle(), reader.ReadSingle());
        }

        private static float EvaluateCurve(Curve curve, float time)
        {
            Key[] keys = curve.keys;
            int index = keys.Length - 1;
            while (index >= 0 && keys[index].time > time) index--;
            if (index < 0) throw new InvalidDataException("Missing curve predecessor");
            Key key = keys[index];
            float[] c = key.coeff;
            if (index + 1 == keys.Length || time == key.time) return c[3];
            float width = keys[index + 1].time - key.time;
            float end = ((c[0] * width + c[1]) * width + c[2]) * width + c[3];
            float endSlope = (3 * c[0] * width + 2 * c[1]) * width + c[2];
            // Build one Hermite segment so a discontinuity at the next source key is preserved.
            AnimationCurve hermite = new AnimationCurve(new Keyframe(0, c[3], c[2], c[2]),
                new Keyframe(width, end, endSlope, endSlope));
            return hermite.Evaluate(time - key.time);
        }

        private static Matrix4x4[] Evaluate(Clip clip, float time, Transform[] transforms = null)
        {
            var positions = new Vector3[clip.nodes.Length];
            var rotations = new Quaternion[clip.nodes.Length];
            var scales = new Vector3[clip.nodes.Length];
            for (int i = 0; i < clip.nodes.Length; i++)
            {
                positions[i] = clip.nodes[i].position;
                rotations[i] = clip.nodes[i].rotation;
                scales[i] = clip.nodes[i].scale;
            }
            int cursor = 0;
            foreach (Binding binding in clip.bindings)
            {
                float[] values = new float[binding.width];
                for (int i = 0; i < values.Length; i++, cursor++)
                    values[i] = cursor < clip.curves.Length ? EvaluateCurve(clip.curves[cursor], time)
                        : clip.constants[cursor - clip.curves.Length];
                var xyz = new Vector3(values[0], values[1], values[2]);
                if (binding.field == 0) positions[binding.node] = xyz;
                else if (binding.field == 1) rotations[binding.node] = new Quaternion(xyz.x, xyz.y, xyz.z, values[3]).normalized;
                else scales[binding.node] = xyz;
            }
            var world = new Matrix4x4[clip.nodes.Length];
            for (int i = 0; i < world.Length; i++)
            {
                Matrix4x4 local = Matrix4x4.TRS(positions[i], rotations[i], scales[i]);
                if (transforms != null)
                {
                    transforms[i].localPosition = positions[i];
                    transforms[i].localRotation = rotations[i];
                    transforms[i].localScale = scales[i];
                }
                int parent = clip.nodes[i].parent;
                world[i] = parent < 0 ? local : world[parent] * local;
            }
            var palette = new Matrix4x4[clip.bones.Length];
            for (int bone = 0; bone < palette.Length; bone++)
            {
                Matrix4x4 bind = new Matrix4x4();
                for (int row = 0; row < 4; row++)
                    for (int col = 0; col < 4; col++) bind[row, col] = clip.bindposes[bone].values[4 * row + col];
                palette[bone] = world[clip.bones[bone]] * bind;
            }
            return palette;
        }

        private static void Compare(string path, Matrix4x4[] palette, Report report)
        {
            using (var reader = new BinaryReader(File.OpenRead(path)))
            {
                if (reader.ReadUInt32() != 0x39303147 || reader.ReadInt32() != 1666
                    || reader.ReadInt32() != palette.Length) throw new InvalidDataException("Wrong payload shape");
                reader.BaseStream.Seek(palette.Length * 64, SeekOrigin.Current);
                var weights = new float[4];
                var indices = new int[4];
                for (int vertex = 0; vertex < 1666; vertex++)
                {
                    var position = new Vector3(reader.ReadSingle(), reader.ReadSingle(), reader.ReadSingle());
                    for (int i = 0; i < 4; i++) weights[i] = reader.ReadSingle();
                    for (int i = 0; i < 4; i++) indices[i] = reader.ReadInt32();
                    var actual = Vector3.zero;
                    for (int i = 0; i < 4; i++)
                        if (weights[i] > 0) actual += weights[i] * palette[indices[i]].MultiplyPoint(position);
                    bool passed = true;
                    for (int axis = 0; axis < 3; axis++)
                    {
                        float expected = reader.ReadSingle();
                        float error = Mathf.Abs(actual[axis] - expected);
                        if (float.IsNaN(error) || float.IsInfinity(error)) throw new InvalidDataException("Nonfinite Unity pose");
                        report.maxAbsoluteError = Mathf.Max(report.maxAbsoluteError, error);
                        passed &= error <= 0.0001f + 0.000001f * Mathf.Abs(expected);
                    }
                    if (!passed) report.failingVertices++;
                    report.positions++;
                }
            }
        }
    }
}
