using UnityEngine;
// Separate authored serialization probe, not the original water MonoBehaviour.
public sealed class GTFFTReferenceWitness : ScriptableObject
{
    public ComputeShader[] selected;
    public ComputeShader[] absent;
}
