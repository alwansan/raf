// Conservative T2 original IL source-string→Unity SetTexture first-argument trace.
// This is a bounded single-basic-block proof of the *compiled call argument*,
// NOT runtime execution, texture-object content, material state or GPU pixels.
// Unknown flow, branch, dynamic/local alias beyond supported opcodes -> no proof.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamSetterFlow
{
    internal readonly record struct VerifiedCall(string SetterKind, string FirstArgRole,
                                                 int InstructionDistance,
                                                 string SecondTextureOperandOrigin,
                                                 bool SecondFormalParameterIsUnityTexture,
                                                 string SecondProducerDeclaredReturnClass,
                                                 string SecondProducerDeclaringTypeClass,
                                                 bool SecondProducerIsCallvirt,
                                                 bool SecondProducerHasThis,
                                                 int SecondProducerParameterCount,
                                                 MethodReference? SecondProducerReference);
    private enum Tag {
        Unknown, OriginalNameString, OriginalPropertyId,
        ArgumentLoad, StaticFieldLoad, InstanceFieldLoad,
        NullLiteral, NumericLiteral, OtherStringLiteral, CallResult
    }
    private static string SecondOrigin(Tag tag) => tag switch {
        Tag.ArgumentLoad => "argument_load",
        Tag.StaticFieldLoad => "static_field_load",
        Tag.InstanceFieldLoad => "instance_field_load",
        Tag.NullLiteral => "null_literal",
        Tag.NumericLiteral => "numeric_literal",
        Tag.OtherStringLiteral => "other_string_literal",
        Tag.CallResult => "call_return",
        Tag.OriginalNameString => "source_name_string",
        Tag.OriginalPropertyId => "source_property_id",
        _ => "unknown",
    };
    private readonly record struct Value(Tag Tag, MethodReference? Producer,
                                         Code ProducerOpcode);
    private static Value V(Tag tag) => new(tag,null,Code.Nop);
    private static string ProducerReturnClass(Value value) {
        if (value.Tag!=Tag.CallResult || value.Producer is null) return "not_a_traced_producer_call";
        return value.Producer.ReturnType.FullName switch {
            "UnityEngine.Texture" => "unity_texture",
            "UnityEngine.Texture2D" => "unity_texture2d",
            "UnityEngine.RenderTexture" => "unity_rendertexture",
            "UnityEngine.Texture3D" => "unity_texture3d",
            "UnityEngine.Cubemap" => "unity_cubemap",
            "UnityEngine.Texture2DArray" => "unity_texture2darray",
            _ => "other_unverified_return_type",
        };
    }
    private static string ProducerDeclaringClass(Value value, ModuleDefinition module) {
        if (value.Tag!=Tag.CallResult || value.Producer is null) return "not_a_traced_producer_call";
        var type=value.Producer.DeclaringType;
        if (type.Namespace=="UnityEngine" ||
            type.Namespace.StartsWith("UnityEngine.",StringComparison.Ordinal))
            return "unityengine_declared";
        if (type.Scope==module || type.Module==module ||
            type.Scope?.Name=="Assembly-CSharp")
            return "original_managed_assembly_declared";
        return "other_external_or_unresolved_declaring_type";
    }
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
        var stack=new List<Value>{V(Tag.OriginalNameString)};
        var locals=new Dictionary<int,Value>();
        void Ensure(int n)
        {
            while (stack.Count<n)
                stack.Insert(0,V(Tag.Unknown));
        }
        Value Pop()
        {
            Ensure(1);
            Value value=stack[stack.Count-1];
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
                    ? value : V(Tag.Unknown));
                continue;
            }
            if (op.StartsWith("ldarg",StringComparison.Ordinal))
            {
                stack.Add(V(Tag.ArgumentLoad));
                continue;
            }
            if (op.StartsWith("ldc.",StringComparison.Ordinal) ||
                op=="ldtoken")
            {
                stack.Add(V(Tag.NumericLiteral));
                continue;
            }
            if (op=="ldnull")
            {
                stack.Add(V(Tag.NullLiteral));
                continue;
            }
            if (op=="ldsfld")
            {
                if (instruction.Operand is not FieldReference)
                    return null;
                stack.Add(V(Tag.StaticFieldLoad));
                continue;
            }
            if (op=="ldstr")
            {
                stack.Add(V(Tag.OtherStringLiteral));
                continue;
            }
            if (op=="ldfld")
            {
                if (instruction.Operand is not FieldReference)
                    return null;
                Pop();
                stack.Add(V(Tag.InstanceFieldLoad));
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
                var args=new List<Value>();
                for (int i=0;i<pcount;i++)
                    args.Add(stack[stack.Count-pcount+i]);
                // A *specific* string/PropertyToID-derived numeric ID must
                // occupy the first formal name argument in the actual call.
                string? setter=Program.SetterClass(instruction);
                if (setter is not null && pcount>=2)
                {
                    string firstType=methodRef.Parameters[0].ParameterType.FullName;
                    var tag=args[0].Tag;
                    if ((tag==Tag.OriginalNameString && firstType=="System.String") ||
                        (tag==Tag.OriginalPropertyId && firstType=="System.Int32"))
                    {
                        // This validates the actual parameter *declared type*.
                        // The second value's source is only the preceding IL
                        // opcode family; this is not proof of a runtime Texture
                        // instance or its source/pixel contents.
                        var second = args[1];
                        string declared = methodRef.Parameters[1].ParameterType.FullName;
                        return new VerifiedCall(setter,
                            tag==Tag.OriginalNameString?"string":"property_id",
                            pos-literalIndex,SecondOrigin(second.Tag),
                            declared=="UnityEngine.Texture",
                            ProducerReturnClass(second),
                            ProducerDeclaringClass(second,method.Module),
                            second.ProducerOpcode==Code.Callvirt,
                            second.Producer?.HasThis ?? false,
                            second.Producer?.Parameters.Count ?? 0,
                            second.Producer);
                    }
                }
                // Do not accept unrelated methods with the same name or
                // a marker that merely resides nearby on the evaluation stack.
                bool propertyId=methodRef.DeclaringType.FullName=="UnityEngine.Shader"
                                && methodRef.Name=="PropertyToID"
                                && pcount==1
                                && methodRef.Parameters[0].ParameterType.FullName=="System.String"
                                && args[0].Tag==Tag.OriginalNameString
                                && !methodRef.HasThis
                                && methodRef.ReturnType.FullName=="System.Int32";
                for (int i=0;i<total;i++)
                    Pop();
                if (methodRef.ReturnType.FullName!="System.Void")
                    stack.Add(propertyId?V(Tag.OriginalPropertyId):
                        new Value(Tag.CallResult,methodRef,instruction.OpCode.Code));
                continue;
            }
            // Never fake argument dataflow for arithmetic, blocks, Phi-like
            // aliases, indirect calls, memory pointers or unknown opcodes.
            return null;
        }
        return null;
    }
}
