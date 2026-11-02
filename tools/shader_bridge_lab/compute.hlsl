// Original synthetic fixture authored solely for the shader translation lab.
// No Raft or third-party compiled game program appears in this file.
RWStructuredBuffer<uint> outputBuffer : register(u0);

[numthreads(8, 8, 1)]
void main(uint3 tid : SV_DispatchThreadID)
{
    uint index = tid.y * 8u + tid.x;
    outputBuffer[index] = tid.x + 17u * tid.y;
}
