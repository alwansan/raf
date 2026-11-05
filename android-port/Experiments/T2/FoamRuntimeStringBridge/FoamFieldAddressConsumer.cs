// T2 WATER-001: bounded original backing-field address-consumer classification.
// Original symbols and IL remain in the SHA-pinned private CI runner.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamFieldAddressConsumer
{
    internal sealed record SafeProfile(
        int ExactFieldAddressSites,
        int DistinctAddressSiteMethods,
        Dictionary<string,int> SinkCategories,
        Dictionary<string,int> FirstFollowingOpCategories,
        bool OriginalRuntimeExecutionVerified,
        bool OriginalRuntimeArrayContentsVerified);

    private enum Tag { Other, ExactFieldAddress, ExactFieldArrayValue }

    private static bool SameExactField(FieldReference a, FieldReference b) =>
        a.FullName==b.FullName &&
        a.DeclaringType.FullName==b.DeclaringType.FullName &&
        a.FieldType.FullName==b.FieldType.FullName;

    private static bool IsOriginalRenderTextureArray(TypeReference type) =>
        type is ArrayType array && array.Rank==1 &&
        array.ElementType.FullName=="UnityEngine.RenderTexture";

    private static int? LocalIndex(Instruction instruction)
    {
        if (instruction.Operand is VariableDefinition v)
            return v.Index;
        for (int i=0;i<4;i++)
            if (instruction.OpCode.Name.EndsWith("."+i,StringComparison.Ordinal))
                return i;
        return null;
    }

    private static string FirstOp(Instruction instruction) =>
        instruction.OpCode.Code switch
        {
            Code.Call or Code.Callvirt => "call",
            Code.Ldind_Ref or Code.Ldobj => "indirect_load",
            Code.Stind_Ref or Code.Stobj => "indirect_store",
            Code.Initobj => "initobj",
            Code.Ldlen => "array_length",
            Code.Newarr => "new_array",
            Code.Dup => "duplicate",
            _ when instruction.OpCode.Name.StartsWith("ldc.",StringComparison.Ordinal) =>
                "constant_load",
            _ when instruction.OpCode.Name.StartsWith("ldloc",StringComparison.Ordinal) =>
                "local_load",
            _ => "other"
        };

    // Trace the exact address after its ldflda; everything originally on the
    // evaluation stack below that address is Other. No branch join is guessed.
    private static (string Sink,string First) Trace(MethodDefinition method, int site,
        Action<MethodReference>? onTypedRecipient = null)
    {
        var ops=method.Body.Instructions;
        var stack=new List<Tag>{Tag.ExactFieldAddress};
        var locals=new Dictionary<int,Tag>();
        static Tag Pop(List<Tag> s)
        {
            if (s.Count==0) return Tag.Other;
            var value=s[^1];
            s.RemoveAt(s.Count-1);
            return value;
        }
        string first="none";
        for (int pos=site+1;pos<ops.Count && pos<=site+40;pos++)
        {
            var instruction=ops[pos];
            var code=instruction.OpCode.Code;
            if (code==Code.Nop)
                continue;
            if (first=="none")
                first=FirstOp(instruction);
            if (instruction.OpCode.FlowControl is FlowControl.Branch or
                    FlowControl.Cond_Branch or FlowControl.Return or
                    FlowControl.Throw or FlowControl.Break)
                return ("control_flow_or_return_before_proven_sink",first);
            if (code==Code.Dup)
            {
                stack.Add(stack.Count>0?stack[^1]:Tag.Other);
                continue;
            }
            if (code==Code.Pop)
            {
                var value=Pop(stack);
                if (value==Tag.ExactFieldAddress)
                    return ("address_discarded",first);
                if (value==Tag.ExactFieldArrayValue)
                    return ("array_value_discarded",first);
                continue;
            }
            var op=instruction.OpCode.Name;
            if (op.StartsWith("stloc",StringComparison.Ordinal))
            {
                int? index=LocalIndex(instruction);
                if (index is null) return ("unsupported_local_alias",first);
                locals[index.Value]=Pop(stack);
                continue;
            }
            if (op.StartsWith("ldloca",StringComparison.Ordinal))
            {
                stack.Add(Tag.Other);
                continue;
            }
            if (op.StartsWith("ldloc",StringComparison.Ordinal))
            {
                int? index=LocalIndex(instruction);
                if (index is null) return ("unsupported_local_alias",first);
                stack.Add(locals.GetValueOrDefault(index.Value,Tag.Other));
                continue;
            }
            if (op.StartsWith("ldarg",StringComparison.Ordinal) ||
                op.StartsWith("ldc.",StringComparison.Ordinal) ||
                code is Code.Ldnull or Code.Ldstr or Code.Ldtoken or Code.Ldsfld)
            {
                stack.Add(Tag.Other);
                continue;
            }
            if (code==Code.Ldind_Ref || code==Code.Ldobj)
            {
                Tag address=Pop(stack);
                if (address==Tag.ExactFieldAddress)
                {
                    if (code==Code.Ldobj &&
                        instruction.Operand is TypeReference elementType &&
                        !IsOriginalRenderTextureArray(elementType))
                        return ("typed_indirect_load_mismatch",first);
                    stack.Add(Tag.ExactFieldArrayValue);
                }
                else
                    stack.Add(Tag.Other);
                continue;
            }
            if (code==Code.Initobj)
            {
                var pointer=Pop(stack);
                return (pointer==Tag.ExactFieldAddress &&
                        instruction.Operand is TypeReference t &&
                        IsOriginalRenderTextureArray(t)
                    ? "direct_field_clear_initobj"
                    : "unproven_initobj_target",first);
            }
            if (code==Code.Stind_Ref || code==Code.Stobj)
            {
                var value=Pop(stack);
                var dest=Pop(stack);
                if (dest==Tag.ExactFieldAddress)
                {
                    if (code==Code.Stobj &&
                        (instruction.Operand is not TypeReference t ||
                        !IsOriginalRenderTextureArray(t)))
                        return ("typed_indirect_store_mismatch",first);
                    return ("direct_field_reference_store",first);
                }
                if (value==Tag.ExactFieldAddress)
                    return ("address_escape_to_another_store",first);
                continue;
            }
            if (code==Code.Cpobj)
            {
                var src=Pop(stack);
                var dest=Pop(stack);
                if (dest==Tag.ExactFieldAddress)
                    return ("direct_field_copy_to_address",first);
                if (src==Tag.ExactFieldAddress)
                    return ("address_used_as_copy_source",first);
                continue;
            }
            if (code==Code.Ldlen)
            {
                var array=Pop(stack);
                if (array==Tag.ExactFieldArrayValue)
                    return ("array_length_read_via_address",first);
                stack.Add(Tag.Other);
                continue;
            }
            if (code==Code.Ldelem_Ref || code==Code.Ldelema)
            {
                Pop(stack); // index
                var array=Pop(stack);
                if (array==Tag.ExactFieldArrayValue)
                    return (code==Code.Ldelema?
                        "array_element_address_taken_via_field":
                        "array_element_read_via_field",first);
                stack.Add(Tag.Other);
                continue;
            }
            if (code==Code.Stelem_Ref)
            {
                Pop(stack); // value
                Pop(stack); // index
                var array=Pop(stack);
                if (array==Tag.ExactFieldArrayValue)
                    return ("direct_array_element_store_via_field",first);
                continue;
            }
            if (code==Code.Newarr)
            {
                Pop(stack);
                stack.Add(Tag.Other);
                continue;
            }
            if (code is Code.Call or Code.Callvirt)
            {
                if (instruction.Operand is not MethodReference called)
                    return ("unknown_call_operand",first);
                int parameters=called.Parameters.Count;
                int total=parameters+(called.HasThis?1:0);
                if (total>33)
                    return ("call_argument_budget",first);
                while (stack.Count<total)
                    stack.Insert(0,Tag.Other);
                int start=stack.Count-total;
                for (int i=0;i<parameters;i++)
                {
                    Tag arg=stack[start+(called.HasThis?1:0)+i];
                    if (arg==Tag.ExactFieldAddress)
                    {
                        if (called.Parameters[i].ParameterType is ByReferenceType br &&
                            IsOriginalRenderTextureArray(br.ElementType))
                        {
                            onTypedRecipient?.Invoke(called);
                            return ("typed_byref_array_call_potential_mutation",first);
                        }
                        return ("address_escaped_to_other_call_argument",first);
                    }
                    if (arg==Tag.ExactFieldArrayValue)
                        return ("array_value_passed_to_call_contents_unknown",first);
                }
                if (called.HasThis && stack[start]==Tag.ExactFieldAddress)
                    return ("address_used_as_call_receiver",first);
                stack.RemoveRange(start,total);
                if (called.ReturnType.FullName!="System.Void")
                    stack.Add(Tag.Other);
                continue;
            }
            if (code==Code.Ldfld)
            {
                var instance=Pop(stack);
                if (instance==Tag.ExactFieldAddress)
                    return ("address_used_as_instance_field_receiver",first);
                stack.Add(Tag.Other);
                continue;
            }
            if (code==Code.Stfld)
            {
                var value=Pop(stack);
                var instance=Pop(stack);
                if (value==Tag.ExactFieldAddress || instance==Tag.ExactFieldAddress)
                    return ("address_escaped_via_instance_store",first);
                if (value==Tag.ExactFieldArrayValue)
                    return ("array_value_stored_in_another_field",first);
                continue;
            }
            return ("unsupported_opcode_before_proven_sink",first);
        }
        return ("bounded_without_proven_sink",first);
    }

    internal static SafeProfile Scan(IEnumerable<MethodDefinition> methods,
                                    FieldReference field,
                                    Action<MethodReference>? onTypedRecipient = null)
    {
        if (methods is null || field is null ||
            !IsOriginalRenderTextureArray(field.FieldType))
            throw new InvalidDataException("Original exact RenderTexture[] field required");
        var sinks=new Dictionary<string,int>(StringComparer.Ordinal);
        var firsts=new Dictionary<string,int>(StringComparer.Ordinal);
        var owners=new HashSet<MethodDefinition>();
        int total=0;
        foreach (var method in methods)
        {
            if (method is null || !method.HasBody) continue;
            var ops=method.Body.Instructions;
            for (int i=0;i<ops.Count;i++)
            {
                if (ops[i].OpCode.Code!=Code.Ldflda ||
                    ops[i].Operand is not FieldReference actual ||
                    !SameExactField(actual,field))
                    continue;
                total++;
                owners.Add(method);
                var (sink,first)=Trace(method,i,onTypedRecipient);
                sinks[sink]=sinks.GetValueOrDefault(sink)+1;
                firsts[first]=firsts.GetValueOrDefault(first)+1;
                if (total>10000) throw new InvalidDataException("Excess address sites");
            }
        }
        if (sinks.Values.Sum()!=total || firsts.Values.Sum()!=total)
            throw new InvalidDataException("Field address consumer classification mismatch");
        return new SafeProfile(total,owners.Count,sinks,firsts,false,false);
    }
}
