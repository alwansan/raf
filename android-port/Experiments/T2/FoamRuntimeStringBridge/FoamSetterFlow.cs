// Conservative T2 original IL source-string→Unity SetTexture first-argument trace.
// This is a bounded single-basic-block proof of the *compiled call argument*,
// NOT runtime execution, texture-object content, material state or GPU pixels.
// Unknown flow, branch, dynamic/local alias beyond supported opcodes -> no proof.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamSetterFlow
{
    internal readonly record struct VerifiedCall(string SetterKind, string FirstArgRole,
                                                 int InstructionDistance);
    private enum Tag { Unknown, OriginalNameString, OriginalPropertyId }
    private const int MaxDistance = 16;

    private static int? LocalIndex(Instruction instruction)
    {
        string n=instruction.OpCode.Name;
        if (instruction.Operand is VariableDefinition variable)
            return variable.Index;
        for (int i=0;i<4;i++)
            if (n.EndsWith("." + i.ToString(),StringComparison.Ordinal))
                return i;
        return null;
    }

    private static bool IsExplicitBranch(Instruction instruction) =>
        instruction.OpCode.FlowControl is
            FlowControl.Branch or FlowControl.Cond_Branch or
            FlowControl.Return or FlowControl.Throw or FlowControl.Break;

    internal static VerifiedCall? Trace(MethodDefinition method, int literalIndex)
    {
        if (!method.HasBody)
            return null;
        var body=method.Body.Instructions;
        if (literalIndex<0 || literalIndex>=body.Count ||
            body[literalIndex].OpCode.Code!=Code.Ldstr)
            return null;
        var stack=new List<Tag>{Tag.OriginalNameString};
        var locals=new Dictionary<int,Tag>();
        void Ensure(int n)
        {
            while (stack.Count<n)
                stack.Insert(0,Tag.Unknown);
        }
        Tag Pop()
        {
            Ensure(1);
            Tag value=stack[stack.Count-1];
            stack.RemoveAt(stack.Count-1);
            return value;
        }
        for (int pos=literalIndex+1;
             pos<body.Count && pos<=literalIndex+MaxDistance;pos++)
        {
            Instruction instruction=body[pos];
            if (IsExplicitBranch(instruction))
                return null;
            string op=instruction.OpCode.Name;
            if (op=="nop")
                continue;
            if (op=="dup")
            {
                Ensure(1);
                stack.Add(stack[stack.Count-1]);
                continue;
            }
            if (op=="pop")
            {
                Pop();
                continue;
            }
            if (op.StartsWith("stloc",StringComparison.Ordinal))
            {
                int? idx=LocalIndex(instruction);
                if (idx is null || idx<0 || idx>65535)
                    return null;
                locals[idx.Value]=Pop();
                continue;
            }
            if (op.StartsWith("ldloca",StringComparison.Ordinal))
                return null;
            if (op.StartsWith("ldloc",StringComparison.Ordinal))
            {
                int? idx=LocalIndex(instruction);
                if (idx is null || idx<0 || idx>65535)
                    return null;
                stack.Add(locals.TryGetValue(idx.Value,out var value)
                    ? value : Tag.Unknown);
                continue;
            }
            if (op.StartsWith("ldarg",StringComparison.Ordinal) ||
                op.StartsWith("ldc.",StringComparison.Ordinal) ||
                op is "ldnull" or "ldsfld" or "ldstr" or "ldtoken")
            {
                stack.Add(Tag.Unknown);
                continue;
            }
            if (op=="ldfld")
            {
                Pop();
                stack.Add(Tag.Unknown);
                continue;
            }
            if (op=="stfld")
            {
                Pop();
                Pop();
                continue;
            }
            if (op=="stsfld" || op.StartsWith("starg",StringComparison.Ordinal))
            {
                Pop();
                continue;
            }
            if (instruction.OpCode.Code is Code.Call or Code.Callvirt)
            {
                if (instruction.Operand is not MethodReference methodRef)
                    return null;
                int pcount=methodRef.Parameters.Count;
                int total=pcount+(methodRef.HasThis?1:0);
                if (pcount>32 || total>33)
                    return null;
                Ensure(total);
                var args=new List<Tag>();
                for (int i=0;i<pcount;i++)
                    args.Add(stack[stack.Count-pcount+i]);
                // A *specific* string/PropertyToID-derived numeric ID must
                // occupy the first formal name argument in the actual call.
                string? setter=Program.SetterClass(instruction);
                if (setter is not null && pcount>=2)
                {
                    string firstType=methodRef.Parameters[0].ParameterType.FullName;
                    var tag=args[0];
                    if ((tag==Tag.OriginalNameString && firstType=="System.String") ||
                        (tag==Tag.OriginalPropertyId && firstType=="System.Int32"))
                        return new VerifiedCall(setter,
                            tag==Tag.OriginalNameString?"string":"property_id",
                            pos-literalIndex);
                }
                // Do not accept unrelated methods with the same name or
                // a marker that merely resides nearby on the evaluation stack.
                bool propertyId=methodRef.DeclaringType.FullName=="UnityEngine.Shader"
                                && methodRef.Name=="PropertyToID"
                                && pcount==1
                                && methodRef.Parameters[0].ParameterType.FullName=="System.String"
                                && args[0]==Tag.OriginalNameString
                                && !methodRef.HasThis
                                && methodRef.ReturnType.FullName=="System.Int32";
                for (int i=0;i<total;i++)
                    Pop();
                if (methodRef.ReturnType.FullName!="System.Void")
                    stack.Add(propertyId?Tag.OriginalPropertyId:Tag.Unknown);
                continue;
            }
            // Never fake argument dataflow for arithmetic, blocks, Phi-like
            // aliases, indirect calls, memory pointers or unknown opcodes.
            return null;
        }
        return null;
    }
}
