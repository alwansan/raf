"""Stage a source-free OpenGLCore dispatch-address canary."""
import argparse
from pathlib import Path

from scripts.t1_sourcefree_unity_fixture import ASSET_FILE, ASSET_PATH, construct


_DISPATCH_COMPUTE = """// Authored dispatch-address control.
#pragma kernel T1Canary
StructuredBuffer<uint> Input;
RWStructuredBuffer<uint> Output;
static uint3 DispatchId;

struct EntryInput
{
    uint3 thread : SV_DispatchThreadID;
};

uint ViaGlobal()
{
    return Input[DispatchId.x];
}

uint ViaArgument(uint x)
{
    return Input[x];
}

[numthreads(64,1,1)]
void T1Canary(EntryInput input)
{
    DispatchId = input.thread;
    uint x = input.thread.x;
    Output[2 * x] = ViaGlobal();
    Output[2 * x + 1] = ViaArgument(x);
}
"""

_DISPATCH_ASSERTIONS = """        Assert.That(SystemInfo.graphicsDeviceType,
            Is.EqualTo(UnityEngine.Rendering.GraphicsDeviceType.OpenGLCore));
        var input = new uint[64];
        for (uint i = 0; i < 64; i++)
            input[i] = 17U + 13U * i;
        var output = new uint[128];
        using (var inputBuffer = new ComputeBuffer(input.Length, sizeof(uint)))
        using (var outputBuffer = new ComputeBuffer(output.Length, sizeof(uint)))
        {
            inputBuffer.SetData(input);
            outputBuffer.SetData(output);
            shader.SetBuffer(kernel, "Input", inputBuffer);
            shader.SetBuffer(kernel, "Output", outputBuffer);
            shader.Dispatch(kernel, 1, 1, 1);
            outputBuffer.GetData(output);
        }
        int viaGlobalMismatches = 0, viaArgumentMismatches = 0;
        for (int i = 0; i < input.Length; i++)
        {
            if (output[2 * i] != input[i]) viaGlobalMismatches++;
            if (output[2 * i + 1] != input[i]) viaArgumentMismatches++;
        }
        Assert.That(viaArgumentMismatches, Is.Zero, "Explicit argument address control");
        Assert.That(viaGlobalMismatches, Is.Zero, "Structured input via static global");
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    project = parser.parse_args().project
    construct(project)
    test = project / ASSET_PATH / ASSET_FILE
    source = test.read_text(encoding="utf-8")
    skip = "        if (!compute)\n            return; // Linux -nographics may expose a null graphics device."
    assertion = "        Assert.That(z, Is.EqualTo(1U));\n"
    if source.count(skip) != 1 or source.count(assertion) != 1:
        raise ValueError("Unexpected source-free fixture structure")
    test.write_text(source.replace(skip, "        Assert.That(compute, Is.True);")
                    .replace(assertion, assertion + _DISPATCH_ASSERTIONS), encoding="utf-8")
    (project / "Assets/T1Synthetic/FFTCanary.compute").write_text(_DISPATCH_COMPUTE, encoding="utf-8")


if __name__ == "__main__":
    main()
