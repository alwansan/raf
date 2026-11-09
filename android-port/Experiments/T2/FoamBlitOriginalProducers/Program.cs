// T2 WATER-001: conservative ORIGINAL managed CIL Foam Blit provenance.
// Never print source names, fields, method tokens, IL, resources or private paths.
// Typed argument roles != texture instance/ShaderLab/Unity/Adreno evidence.
using Mono.Cecil;
using Mono.Cecil.Cil;
using System.Security.Cryptography;
using System.Text.Json;

internal static class Program
{
    const string Shader = "UnityEngine.Shader";
    const string Material = "UnityEngine.Material";
    const string Texture = "UnityEngine.Texture";
    const string RenderTexture = "UnityEngine.RenderTexture";
    const int MaxTrace = 48;
    record Site(string Source, string Destination, string SourceProducer, string DestinationProducer);
    record Producer(string Type, string Kind);

    static IEnumerable<TypeDefinition> Descend(TypeDefinition t)
    {
        yield return t;
        foreach (var n in t.NestedTypes)
            foreach (var x in Descend(n)) yield return x;
    }
    static IEnumerable<MethodDefinition> Methods(AssemblyDefinition asm) =>
        asm.Modules.SelectMany(m => m.Types.SelectMany(Descend))
            .SelectMany(t => t.Methods).Where(m => m.HasBody);

    static bool FindShader(Instruction i) =>
        i.OpCode.Code == Code.Call && i.Operand is MethodReference m &&
        m.DeclaringType.FullName == Shader && m.Name == "Find" &&
        !m.HasThis && m.ReturnType.FullName == Shader &&
        m.Parameters.Count == 1 && m.Parameters[0].ParameterType.FullName == "System.String";
    static bool Blit(Instruction i) =>
        i.OpCode.Code == Code.Call && i.Operand is MethodReference m &&
        m.DeclaringType.FullName == "UnityEngine.Graphics" && m.Name == "Blit" &&
        !m.HasThis && m.ReturnType.FullName == "System.Void" &&
        m.Parameters.Count == 4 &&
        m.Parameters[0].ParameterType.FullName == Texture &&
        m.Parameters[1].ParameterType.FullName == RenderTexture &&
        m.Parameters[2].ParameterType.FullName == Material &&
        m.Parameters[3].ParameterType.FullName == "System.Int32";

    static int Previous(IList<Instruction> il, int index)
    {
        int n=0;
        while(index>=0 && il[index].OpCode.Code==Code.Nop && n++<4) index--;
        return index>=0 && il[index].OpCode.Code!=Code.Nop ? index : -1;
    }
    static int Next(IList<Instruction> il, int index)
    {
        int n=0;
        while(index<il.Count && il[index].OpCode.Code==Code.Nop && n++<4) index++;
        return index<il.Count && il[index].OpCode.Code!=Code.Nop ? index : -1;
    }
    static int? Literal(Instruction i) => i.OpCode.Code switch
    {
        Code.Ldc_I4_0 => 0, Code.Ldc_I4_1 => 1, Code.Ldc_I4_2 => 2,
        Code.Ldc_I4_M1 => -1, Code.Ldc_I4_3 => 3, Code.Ldc_I4_4 => 4,
        Code.Ldc_I4_5 => 5, Code.Ldc_I4_6 => 6, Code.Ldc_I4_7 => 7,
        Code.Ldc_I4_8 => 8, Code.Ldc_I4_S when i.Operand is sbyte n => n,
        Code.Ldc_I4 when i.Operand is int n => n,
        _ => null
    };
    static int LocalIndex(Instruction i, bool store)
    {
        if(store)
        {
            return i.OpCode.Code switch
            {
                Code.Stloc_0=>0,Code.Stloc_1=>1,Code.Stloc_2=>2,Code.Stloc_3=>3,
                Code.Stloc or Code.Stloc_S when i.Operand is VariableDefinition v => v.Index,
                _=>-1
            };
        }
        return i.OpCode.Code switch
        {
            Code.Ldloc_0=>0,Code.Ldloc_1=>1,Code.Ldloc_2=>2,Code.Ldloc_3=>3,
            Code.Ldloc or Code.Ldloc_S when i.Operand is VariableDefinition v => v.Index,
            _=>-1
        };
    }
    static bool SameField(Instruction i, FieldDefinition field, bool reading)
    {
        if(i.OpCode.Code is not (Code.Ldfld or Code.Ldsfld or Code.Stfld or Code.Stsfld) ||
           (reading && i.OpCode.Code is not (Code.Ldfld or Code.Ldsfld)) ||
           (!reading && i.OpCode.Code is not (Code.Stfld or Code.Stsfld)) ||
           i.Operand is not FieldReference reference ||
           reference.FieldType.FullName != field.FieldType.FullName) return false;
        try
        {
            var resolved = reference.Resolve();
            return resolved is not null && resolved.Module==field.Module &&
                resolved.MetadataToken==field.MetadataToken;
        }
        catch(AssemblyResolutionException) {return false;}
        catch(ResolutionException) {return false;}
    }
    static bool Receiver(Instruction i) =>
        i.OpCode.Code is Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3
        or Code.Ldarg or Code.Ldarg_S or Code.Ldloc_0 or Code.Ldloc_1
        or Code.Ldloc_2 or Code.Ldloc_3 or Code.Ldloc or Code.Ldloc_S
        or Code.Ldsfld;

    static bool MaterialCtor(Instruction i) =>
        i.OpCode.Code==Code.Newobj && i.Operand is MethodReference m &&
        m.Name==".ctor" && m.DeclaringType.FullName==Material && m.HasThis &&
        m.Parameters.Count==1 && m.Parameters[0].ParameterType.FullName==Shader;

    static int FixedStackCount(string name, string prefix)
    {
        if(name==prefix+"0") return 0;
        if(!name.StartsWith(prefix,StringComparison.Ordinal)) return -1;
        if(name==prefix+"1" || name==prefix+"i" || name==prefix+"ref"
            || name==prefix+"r4" || name==prefix+"r8") return 1;
        // Cecil enums include Pop1_pop1 / Popref_popi_pop1 etc.
        if(name.Contains('_')) return name.Split('_').Length;
        return -1;
    }
    static FieldDefinition? MaterialFieldFromCtor(MethodDefinition method, int ctor)
    {
        var il=method.Body.Instructions;
        var stack=new List<bool>{true};
        var locals=new Dictionary<int,bool>();
        var fields=new HashSet<FieldDefinition>();
        bool Pop()
        {
            if(stack.Count==0)return false; // unknown pre-ctor receiver, never tainted
            var b=stack[^1];stack.RemoveAt(stack.Count-1);return b;
        }
        for(int i=ctor+1;i<il.Count && i<=ctor+MaxTrace;i++)
        {
            var x=il[i];
            if(x.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw)break;
            if(x.OpCode.Code==Code.Nop)continue;
            if(x.OpCode.Code==Code.Dup)
            {
                if(stack.Count==0)break;
                stack.Add(stack[^1]);continue;
            }
            int store=LocalIndex(x,true),load=LocalIndex(x,false);
            if(store>=0)
            {
                locals[store]=Pop() && store<method.Body.Variables.Count &&
                    method.Body.Variables[store].VariableType.FullName==Material;
                continue;
            }
            if(load>=0)
            {
                stack.Add(locals.GetValueOrDefault(load,false));continue;
            }
            if(x.OpCode.Code is Code.Stfld or Code.Stsfld)
            {
                bool isMaterial=Pop();
                if(x.OpCode.Code==Code.Stfld)Pop();
                if(isMaterial && x.Operand is FieldReference reference &&
                   reference.FieldType.FullName==Material)
                {
                    try
                    {
                        var f=reference.Resolve();
                        if(f is not null && f.Module==method.Module &&
                           f.FieldType.FullName==Material)fields.Add(f);
                    }
                    catch(AssemblyResolutionException) {}
                    catch(ResolutionException) {}
                }
                continue;
            }
            if(x.OpCode.Code is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if(x.Operand is not MethodReference call || call.Parameters.Count>16)break;
                int pop=call.Parameters.Count+(x.OpCode.Code!=Code.Newobj && call.HasThis?1:0);
                for(int n=0;n<pop;n++)Pop();
                if(x.OpCode.Code==Code.Newobj || call.ReturnType.FullName!="System.Void")
                    stack.Add(false);
                continue;
            }
            if(x.OpCode.Code==Code.Pop){Pop();continue;}
            int pops=FixedStackCount(x.OpCode.StackBehaviourPop.ToString(),"Pop");
            int pushes=FixedStackCount(x.OpCode.StackBehaviourPush.ToString(),"Push");
            if(pops<0||pushes<0||pops>5||pushes>2)break;
            for(int n=0;n<pops;n++)Pop();
            for(int n=0;n<pushes;n++)stack.Add(false);
            if(stack.Count>32)break;
        }
        return fields.Count==1 ? fields.Single():null;
    }
    static bool UnsafeFlow(MethodDefinition method, int start, int end)
    {
        if(start<0 || end>=method.Body.Instructions.Count || start>end ||
           method.Body.HasExceptionHandlers)return true;
        var il=method.Body.Instructions;
        var region=new HashSet<Instruction>(il.Skip(start).Take(end-start+1));
        for(int i=0;i<il.Count;i++)
        {
            var x=il[i];
            if(i>=start && i<=end && x.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw)return true;
            if(i>=start && i<=end)continue;
            if(x.Operand is Instruction target && region.Contains(target))return true;
            if(x.Operand is Instruction[] targets && targets.Any(region.Contains))return true;
        }
        return false;
    }
    static Producer TypedValue(MethodDefinition m, IList<Instruction> il, ref int at)
    {
        at=Previous(il,at);
        if(at<0)return new("unknown","unknown");
        var i=il[at];
        if(i.OpCode.Code==Code.Ldnull){at--;return new("null","literal_null");}
        int loc=LocalIndex(i,false);
        if(loc>=0)
        {
            at--;
            return loc<m.Body.Variables.Count
                ? new(m.Body.Variables[loc].VariableType.FullName,"typed_local")
                : new("unknown","unknown");
        }
        if((i.OpCode.Code is Code.Ldsfld or Code.Ldfld) &&
           i.Operand is FieldReference f)
        {
            // A typed field proves only a declared TYPE, not texture instance identity.
            string type=f.FieldType.FullName;
            at--;
            if(i.OpCode.Code==Code.Ldfld)
            {
                at=Previous(il,at);
                if(at<0 || !Receiver(il[at]))return new("unknown","unknown");
                at--;
            }
            return new(type,"typed_field");
        }
        // Require exact public type from method argument definition.
        int arg=i.OpCode.Code switch
        {
            Code.Ldarg_0=>0,Code.Ldarg_1=>1,Code.Ldarg_2=>2,Code.Ldarg_3=>3,
            Code.Ldarg or Code.Ldarg_S when i.Operand is ParameterDefinition p=>
                p.Index + (m.HasThis ? 1 : 0),
            _=>-1
        };
        if(arg>=0)
        {
            at--;
            int idx=arg-(m.HasThis?1:0);
            if(idx>=0 && idx<m.Parameters.Count)
                return new(m.Parameters[idx].ParameterType.FullName,"typed_argument");
        }
        return new("unknown","unknown");
    }
    static bool DirectMaterialBlit(MethodDefinition m,int callIndex,FieldDefinition field)
    {
        var il=m.Body.Instructions;
        int p=Previous(il,callIndex-1);
        if(p<0 || Literal(il[p]) is not (0 or 1))return false;
        int material=Previous(il,p-1);
        if(material<0 || !SameField(il[material],field,true))return false;
        int start=material;
        if(il[material].OpCode.Code==Code.Ldfld)
        {
            start=Previous(il,material-1);
            if(start<0 || !Receiver(il[start]))return false;
        }
        return !UnsafeFlow(m,start,callIndex);
    }
    static bool OriginalMaterialLocalAliasBlit(MethodDefinition m,int callIndex,FieldDefinition field)
    {
        var il=m.Body.Instructions;
        int p=Previous(il,callIndex-1);
        if(p<0 || Literal(il[p]) is not (0 or 1))return false;
        int load=Previous(il,p-1);
        if(load<0)return false;
        int idx=LocalIndex(il[load],false);
        if(idx<0 || idx>=m.Body.Variables.Count ||
           m.Body.Variables[idx].VariableType.FullName!=Material)return false;
        // A bounded same-block, definite nearest store from the exact Foam
        // Material field is required. No other prior/stale local write is
        // accepted, and any branch into the region fails closed.
        for(int store=load-1;store>=0 && load-store<=MaxTrace;store--)
        {
            if(LocalIndex(il[store],true)!=idx)continue;
            int value=Previous(il,store-1);
            if(value<0 || !SameField(il[value],field,true))return false;
            int start=value;
            if(il[value].OpCode.Code==Code.Ldfld)
            {
                start=Previous(il,value-1);
                if(start<0 || !Receiver(il[start]))return false;
            }
            return !UnsafeFlow(m,start,callIndex);
        }
        return false;
    }
    static string FirstUnresolvedImageOperand(MethodDefinition method,int callIndex,FieldDefinition field)
    {
        // Report ONLY one of five source-free reason tags, never raw CIL.
        var il=method.Body.Instructions;
        if(!DirectMaterialBlit(method,callIndex,field))return "material_not_direct";
        int p=Previous(il,callIndex-1);
        int material=Previous(il,p-1);
        int at=material-1;
        if(il[material].OpCode.Code==Code.Ldfld)
        {
            at=Previous(il,at);
            if(at<0 || !Receiver(il[at]))return "material_not_direct";
            at--;
        }
        var dst=TypedValue(method,il,ref at);
        if(dst.Type is not (RenderTexture or "null"))return "destination_not_direct";
        var src=TypedValue(method,il,ref at);
        if(src.Type is not (Texture or RenderTexture))return "source_not_direct";
        int start=Previous(il,at+1);
        if(start<0 || UnsafeFlow(method,start,callIndex))return "control_flow";
        return "none";
    }
    private sealed record StackSourceTrace(string Role,string Kind,string Reason,int Steps,int VoidCalls,
        Instruction? SourceInstruction);

    static StackSourceTrace BacktraceBlitSource(MethodDefinition method,int blitIndex)
    {
        // Backwards CIL stack accounting for the FOURTH value below the
        // Blit call (source). A preceding void call contributes zero pushes
        // but consumes its typed arguments; its own return is never source.
        // Proves at most static declared TYPE on a bounded straight-line
        // original method path, never texture INSTANCE or shader equivalence.
        StackSourceTrace Blocked(string why,int steps,int voids) =>
            new("unknown","unknown",why,steps,voids,null);
        if(method.Body.HasExceptionHandlers || blitIndex<1 ||
            blitIndex>=method.Body.Instructions.Count || !Blit(method.Body.Instructions[blitIndex]))
            return Blocked("not_straight_line",0,0);
        var il=method.Body.Instructions;
        int depth=3,voidCalls=0,steps=0;
        int min=Math.Max(0,blitIndex-96);
        for(int at=blitIndex-1;at>=min;at--)
        {
            var ins=il[at];
            if(ins.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw)
                return Blocked("control_flow_boundary",steps,voidCalls);
            steps++;
            int pops=0,pushes=0;
            string type="unknown",kind="unknown";
            var op=ins.OpCode.Code;
            if(op==Code.Nop)continue;
            if(op is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if(ins.Operand is not MethodReference call || call.Parameters.Count>16)
                    return Blocked("unsupported_call_signature",steps,voidCalls);
                pops=call.Parameters.Count+(op!=Code.Newobj && call.HasThis ? 1:0);
                pushes=op==Code.Newobj || call.ReturnType.FullName!="System.Void" ? 1:0;
                if(pushes==0)voidCalls++;
                type=op==Code.Newobj?call.DeclaringType.FullName:call.ReturnType.FullName;
                kind=op==Code.Newobj?"constructor_result":"typed_call_result";
            }
            else if(op is Code.Ldfld or Code.Ldsfld)
            {
                if(ins.Operand is not FieldReference field)
                    return Blocked("unsupported_field_signature",steps,voidCalls);
                pops=op==Code.Ldfld?1:0;pushes=1;
                type=field.FieldType.FullName;kind="typed_field";
            }
            else if(op is Code.Stfld or Code.Stsfld)
            {
                pops=op==Code.Stfld?2:1;
            }
            else if(op==Code.Ldnull){pushes=1;type="null";kind="literal_null";}
            else if(op==Code.Ldstr){pushes=1;type="System.String";kind="string_literal";}
            else if(Literal(ins).HasValue){pushes=1;type="System.Int32";kind="int_literal";}
            else if(op==Code.Pop){pops=1;}
            else if(op==Code.Dup)
            {
                // Both copies represent the same underlying value. Continue
                // toward the original; do not treat DUP as a texture producer.
                if(depth<2){depth=0;continue;}
                pops=1;pushes=2;
            }
            else if(LocalIndex(ins,true)>=0){pops=1;}
            else if(LocalIndex(ins,false)>=0)
            {
                int local=LocalIndex(ins,false);
                if(local>=method.Body.Variables.Count)
                    return Blocked("bad_local_type",steps,voidCalls);
                pushes=1;
                type=method.Body.Variables[local].VariableType.FullName;
                kind="typed_local";
            }
            else if(op is Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3
                    or Code.Ldarg or Code.Ldarg_S)
            {
                int argument=op switch {
                    Code.Ldarg_0=>0, Code.Ldarg_1=>1, Code.Ldarg_2=>2, Code.Ldarg_3=>3,
                    Code.Ldarg or Code.Ldarg_S when ins.Operand is ParameterDefinition p=>
                        p.Index + (method.HasThis?1:0),
                    _=>-1
                };
                if(argument<0)return Blocked("bad_argument_type",steps,voidCalls);
                pushes=1;kind="typed_argument";
                int index=argument-(method.HasThis?1:0);
                type=index<0?method.DeclaringType.FullName:
                    index<method.Parameters.Count?method.Parameters[index].ParameterType.FullName:
                    "unknown";
            }
            else if(op is Code.Castclass or Code.Isinst)
            {
                if(ins.Operand is not TypeReference cast)
                    return Blocked("bad_cast_type",steps,voidCalls);
                pops=1;pushes=1;type=cast.FullName;kind="typed_cast";
            }
            else if(op==Code.Ldelem_Ref)
            {
                pops=2;pushes=1;kind="array_element";
            }
            else if(op==Code.Ldind_Ref)
            {
                pops=1;pushes=1;kind="indirect_reference";
            }
            else if(op is Code.Ldloca or Code.Ldloca_S or Code.Ldarga or Code.Ldarga_S
                    or Code.Ldsflda)
            {
                pushes=1;kind="address_load";
            }
            else if(op==Code.Ldflda)
            {
                pops=1;pushes=1;kind="address_load";
            }
            else if(op==Code.Ldelema)
            {
                pops=2;pushes=1;kind="address_load";
            }
            else return Blocked("unsupported_cil_opcode",steps,voidCalls);
            if(depth<pushes)
            {
                if(UnsafeFlow(method,at,blitIndex))
                    return Blocked("inbound_branch_or_exception",steps,voidCalls);
                string role=type switch{
                    RenderTexture=>"RenderTexture",
                    Texture=>"Texture",
                    _=>"unknown"
                };
                return new(role,kind,role=="unknown"?"producer_type_not_base_texture":
                    "static_type_only_no_instance_proof",steps,voidCalls,ins);
            }
            depth=depth-pushes+pops;
            if(depth>32)return Blocked("stack_depth_budget",steps,voidCalls);
        }
        return Blocked("trace_budget_or_no_producer",steps,voidCalls);
    }

    static string OriginalTextureReturnBodyFamily(StackSourceTrace trace,ModuleDefinition sourceModule)
    {
        // Only the STATIC return-statement family of a resolvable original
        // managed method definition. No private class/member name, IL index,
        // token or string is printed. Calls through callvirt may dispatch to
        // a different implementation at runtime and are rejected.
        if(trace.Kind!="typed_call_result")return "not_call_return_source";
        var sourceInstruction=trace.SourceInstruction;
        if(sourceInstruction is null || sourceInstruction.Operand is not MethodReference callee)
            return "missing_call_reference";
        // C# can emit CALLVIRT for nonvirtual instance methods merely for the
        // receiver null-check. Do not equate opcode CALLVIRT with dynamic
        // dispatch without checking the exact ORIGINAL MethodDefinition flags.
        MethodDefinition? original=null;
        try { original=callee.Resolve(); }
        catch(AssemblyResolutionException) {return "external_or_unresolved_method";}
        catch(ResolutionException) {return "external_or_unresolved_method";}
        if(original is null || original.Module!=sourceModule)
            return "external_or_unresolved_method";
        if(sourceInstruction.OpCode.Code==Code.Callvirt)
        {
            if(!original.HasThis)return "callvirt_receiver_signature_invalid";
            if(original.IsVirtual && !original.IsFinal)
                return "virtual_dispatch_unresolved";
        }
        if(!original.HasBody)return "original_method_without_body";
        var il=original.Body.Instructions;
        if(original.Body.HasExceptionHandlers)return "original_method_exception_regions";
        if(il.Count>128)return "original_method_budget_exceeded";
        if(il.Any(x=>x.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Throw))return "original_method_branch_flow";
        var returns=il.Select((v,i)=>(Instruction:v,Index:i))
            .Where(x=>x.Instruction.OpCode.Code==Code.Ret).ToArray();
        if(returns.Length!=1)return "original_method_multiple_or_missing_returns";
        int preceding=Previous(il,returns[0].Index-1);
        if(preceding<0)return "original_method_return_producer_unknown";
        var predecessor=il[preceding];
        if(predecessor.OpCode.Code==Code.Ldsfld)
            return "original_method_static_field_return";
        if(predecessor.OpCode.Code==Code.Ldfld)
            return "original_method_instance_field_return_receiver_unproved";
        if(LocalIndex(predecessor,false)>=0)
            return "original_method_local_return_untraced";
        if(predecessor.OpCode.Code is Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2
           or Code.Ldarg_3 or Code.Ldarg or Code.Ldarg_S)
            return "original_method_argument_return_untraced";
        if(predecessor.OpCode.Code is Code.Call or Code.Callvirt)
            return "original_method_nested_call_return_untraced";
        if(predecessor.OpCode.Code==Code.Ldnull)
            return "original_method_null_return";
        return "original_method_return_producer_unknown";
    }

    // Independent CFG topology AUDIT ONLY. An adjacent return predecessor is
    // syntax, never an object-instance or evaluation-stack provenance proof.
    // Inspect only source-original managed method identities in runner scratch.
    static string ReachableReturnTopology(MethodDefinition method)
    {
        if(!method.HasBody)return "cfg_missing_body";
        if(method.Body.HasExceptionHandlers)return "cfg_exception_regions";
        var il=method.Body.Instructions;
        if(il.Count==0 || il.Count>128)return "cfg_instruction_budget";
        var indices=new Dictionary<Instruction,int>();
        for(int i=0;i<il.Count;i++)
            if(!indices.TryAdd(il[i],i))return "cfg_malformed_graph";
        var queue=new Queue<int>();
        var reached=new HashSet<int>();
        var incoming=new Dictionary<int,HashSet<int>>();
        var returns=new List<int>();
        queue.Enqueue(0);
        while(queue.Count>0)
        {
            int at=queue.Dequeue();
            if(at<0 || at>=il.Count)return "cfg_malformed_graph";
            if(!reached.Add(at))continue;
            if(reached.Count>128)return "cfg_instruction_budget";
            var instruction=il[at];
            var flow=instruction.OpCode.FlowControl;
            var targets=new List<int>();
            if(flow==FlowControl.Return)
            {
                if(instruction.OpCode.Code!=Code.Ret)return "cfg_unsupported_flow";
                returns.Add(at);
                continue;
            }
            if(flow==FlowControl.Throw)
                continue; // Throw terminates this route; no inferred return.
            if(flow is FlowControl.Branch or FlowControl.Cond_Branch)
            {
                if(instruction.OpCode.Code==Code.Switch)
                {
                    if(instruction.Operand is not Instruction[] jumpTable || jumpTable.Length>128)
                        return "cfg_malformed_graph";
                    foreach(var target in jumpTable)
                    {
                        if(!indices.TryGetValue(target,out int dest))return "cfg_malformed_graph";
                        targets.Add(dest);
                    }
                }
                else
                {
                    if(instruction.Operand is not Instruction jump ||
                       !indices.TryGetValue(jump,out int dest))
                        return "cfg_malformed_graph";
                    targets.Add(dest);
                }
                if(flow==FlowControl.Cond_Branch)
                {
                    if(at+1>=il.Count)return "cfg_fallthrough_past_end";
                    targets.Add(at+1);
                }
            }
            else if(flow is FlowControl.Next or FlowControl.Call or FlowControl.Meta or FlowControl.Break)
            {
                if(at+1>=il.Count)return "cfg_fallthrough_past_end";
                targets.Add(at+1);
            }
            else return "cfg_unsupported_flow";
            foreach(int target in targets.Distinct())
            {
                if(!incoming.TryGetValue(target,out var parents))
                    incoming[target]=parents=new HashSet<int>();
                parents.Add(at);
                if(!reached.Contains(target))queue.Enqueue(target);
            }
        }
        if(returns.Count==0)return "cfg_no_reachable_returns";
        var families=new HashSet<string>();
        foreach(int ret in returns)
        {
            if(!incoming.TryGetValue(ret,out var parents) || parents.Count!=1)
                return "cfg_multiple_or_entry_return_predecessors";
            int predecessor=parents.Single();
            // An unconditional branch entering a ret may carry a value
            // loaded elsewhere; never treat the prior textual instruction
            // as the actual producer in that situation.
            if(predecessor!=ret-1)return "cfg_nonadjacent_return_predecessor";
            var source=il[predecessor];
            string family=source.OpCode.Code switch
            {
                Code.Ldsfld when source.Operand is FieldReference f &&
                    f.FieldType.FullName is Texture or RenderTexture =>
                    "cfg_syntactic_static_texture_field",
                Code.Ldfld when source.Operand is FieldReference f &&
                    f.FieldType.FullName is Texture or RenderTexture =>
                    "cfg_syntactic_instance_texture_field_receiver_unproved",
                Code.Ldnull=>"cfg_syntactic_null",
                Code.Call or Code.Callvirt =>"cfg_syntactic_nested_call_untraced",
                Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or
                    Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3=>
                    "cfg_syntactic_local_untraced",
                Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or
                    Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3=>
                    "cfg_syntactic_argument_untraced",
                _=>"cfg_syntactic_other_untraced"
            };
            families.Add(family);
        }
        return families.Count==1?families.Single():"cfg_mixed_syntactic_return_predecessors";
    }

    static string OriginalTextureReturnCfgTopology(StackSourceTrace trace,ModuleDefinition sourceModule)
    {
        if(trace.Kind!="typed_call_result")return "not_call_return_source";
        var source=trace.SourceInstruction;
        if(source?.Operand is not MethodReference reference)return "cfg_missing_call_reference";
        MethodDefinition? original=null;
        try {original=reference.Resolve();}
        catch(AssemblyResolutionException){return "cfg_external_or_unresolved";}
        catch(ResolutionException){return "cfg_external_or_unresolved";}
        if(original is null || original.Module!=sourceModule)return "cfg_external_or_unresolved";
        if(source.OpCode.Code==Code.Callvirt)
        {
            if(!original.HasThis)return "cfg_invalid_callvirt_receiver";
            if(original.IsVirtual && !original.IsFinal)return "cfg_dynamic_dispatch_unresolved";
        }
        return ReachableReturnTopology(original);
    }

    // Forward abstract CIL evaluation: follows reachable stack/local VALUES
    // through branches, not merely the opcode adjacent to ret. This is only
    // a category-level structural diagnostic, NEVER instance equality.
    private sealed record ReturnFlowState(string[] Stack,string[] Locals);
    static string ReachableReturnValueFlow(MethodDefinition method)
    {
        if(!method.HasBody)return "value_no_body";
        if(method.Body.HasExceptionHandlers)return "value_exception_regions";
        if(method.ReturnType.FullName is not (Texture or RenderTexture))
            return "value_wrong_return_type";
        var il=method.Body.Instructions;
        if(il.Count is <1 or >128 || method.Body.Variables.Count>32)
            return "value_budget";
        var ix=new Dictionary<Instruction,int>();
        for(int i=0;i<il.Count;i++)
            if(!ix.TryAdd(il[i],i))return "value_bad_target";
        var initial=new ReturnFlowState(Array.Empty<string>(),
            Enumerable.Repeat("opaque",method.Body.Variables.Count).ToArray());
        var input=new Dictionary<int,ReturnFlowState>{{0,initial}};
        var queue=new Queue<int>();
        queue.Enqueue(0);
        var returns=new Dictionary<int,string>();
        int visits=0;
        while(queue.Count>0)
        {
            if(++visits>2048)return "value_budget";
            int at=queue.Dequeue();
            if(!input.TryGetValue(at,out var state)||at<0||at>=il.Count)
                return "value_bad_target";
            var stack=state.Stack.ToList();
            var locals=state.Locals.ToArray();
            var ins=il[at];
            var op=ins.OpCode.Code;
            var flow=ins.OpCode.FlowControl;
            string Pop()
            {
                if(stack.Count==0)throw new InvalidOperationException("abstract_stack_underflow");
                string v=stack[^1];
                stack.RemoveAt(stack.Count-1);
                return v;
            }
            try
            {
                if(op==Code.Ret)
                {
                    if(stack.Count!=1)return "value_invalid_return_stack";
                    returns[at]=stack[0];
                    continue;
                }
                if(op==Code.Throw)
                {
                    Pop(); // Throw path cannot reach a normal return.
                    continue;
                }
                if(op==Code.Rethrow)return "value_exception_regions";
                if(flow is FlowControl.Branch or FlowControl.Cond_Branch)
                {
                    if(flow==FlowControl.Cond_Branch)
                    {
                        if(op is Code.Brtrue or Code.Brtrue_S or Code.Brfalse or
                            Code.Brfalse_S or Code.Switch)Pop();
                        else if(op is Code.Beq or Code.Beq_S or Code.Bne_Un or Code.Bne_Un_S or
                            Code.Bge or Code.Bge_S or Code.Bge_Un or Code.Bge_Un_S or
                            Code.Bgt or Code.Bgt_S or Code.Bgt_Un or Code.Bgt_Un_S or
                            Code.Ble or Code.Ble_S or Code.Ble_Un or Code.Ble_Un_S or
                            Code.Blt or Code.Blt_S or Code.Blt_Un or Code.Blt_Un_S)
                        {Pop();Pop();}
                        else return "value_unsupported_branch";
                    }
                    else if(op is not (Code.Br or Code.Br_S))
                        return "value_unsupported_branch";
                }
                else if(op==Code.Nop){}
                else if(op==Code.Ldnull)stack.Add("null");
                else if(op==Code.Ldstr || Literal(ins).HasValue ||
                        op is Code.Ldc_I8 or Code.Ldc_R4 or Code.Ldc_R8)
                    stack.Add("opaque");
                else if(op is Code.Ldsfld or Code.Ldfld)
                {
                    if(ins.Operand is not FieldReference field)return "value_unsupported_opcode";
                    if(op==Code.Ldfld)Pop(); // Receiver identity is NOT known.
                    stack.Add(field.FieldType.FullName is Texture or RenderTexture ?
                        (op==Code.Ldsfld?"static_field_category":"instance_field_receiver_unknown"):
                        "opaque");
                }
                else if(op is Code.Stsfld or Code.Stfld)
                {
                    if(ins.Operand is not FieldReference)return "value_unsupported_opcode";
                    Pop();
                    if(op==Code.Stfld)Pop();
                }
                else if(LocalIndex(ins,false)>=0)
                {
                    int local=LocalIndex(ins,false);
                    if(local>=locals.Length)return "value_bad_local";
                    stack.Add(locals[local]);
                }
                else if(LocalIndex(ins,true)>=0)
                {
                    int local=LocalIndex(ins,true);
                    if(local>=locals.Length)return "value_bad_local";
                    locals[local]=Pop();
                }
                else if(op is Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2 or
                    Code.Ldarg_3 or Code.Ldarg or Code.Ldarg_S)
                    stack.Add("argument_untraced");
                else if(op==Code.Dup)
                {
                    string top=Pop();
                    stack.Add(top);stack.Add(top);
                }
                else if(op==Code.Pop)Pop();
                else if(op is Code.Call or Code.Callvirt or Code.Newobj)
                {
                    if(ins.Operand is not MethodReference call || call.Parameters.Count>16)
                        return "value_unsupported_opcode";
                    for(int i=0;i<call.Parameters.Count;i++)Pop();
                    if(op!=Code.Newobj && call.HasThis)Pop();
                    if(op==Code.Newobj)stack.Add("constructed_untraced");
                    else if(call.ReturnType.FullName!="System.Void")
                        stack.Add("nested_call_untraced");
                }
                else if(op is Code.Castclass or Code.Isinst or Code.Box or Code.Unbox_Any)
                {
                    Pop();
                    stack.Add("opaque"); // No receiver/alias promotion by a cast.
                }
                else if(op is Code.Ldloca or Code.Ldloca_S or Code.Ldarga or
                    Code.Ldarga_S or Code.Ldsflda)
                    stack.Add("opaque");
                else if(op==Code.Ldflda)
                {Pop();stack.Add("opaque");}
                else if(op==Code.Ldelem_Ref || op==Code.Ldelema)
                {Pop();Pop();stack.Add("opaque");}
                else if(op is Code.Ldind_Ref or Code.Ldlen)
                {Pop();stack.Add("opaque");}
                else if(op is Code.Ceq or Code.Cgt or Code.Cgt_Un or Code.Clt or
                    Code.Clt_Un or Code.Add or Code.Sub or Code.Mul)
                {Pop();Pop();stack.Add("opaque");}
                else if(op==Code.Initobj)Pop();
                else if(op==Code.Stind_Ref){Pop();Pop();}
                else return "value_unsupported_opcode";
            }
            catch(InvalidOperationException)
            {
                return "value_invalid_stack";
            }
            if(stack.Count>32)return "value_budget";
            var successors=new List<int>();
            if(flow is FlowControl.Branch or FlowControl.Cond_Branch)
            {
                if(op==Code.Switch)
                {
                    if(ins.Operand is not Instruction[] options || options.Length>128)
                        return "value_bad_target";
                    foreach(var target in options)
                    {
                        if(!ix.TryGetValue(target,out int dest))return "value_bad_target";
                        successors.Add(dest);
                    }
                }
                else
                {
                    if(ins.Operand is not Instruction target || !ix.TryGetValue(target,out int dest))
                        return "value_bad_target";
                    successors.Add(dest);
                }
                if(flow==FlowControl.Cond_Branch)successors.Add(at+1);
            }
            else if(flow is FlowControl.Next or FlowControl.Call or FlowControl.Meta)
                successors.Add(at+1);
            else return "value_unsupported_opcode";
            foreach(int target in successors.Distinct())
            {
                if(target<0||target>=il.Count)return "value_bad_target";
                var candidate=new ReturnFlowState(stack.ToArray(),locals.ToArray());
                if(input.TryGetValue(target,out var previous))
                {
                    if(previous.Stack.Length!=candidate.Stack.Length ||
                       previous.Locals.Length!=candidate.Locals.Length)
                        return "value_invalid_join_stack";
                    string Merge(string a,string b)=>a==b?a:"mixed";
                    var newStack=previous.Stack.Zip(candidate.Stack,Merge).ToArray();
                    var newLocals=previous.Locals.Zip(candidate.Locals,Merge).ToArray();
                    if(!newStack.SequenceEqual(previous.Stack) ||
                       !newLocals.SequenceEqual(previous.Locals))
                    {
                        input[target]=new ReturnFlowState(newStack,newLocals);
                        queue.Enqueue(target);
                    }
                }
                else
                {
                    input[target]=candidate;
                    queue.Enqueue(target);
                }
            }
        }
        if(returns.Count==0)return "value_no_reachable_return";
        var categories=returns.Values.Distinct().ToArray();
        if(categories.Length!=1 || categories[0]=="mixed")return "value_mixed_or_joined";
        return categories[0] switch
        {
            "null"=>"value_null_only",
            "static_field_category"=>"value_static_field_category_only",
            "instance_field_receiver_unknown"=>"value_instance_field_receiver_unknown",
            "argument_untraced"=>"value_argument_untraced",
            "nested_call_untraced"=>"value_nested_call_untraced",
            "constructed_untraced"=>"value_constructed_untraced",
            _=>"value_opaque_untraced"
        };
    }

    static string OriginalTextureReturnValueFlow(StackSourceTrace trace,ModuleDefinition sourceModule)
    {
        if(trace.Kind!="typed_call_result")return "not_call_return_source";
        if(trace.SourceInstruction?.Operand is not MethodReference method)
            return "value_missing_call_reference";
        MethodDefinition? callee;
        try{callee=method.Resolve();}
        catch(AssemblyResolutionException){return "value_external_or_unresolved";}
        catch(ResolutionException){return "value_external_or_unresolved";}
        if(callee is null||callee.Module!=sourceModule)return "value_external_or_unresolved";
        if(trace.SourceInstruction.OpCode.Code==Code.Callvirt)
        {
            if(!callee.HasThis)return "value_bad_receiver_signature";
            if(callee.IsVirtual&&!callee.IsFinal)return "value_dynamic_dispatch_unresolved";
        }
        return ReachableReturnValueFlow(callee);
    }

    static string SourceAdjacentCallReturnFamily(MethodDefinition method,int callIndex,FieldDefinition field)
    {
        // Public type-family only. In particular a preceding void call is
        // NOT the Blit source producer; typed call-return is still NOT an
        // authenticated texture *instance*. Never export private type names.
        if(!DirectMaterialBlit(method,callIndex,field))return "material_not_direct";
        var il=method.Body.Instructions;
        int p=Previous(il,callIndex-1), mat=Previous(il,p-1);
        int at=mat-1;
        if(il[mat].OpCode.Code==Code.Ldfld)
        {
            at=Previous(il,at);
            if(at<0 || !Receiver(il[at]))return "material_not_direct";
            at--;
        }
        var dst=TypedValue(method,il,ref at);
        if(dst.Type is not (RenderTexture or "null"))return "destination_not_direct";
        int preceding=Previous(il,at);
        if(preceding<0)return "no_adjacent_opcode";
        var inst=il[preceding];
        if(inst.OpCode.Code is not (Code.Call or Code.Callvirt) ||
           inst.Operand is not MethodReference m)return "not_typed_call";
        return m.ReturnType.FullName switch
        {
            "System.Void"=>"void",
            "UnityEngine.Texture"=>"texture",
            "UnityEngine.RenderTexture"=>"render_texture",
            "UnityEngine.Texture2D"=>"texture2d",
            "UnityEngine.Texture3D"=>"texture3d",
            "UnityEngine.Texture2DArray"=>"texture2d_array",
            "UnityEngine.Cubemap"=>"cubemap",
            "UnityEngine.CubemapArray"=>"cubemap_array",
            "UnityEngine.CustomRenderTexture"=>"custom_render_texture",
            "UnityEngine.SparseTexture"=>"sparse_texture",
            "UnityEngine.Object"=>"unity_object",
            "System.Object"=>"system_object",
            "UnityEngine.Material"=>"material",
            "System.Int32" or "System.Int64" or "System.Boolean" or
                "System.Single" or "System.Double"=>"primitive",
            var full when full.StartsWith("UnityEngine.",StringComparison.Ordinal)=>
                "other_unity_type",
            var full when full.StartsWith("System.",StringComparison.Ordinal)=>
                "other_system_type",
            _=>"opaque_nonpublic_or_external_type"
        };
    }

    static string SourceHeadClass(MethodDefinition method, int callIndex, FieldDefinition field)
    {
        // Classify the *immediately preceding CIL opcode family* once the
        // typed destination has been consumed. This is NOT the identity or
        // stack producer of a texture; keep unrelated private IL out of logs.
        if(!DirectMaterialBlit(method,callIndex,field))return "not_direct_material";
        var il=method.Body.Instructions;
        int pass=Previous(il,callIndex-1);
        int mat=Previous(il,pass-1);
        int at=mat-1;
        if(il[mat].OpCode.Code==Code.Ldfld)
        {
            at=Previous(il,at);
            if(at<0||!Receiver(il[at]))return "not_direct_material";
            at--;
        }
        var dst=TypedValue(method,il,ref at);
        if(dst.Type is not (RenderTexture or "null"))return "destination_not_direct";
        int srcIndex=Previous(il,at);
        if(srcIndex<0)return "source_head_missing";
        var inst=il[srcIndex];
        if(inst.OpCode.Code is Code.Call or Code.Callvirt)
        {
            if(inst.Operand is not MethodReference call)return "call_signature_unavailable";
            return call.ReturnType.FullName switch
            {
                RenderTexture=>"call_returns_render_texture",
                Texture=>"call_returns_texture",
                _=>"call_returns_other"
            };
        }
        if(inst.OpCode.Code==Code.Newobj)return "constructor_result";
        if(inst.OpCode.Code is Code.Castclass or Code.Isinst)
        {
            if(inst.Operand is not TypeReference type)return "cast_type_unavailable";
            return type.FullName switch
            {
                RenderTexture=>"cast_to_render_texture",
                Texture=>"cast_to_texture",
                _=>"cast_to_other"
            };
        }
        if(inst.OpCode.Code==Code.Ldelem_Ref)return "array_element";
        if(inst.OpCode.Code==Code.Ldind_Ref)return "indirect_reference";
        if(inst.OpCode.Code is Code.Ldloca or Code.Ldloca_S or Code.Ldarga or
            Code.Ldarga_S or Code.Ldflda or Code.Ldsflda or Code.Ldelema)
            return "address_load";
        if(inst.OpCode.Code is Code.Ldfld or Code.Ldsfld)return "field_load_complex";
        if(inst.OpCode.Code==Code.Dup)return "stack_duplicate";
        if(inst.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch)
            return "control_flow";
        return "other_opcode_family";
    }

    static Site? DirectFieldBlit(MethodDefinition m,int callIndex,FieldDefinition field)
    {
        var il=m.Body.Instructions;
        int pass=Previous(il,callIndex-1);
        if(pass<0 || Literal(il[pass]) is not (0 or 1))return null;
        int material=Previous(il,pass-1);
        if(material<0 || !SameField(il[material],field,true))return null;
        int before=material-1;
        if(il[material].OpCode.Code==Code.Ldfld)
        {
            before=Previous(il,before);
            if(before<0||!Receiver(il[before]))return null;
            before--;
        }
        var dst=TypedValue(m,il,ref before);
        var src=TypedValue(m,il,ref before);
        if(src.Type is not (Texture or RenderTexture) ||
           dst.Type is not (RenderTexture or "null"))return null;
        int start=Previous(il,before+1);
        if(start<0 || UnsafeFlow(m,start,callIndex))return null;
        return new(src.Type==Texture?"Texture":"RenderTexture",
            dst.Type=="null"?"null":"RenderTexture",
            src.Kind,dst.Kind);
    }
    static object Scan(AssemblyDefinition asm,string originalName)
    {
        var methods=Methods(asm).ToList();
        var findSites=new List<(MethodDefinition Method,int At)>();
        int findCount=0,shaderToCtor=0;
        foreach(var method in methods)
        {
            var il=method.Body.Instructions;
            for(int i=0;i<il.Count;i++)
                if(FindShader(il[i]))
                {
                    findCount++;
                    int prev=Previous(il,i-1);
                    if(prev>=0 && il[prev].OpCode.Code==Code.Ldstr &&
                       il[prev].Operand is string s &&
                       string.Equals(s,originalName,StringComparison.Ordinal))
                        findSites.Add((method,i));
                }
        }
        FieldDefinition? shaderField=null;
        if(findSites.Count==1)
        {
            var (m,at)=findSites[0];
            var il=m.Body.Instructions;
            int next=Next(il,at+1);
            if(next>=0 && (il[next].OpCode.Code is Code.Stfld or Code.Stsfld) &&
               il[next].Operand is FieldReference fr && fr.FieldType.FullName==Shader)
            {
                try{var f=fr.Resolve();if(f is not null && f.Module==m.Module)shaderField=f;}
                catch(AssemblyResolutionException){}catch(ResolutionException){}
            }
        }
        var ctorSites=new List<(MethodDefinition Method,int At)>();
        if(shaderField is not null)
            foreach(var m in methods)
            {
                var il=m.Body.Instructions;
                for(int i=0;i<il.Count;i++)
                    if(SameField(il[i],shaderField,true))
                    {
                        int next=Next(il,i+1);
                        if(next>=0 && MaterialCtor(il[next]))
                            ctorSites.Add((m,next));
                    }
            }
        shaderToCtor=ctorSites.Count;
        FieldDefinition? materialField=null;
        if(ctorSites.Count==1)
            materialField=MaterialFieldFromCtor(ctorSites[0].Method,ctorSites[0].At);
        var candidates=new Dictionary<int,List<Site>>{{0,new()},{1,new()}};
        int allBlits=0,allPass0=0,allPass1=0,allOther=0,linked=0;
        var exactMaterialDirect=new int[2];
        var exactMaterialLocalAlias=new int[2];
        var originalFirstBlockers=new Dictionary<int,List<string>>{{0,new()},{1,new()}};
        var originalSourceHeadKinds=new Dictionary<int,List<string>>{{0,new()},{1,new()}};
        var originalSourceReturnKinds=new Dictionary<int,List<string>>{{0,new()},{1,new()}};
        var originalBacktraces=new Dictionary<int,List<StackSourceTrace>>{{0,new()},{1,new()}};
        foreach(var m in methods)
        {
            var il=m.Body.Instructions;
            for(int i=0;i<il.Count;i++)
                if(Blit(il[i]))
                {
                    allBlits++;
                    int n=Previous(il,i-1);
                    int? lit=n>=0?Literal(il[n]):null;
                    if(lit==0)allPass0++;
                    else if(lit==1)allPass1++;
                    else allOther++;
                    if(materialField is null || lit is not (0 or 1))continue;
                    if(DirectMaterialBlit(m,i,materialField))
                    {
                        exactMaterialDirect[lit.Value]++;
                        originalFirstBlockers[lit.Value].Add(FirstUnresolvedImageOperand(m,i,materialField));
                        originalSourceHeadKinds[lit.Value].Add(SourceHeadClass(m,i,materialField));
                        originalSourceReturnKinds[lit.Value].Add(SourceAdjacentCallReturnFamily(m,i,materialField));
                        originalBacktraces[lit.Value].Add(BacktraceBlitSource(m,i));
                    }
                    else if(OriginalMaterialLocalAliasBlit(m,i,materialField))
                        exactMaterialLocalAlias[lit.Value]++;
                    var match=DirectFieldBlit(m,i,materialField);
                    if(match is not null){candidates[lit.Value].Add(match);linked++;}
                }
        }
        var pass0=candidates[0].Count==1?candidates[0][0]:null;
        var pass1=candidates[1].Count==1?candidates[1][0]:null;
        // The one-step numeric-safe diagnosis runs on authenticated original
        // IL, but never claims a private source/target object's identity.
        string tag0=originalFirstBlockers[0].Count==1?originalFirstBlockers[0][0]:"ambiguous_or_missing";
        string tag1=originalFirstBlockers[1].Count==1?originalFirstBlockers[1][0]:"ambiguous_or_missing";
        var allowed=new HashSet<string>{"none","destination_not_direct","source_not_direct",
            "control_flow","material_not_direct","ambiguous_or_missing"};
        if(!allowed.Contains(tag0) || !allowed.Contains(tag1))
            throw new InvalidOperationException("unsafe_original_diagnostic_tag");
        Console.WriteLine("T2_FOAM_PASS0_FIRST_IMAGE_OPERAND "+tag0);
        Console.WriteLine("T2_FOAM_PASS1_FIRST_IMAGE_OPERAND "+tag1);
        string head0=originalSourceHeadKinds[0].Count==1?originalSourceHeadKinds[0][0]:"ambiguous_or_missing";
        string head1=originalSourceHeadKinds[1].Count==1?originalSourceHeadKinds[1][0]:"ambiguous_or_missing";
        var safeHeadTags=new HashSet<string>{
            "not_direct_material", "destination_not_direct", "source_head_missing",
            "call_signature_unavailable", "call_returns_render_texture",
            "call_returns_texture", "call_returns_other", "constructor_result",
            "cast_type_unavailable", "cast_to_render_texture", "cast_to_texture",
            "cast_to_other", "array_element", "indirect_reference", "address_load",
            "field_load_complex", "stack_duplicate", "control_flow",
            "other_opcode_family", "ambiguous_or_missing"
        };
        if(!safeHeadTags.Contains(head0)||!safeHeadTags.Contains(head1))
            throw new InvalidOperationException("private_CIL_source_head_not_allowed");
        Console.WriteLine("T2_FOAM_PASS0_SOURCE_HEAD_CLASS "+head0);
        Console.WriteLine("T2_FOAM_PASS1_SOURCE_HEAD_CLASS "+head1);
        string ret0=originalSourceReturnKinds[0].Count==1?originalSourceReturnKinds[0][0]:"ambiguous_or_missing";
        string ret1=originalSourceReturnKinds[1].Count==1?originalSourceReturnKinds[1][0]:"ambiguous_or_missing";
        var safeReturns=new HashSet<string>{
            "material_not_direct","destination_not_direct","no_adjacent_opcode","not_typed_call",
            "void","texture","render_texture","texture2d","texture3d","texture2d_array",
            "cubemap","cubemap_array","custom_render_texture","sparse_texture","unity_object",
            "system_object","material","primitive","other_unity_type","other_system_type",
            "opaque_nonpublic_or_external_type","ambiguous_or_missing"
        };
        if(!safeReturns.Contains(ret0)||!safeReturns.Contains(ret1))
            throw new InvalidOperationException("unsafe_original_return_type_family");
        Console.WriteLine("T2_FOAM_PASS0_ADJACENT_RETURN_FAMILY "+ret0);
        Console.WriteLine("T2_FOAM_PASS1_ADJACENT_RETURN_FAMILY "+ret1);
        var back0=originalBacktraces[0].Count==1?originalBacktraces[0][0]:
            new StackSourceTrace("unknown","unknown","ambiguous_or_missing",0,0,null);
        var back1=originalBacktraces[1].Count==1?originalBacktraces[1][0]:
            new StackSourceTrace("unknown","unknown","ambiguous_or_missing",0,0,null);
        var safeStackKinds=new HashSet<string>{
            "unknown","typed_field","typed_local","typed_argument","typed_call_result",
            "typed_cast","constructor_result","array_element","indirect_reference",
            "literal_null","string_literal","int_literal","address_load"
        };
        var safeStackReasons=new HashSet<string>{
            "not_straight_line","control_flow_boundary","unsupported_call_signature",
            "unsupported_field_signature","bad_local_type","bad_argument_type",
            "bad_cast_type","unsupported_cil_opcode","inbound_branch_or_exception",
            "producer_type_not_base_texture","static_type_only_no_instance_proof",
            "stack_depth_budget","trace_budget_or_no_producer","ambiguous_or_missing"
        };
        foreach(var tr in new[]{back0,back1})
            if(tr.Role is not ("unknown" or "Texture" or "RenderTexture") ||
               !safeStackKinds.Contains(tr.Kind)||!safeStackReasons.Contains(tr.Reason)||
               tr.Steps<0||tr.Steps>96||tr.VoidCalls<0||tr.VoidCalls>tr.Steps)
                throw new InvalidOperationException("private_or_invalid_stack_trace_tag");
        Console.WriteLine("T2_FOAM_PASS0_BACKTRACE "+back0.Role+" "+back0.Kind+" "+back0.Reason+
            " steps="+back0.Steps+" void_calls="+back0.VoidCalls);
        Console.WriteLine("T2_FOAM_PASS1_BACKTRACE "+back1.Role+" "+back1.Kind+" "+back1.Reason+
            " steps="+back1.Steps+" void_calls="+back1.VoidCalls);
        string methodKind0=OriginalTextureReturnBodyFamily(back0,asm.MainModule);
        string methodKind1=OriginalTextureReturnBodyFamily(back1,asm.MainModule);
        var permittedReturnBodies=new HashSet<string>{
            "not_call_return_source", "missing_call_reference", "virtual_dispatch_unresolved",
            "callvirt_receiver_signature_invalid", "external_or_unresolved_method", "original_method_without_body",
            "original_method_exception_regions", "original_method_budget_exceeded",
            "original_method_branch_flow", "original_method_multiple_or_missing_returns",
            "original_method_return_producer_unknown", "original_method_static_field_return",
            "original_method_instance_field_return_receiver_unproved",
            "original_method_local_return_untraced",
            "original_method_argument_return_untraced",
            "original_method_nested_call_return_untraced", "original_method_null_return"
        };
        if(!permittedReturnBodies.Contains(methodKind0) ||
           !permittedReturnBodies.Contains(methodKind1))
            throw new InvalidOperationException("private_return_method_info_forbidden");
        Console.WriteLine("T2_FOAM_PASS0_CALLEE_BODY_FAMILY "+methodKind0);
        Console.WriteLine("T2_FOAM_PASS1_CALLEE_BODY_FAMILY "+methodKind1);
        var topo0=OriginalTextureReturnCfgTopology(back0,asm.MainModule);
        var topo1=OriginalTextureReturnCfgTopology(back1,asm.MainModule);
        var permittedCfg=new HashSet<string>{
            "not_call_return_source","cfg_missing_call_reference","cfg_external_or_unresolved",
            "cfg_invalid_callvirt_receiver","cfg_dynamic_dispatch_unresolved","cfg_missing_body",
            "cfg_exception_regions","cfg_instruction_budget","cfg_malformed_graph",
            "cfg_unsupported_flow","cfg_fallthrough_past_end","cfg_no_reachable_returns",
            "cfg_multiple_or_entry_return_predecessors","cfg_nonadjacent_return_predecessor",
            "cfg_syntactic_static_texture_field",
            "cfg_syntactic_instance_texture_field_receiver_unproved",
            "cfg_syntactic_null","cfg_syntactic_nested_call_untraced",
            "cfg_syntactic_local_untraced","cfg_syntactic_argument_untraced",
            "cfg_syntactic_other_untraced","cfg_mixed_syntactic_return_predecessors"
        };
        if(!permittedCfg.Contains(topo0)||!permittedCfg.Contains(topo1))
            throw new InvalidOperationException("private_cfg_return_info_forbidden");
        Console.WriteLine("T2_FOAM_PASS0_CALLEE_CFG_TOPOLOGY "+topo0);
        Console.WriteLine("T2_FOAM_PASS1_CALLEE_CFG_TOPOLOGY "+topo1);
        var value0=OriginalTextureReturnValueFlow(back0,asm.MainModule);
        var value1=OriginalTextureReturnValueFlow(back1,asm.MainModule);
        var safeValueTags=new HashSet<string>{
            "not_call_return_source","value_missing_call_reference",
            "value_external_or_unresolved","value_bad_receiver_signature",
            "value_dynamic_dispatch_unresolved","value_no_body",
            "value_exception_regions","value_wrong_return_type","value_budget",
            "value_bad_target","value_unsupported_opcode","value_unsupported_branch",
            "value_bad_local","value_invalid_stack","value_invalid_return_stack",
            "value_invalid_join_stack","value_no_reachable_return",
            "value_mixed_or_joined","value_null_only",
            "value_static_field_category_only","value_instance_field_receiver_unknown",
            "value_argument_untraced","value_nested_call_untraced",
            "value_constructed_untraced","value_opaque_untraced"
        };
        if(!safeValueTags.Contains(value0)||!safeValueTags.Contains(value1))
            throw new InvalidOperationException("unsafe_original_value_flow_category");
        Console.WriteLine("T2_FOAM_PASS0_CALLEE_RETURN_VALUE_FLOW "+value0);
        Console.WriteLine("T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW "+value1);
        // Correct original field role proof remains separate from image instance continuity.
        return new {
            status="original_foam_typed_blit_producer_audit",
            immutable_original_zip2_sha_verified=true,
            original_Assembly_CSharp_sha_verified=true,
            original_Foam_Shader_name_sha_verified=true,
            original_compiled_methods_scanned=methods.Count,
            original_typed_Shader_Find_calls=findCount,
            exact_original_Foam_direct_Find_sites=findSites.Count,
            original_Shader_field_resolved=shaderField is not null,
            original_direct_Material_constructor_sites=shaderToCtor,
            original_Material_field_uniquely_resolved=materialField is not null,
            original_exact_static_four_arg_Blit_calls=allBlits,
            original_explicit_pass0_literal_Blit_calls=allPass0,
            original_explicit_pass1_literal_Blit_calls=allPass1,
            original_other_or_dynamic_pass_Blit_calls=allOther,
            original_direct_material_field_and_typed_image_linked_Blit_calls=linked,
            original_pass0_direct_link_candidates=candidates[0].Count,
            original_pass1_direct_link_candidates=candidates[1].Count,
            original_pass0_exact_Material_field_argument_calls=exactMaterialDirect[0],
            original_pass1_exact_Material_field_argument_calls=exactMaterialDirect[1],
            original_pass0_exact_Material_local_alias_calls=exactMaterialLocalAlias[0],
            original_pass1_exact_Material_local_alias_calls=exactMaterialLocalAlias[1],
            original_pass0_linked_Material_image_producers_unresolved=
                exactMaterialDirect[0]-candidates[0].Count,
            original_pass1_linked_Material_image_producers_unresolved=
                exactMaterialDirect[1]-candidates[1].Count,
            pass0_source=pass0?.Source??"unknown",
            pass0_destination=pass0?.Destination??"unknown",
            pass0_source_producer=pass0?.SourceProducer??"unknown",
            pass0_destination_producer=pass0?.DestinationProducer??"unknown",
            pass1_source=pass1?.Source??"unknown",
            pass1_destination=pass1?.Destination??"unknown",
            pass1_source_producer=pass1?.SourceProducer??"unknown",
            pass1_destination_producer=pass1?.DestinationProducer??"unknown",
            original_pass0_bounded_stack_source_type=back0.Role,
            original_pass1_bounded_stack_source_type=back1.Role,
            original_pass0_bounded_stack_source_kind=back0.Kind,
            original_pass1_bounded_stack_source_kind=back1.Kind,
            original_pass0_bounded_stack_reason=back0.Reason,
            original_pass1_bounded_stack_reason=back1.Reason,
            original_pass0_bounded_stack_steps=back0.Steps,
            original_pass1_bounded_stack_steps=back1.Steps,
            original_pass0_bounded_stack_void_calls=back0.VoidCalls,
            original_pass1_bounded_stack_void_calls=back1.VoidCalls,
            original_bounded_stack_static_type_only=true,
            original_bounded_stack_texture_instance_equality_verified=false,
            original_shader_to_blit_direct_field_types_confirmed=pass0 is not null && pass1 is not null,
            original_texture_instance_identity_proven=false,
            original_crosspass_destination_to_source_identity_proven=false,
            original_CB0_sampler_binding_verified=false,
            original_ShaderLab_Unity_or_Android_pixels_verified=false,
            private_names_IL_methods_fields_pathids_or_bytecode_exported=false
        };
    }

    static void SelfTest()
    {
        var mod=ModuleDefinition.CreateModule("SyntheticNoOriginalSource",ModuleKind.Dll);
        var gfx=new TypeReference("UnityEngine","Graphics",mod,mod.TypeSystem.CoreLibrary);
        var tex=new TypeReference("UnityEngine","Texture",mod,mod.TypeSystem.CoreLibrary);
        var rt=new TypeReference("UnityEngine","RenderTexture",mod,mod.TypeSystem.CoreLibrary);
        var mat=new TypeReference("UnityEngine","Material",mod,mod.TypeSystem.CoreLibrary);
        var b=new MethodReference("Blit",mod.TypeSystem.Void,gfx){HasThis=false};
        foreach(var p in new[]{tex,rt,mat,mod.TypeSystem.Int32})b.Parameters.Add(new ParameterDefinition(p));
        if(!Blit(Instruction.Create(OpCodes.Call,b)) ||
           !Equals(Literal(Instruction.Create(OpCodes.Ldc_I4_1)),1) ||
           !Equals(Literal(Instruction.Create(OpCodes.Ldc_I4_0)),0) ||
           Literal(Instruction.Create(OpCodes.Ldc_I4_7))==1)
            throw new InvalidOperationException("synthetic_exact_signature");
        b.Name="Other";
        if(Blit(Instruction.Create(OpCodes.Call,b)))
            throw new InvalidOperationException("impostor_method_accepted");
        var owner=new TypeDefinition("Fixture","Owner",Mono.Cecil.TypeAttributes.Public|Mono.Cecil.TypeAttributes.Class,mod.TypeSystem.Object);
        mod.Types.Add(owner);
        var method=new MethodDefinition("Fixture",Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,mod.TypeSystem.Void);
        owner.Methods.Add(method);
        method.Parameters.Add(new ParameterDefinition(tex));
        method.Body.Variables.Add(new VariableDefinition(rt));
        var instructions=new List<Instruction>{Instruction.Create(OpCodes.Ldarg_0),Instruction.Create(OpCodes.Ldloc_0),Instruction.Create(OpCodes.Ldnull)};
        int at=2;
        if(TypedValue(method,instructions,ref at).Type!="null"||at!=1||
           TypedValue(method,instructions,ref at).Type!=RenderTexture||at!=0||
           TypedValue(method,instructions,ref at).Type!=Texture||at!=-1)
            throw new InvalidOperationException("typed_fixture_order");
        // Test a nested call-producing source value: the last CIL opcode
        // is a typed call, but the actual returned texture *instance* is NOT
        // deducible from its public return-type declaration.
        var fixtureMatField=new FieldDefinition("MaterialFixture",
            Mono.Cecil.FieldAttributes.Private|Mono.Cecil.FieldAttributes.Static,mat);
        var fixtureRtField=new FieldDefinition("TargetFixture",
            Mono.Cecil.FieldAttributes.Private|Mono.Cecil.FieldAttributes.Static,rt);
        owner.Fields.Add(fixtureMatField);
        owner.Fields.Add(fixtureRtField);
        var fixtureMethod=new MethodDefinition("HeadFixture",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,mod.TypeSystem.Void);
        owner.Methods.Add(fixtureMethod);
        var producerCall=new MethodReference("PrivateSyntheticProducer",rt,owner){HasThis=false};
        var stream=fixtureMethod.Body.Instructions;
        stream.Add(Instruction.Create(OpCodes.Call,producerCall)); // source
        stream.Add(Instruction.Create(OpCodes.Ldsfld,fixtureRtField)); // destination
        stream.Add(Instruction.Create(OpCodes.Ldsfld,fixtureMatField)); // Foam material
        stream.Add(Instruction.Create(OpCodes.Ldc_I4_1)); // pass
        stream.Add(Instruction.Create(OpCodes.Call,b)); // Blit, name restored next
        b.Name="Blit";
        if(!DirectMaterialBlit(fixtureMethod,4,fixtureMatField) ||
           FirstUnresolvedImageOperand(fixtureMethod,4,fixtureMatField)!="source_not_direct" ||
           SourceHeadClass(fixtureMethod,4,fixtureMatField)!="call_returns_render_texture")
            throw new InvalidOperationException("synthetic_call_head_not_classified");
        producerCall.ReturnType=mod.TypeSystem.Void;
        if(SourceAdjacentCallReturnFamily(fixtureMethod,4,fixtureMatField)!="void")
            throw new InvalidOperationException("void_return_must_not_be_texture");
        if(SourceHeadClass(fixtureMethod,4,fixtureMatField)!="call_returns_other")
            throw new InvalidOperationException("void_call_not_texture");
        producerCall.ReturnType=rt;
        if(SourceAdjacentCallReturnFamily(fixtureMethod,4,fixtureMatField)!="render_texture")
            throw new InvalidOperationException("typed_public_RT_return_family");
        stream[0]=Instruction.Create(OpCodes.Ldelem_Ref);
        if(SourceAdjacentCallReturnFamily(fixtureMethod,4,fixtureMatField)!="not_typed_call")
            throw new InvalidOperationException("array_must_not_be_forged_call_return");
        if(SourceHeadClass(fixtureMethod,4,fixtureMatField)!="array_element")
            throw new InvalidOperationException("array_result_not_kind");
        // Backtrace a genuinely void call that consumes one argument:
        // src field, int argument, void call, dst field, mat field, pass, Blit.
        var sideEffect=new MethodReference("SyntheticVoidSideEffect",
            mod.TypeSystem.Void,owner){HasThis=false};
        sideEffect.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Int32));
        stream.Clear();
        stream.Add(Instruction.Create(OpCodes.Ldsfld,fixtureRtField)); // original source
        stream.Add(Instruction.Create(OpCodes.Ldc_I4_7)); // void call input
        stream.Add(Instruction.Create(OpCodes.Call,sideEffect)); // NO return
        stream.Add(Instruction.Create(OpCodes.Ldsfld,fixtureRtField)); // destination
        stream.Add(Instruction.Create(OpCodes.Ldsfld,fixtureMatField));
        stream.Add(Instruction.Create(OpCodes.Ldc_I4_1));
        stream.Add(Instruction.Create(OpCodes.Call,b));
        var traced=BacktraceBlitSource(fixtureMethod,6);
        if(traced.Role!="RenderTexture" || traced.Kind!="typed_field" ||
           traced.Reason!="static_type_only_no_instance_proof" ||
           traced.VoidCalls!=1 || traced.Steps!=6)
            throw new InvalidOperationException("void_call_stack_did_not_reach_original_source");
        sideEffect.ReturnType=rt;
        traced=BacktraceBlitSource(fixtureMethod,6);
        if(traced.Role!="RenderTexture" || traced.Kind!="typed_call_result" ||
           traced.VoidCalls!=0)
            throw new InvalidOperationException("typed_call_return_stack_misclassified");
        sideEffect.ReturnType=mod.TypeSystem.Void;
        stream[1]=Instruction.Create(OpCodes.Br_S,stream[2]);
        traced=BacktraceBlitSource(fixtureMethod,6);
        if(traced.Role!="unknown"||traced.Reason!="control_flow_boundary")
            throw new InvalidOperationException("synthetic_branch_must_block_source_proof");
        stream[1]=Instruction.Create(OpCodes.Ldc_I4_7);
        stream[0]=Instruction.Create(OpCodes.Ldstr,"untyped_source");
        traced=BacktraceBlitSource(fixtureMethod,6);
        if(traced.Role!="unknown" || traced.Reason!="producer_type_not_base_texture")
            throw new InvalidOperationException("non_texture_stack_value_must_not_pass");
        // An original-module method with a single direct static field return
        // is type-classifiable without proving any runtime texture identity.
        var getter=new MethodDefinition("SourceFreeSyntheticGetter",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,tex);
        owner.Methods.Add(getter);
        getter.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,fixtureRtField));
        getter.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        stream[2]=Instruction.Create(OpCodes.Call,getter);
        traced=BacktraceBlitSource(fixtureMethod,6);
        if(traced.Role!="Texture" ||
           OriginalTextureReturnBodyFamily(traced,mod)!="original_method_static_field_return")
            throw new InvalidOperationException("original_module_return_lineage_not_bounded");
        getter.Body.Instructions.Insert(0,Instruction.Create(OpCodes.Ret));
        if(OriginalTextureReturnBodyFamily(traced,mod)!="original_method_multiple_or_missing_returns")
            throw new InvalidOperationException("multiple_returns_must_remain_unresolved");
        // CALLVIRT with an ORIGINAL NONVIRTUAL instance method has a fixed
        // static body (null-check), unlike a genuinely virtual method.
        var instanceGetter=new MethodDefinition("SourceFreeNonvirtualGetter",
            Mono.Cecil.MethodAttributes.Public,tex);
        owner.Methods.Add(instanceGetter);
        instanceGetter.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,fixtureRtField));
        instanceGetter.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        stream[2]=Instruction.Create(OpCodes.Callvirt,instanceGetter);
        traced=BacktraceBlitSource(fixtureMethod,6);
        if(traced.Role!="Texture" ||
           OriginalTextureReturnBodyFamily(traced,mod)!="original_method_static_field_return")
            throw new InvalidOperationException("callvirt_nonvirtual_body_must_be_statically_traceable");
        instanceGetter.IsVirtual=true;
        if(OriginalTextureReturnBodyFamily(traced,mod)!="virtual_dispatch_unresolved")
            throw new InvalidOperationException("virtual_dispatch_must_not_pick_a_body");
        instanceGetter.IsVirtual=false;
        instanceGetter.Body.Instructions.Insert(0,Instruction.Create(OpCodes.Br_S,instanceGetter.Body.Instructions[0]));
        if(OriginalTextureReturnBodyFamily(traced,mod)!="original_method_branch_flow")
            throw new InvalidOperationException("branchy_body_must_remain_unresolved");
        // Reachability is stronger than a text-only predecessor guess:
        // two controlled branches can both end in typed static source loads.
        var branchGetter=new MethodDefinition("SourceFreeBranchGetter",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,tex);
        owner.Methods.Add(branchGetter);
        var branchBody=branchGetter.Body.Instructions;
        var sideA=Instruction.Create(OpCodes.Ldsfld,fixtureRtField);
        var retA=Instruction.Create(OpCodes.Ret);
        var sideB=Instruction.Create(OpCodes.Ldsfld,fixtureRtField);
        var retB=Instruction.Create(OpCodes.Ret);
        branchBody.Add(Instruction.Create(OpCodes.Ldc_I4_1));
        branchBody.Add(Instruction.Create(OpCodes.Brtrue_S,sideB));
        branchBody.Add(sideA);branchBody.Add(retA);branchBody.Add(sideB);branchBody.Add(retB);
        if(ReachableReturnTopology(branchGetter)!="cfg_syntactic_static_texture_field")
            throw new InvalidOperationException("branch_return_static_predecessors_not_detected");
        branchBody[4]=Instruction.Create(OpCodes.Ldnull);
        // Update the conditional target to the replaced instruction.
        branchBody[1].Operand=branchBody[4];
        if(ReachableReturnTopology(branchGetter)!="cfg_mixed_syntactic_return_predecessors")
            throw new InvalidOperationException("branch_mixed_return_predecessor_not_rejected");
        var jumpToRet=Instruction.Create(OpCodes.Br_S,retB);
        branchBody[4]=jumpToRet;
        branchBody[1].Operand=jumpToRet;
        if(ReachableReturnTopology(branchGetter)!="cfg_mixed_syntactic_return_predecessors")
            throw new InvalidOperationException("direct_ret_branch_must_not_forge_producer");
        // Both a direct jump and a second incoming edge reach the same ret.
        // A textual predecessor must never be reported as unique here.
        branchBody[4]=Instruction.Create(OpCodes.Ldsfld,fixtureRtField);
        branchBody[3]=Instruction.Create(OpCodes.Br_S,retB);
        branchBody[1].Operand=retB;
        if(ReachableReturnTopology(branchGetter)!="cfg_multiple_or_entry_return_predecessors")
            throw new InvalidOperationException("return_phi_must_remain_unresolved");
        branchBody[3]=retA;
        branchBody[4]=Instruction.Create(OpCodes.Br_S,Instruction.Create(OpCodes.Nop));
        branchBody[1].Operand=branchBody[4];
        if(ReachableReturnTopology(branchGetter)!="cfg_malformed_graph")
            throw new InvalidOperationException("detached_target_must_be_rejected");
        branchBody[4]=Instruction.Create(OpCodes.Ldsfld,fixtureRtField);
        branchBody[1].Operand=branchBody[4];
        var switchBranch=Instruction.Create(OpCodes.Switch,new[]{branchBody[4]});
        branchBody[1]=switchBranch;
        if(ReachableReturnTopology(branchGetter)!="cfg_syntactic_static_texture_field")
            throw new InvalidOperationException("switch_return_paths_not_counted");
        switchBranch.Operand=new[]{Instruction.Create(OpCodes.Nop)};
        if(ReachableReturnTopology(branchGetter)!="cfg_malformed_graph")
            throw new InvalidOperationException("detached_switch_target_not_rejected");
        // A synthetic exception region remains blocked regardless of returns.
        branchGetter.Body.ExceptionHandlers.Add(new ExceptionHandler(ExceptionHandlerType.Finally));
        if(ReachableReturnTopology(branchGetter)!="cfg_exception_regions")
            throw new InvalidOperationException("exception_return_paths_must_remain_unresolved");
        // Independent forward abstract stack+local dataflow synthetic fixtures.
        // Same family across two original CIL return paths is NOT proof of
        // identical field tokens, heap objects or crosspass texture instances.
        var valueGetter=new MethodDefinition("SyntheticValueReturnJoin",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,tex);
        owner.Methods.Add(valueGetter);
        valueGetter.Body.Variables.Add(new VariableDefinition(tex));
        var v=valueGetter.Body.Instructions;
        var vloadA=Instruction.Create(OpCodes.Ldloc_0);
        var vloadB=Instruction.Create(OpCodes.Ldloc_0);
        v.Add(Instruction.Create(OpCodes.Ldsfld,fixtureRtField));
        v.Add(Instruction.Create(OpCodes.Stloc_0));
        v.Add(Instruction.Create(OpCodes.Ldc_I4_1));
        v.Add(Instruction.Create(OpCodes.Brtrue_S,vloadB));
        v.Add(vloadA);
        v.Add(Instruction.Create(OpCodes.Ret));
        v.Add(vloadB);
        v.Add(Instruction.Create(OpCodes.Ret));
        if(ReachableReturnValueFlow(valueGetter)!="value_static_field_category_only")
            throw new InvalidOperationException("return_value_local_join_must_preserve_category");
        v[6]=Instruction.Create(OpCodes.Ldnull);
        v[3].Operand=v[6];
        if(ReachableReturnValueFlow(valueGetter)!="value_mixed_or_joined")
            throw new InvalidOperationException("return_value_mixed_paths_must_not_claim_field");
        v[6]=Instruction.Create(OpCodes.Ldloc_0);
        v[3].Operand=v[6];
        var sharedRet=Instruction.Create(OpCodes.Ret);
        v.Clear();
        v.Add(Instruction.Create(OpCodes.Ldc_I4_0));
        var ifTrue=Instruction.Create(OpCodes.Ldsfld,fixtureRtField);
        v.Add(Instruction.Create(OpCodes.Brtrue_S,ifTrue));
        v.Add(Instruction.Create(OpCodes.Ldnull));
        v.Add(Instruction.Create(OpCodes.Br_S,sharedRet));
        v.Add(ifTrue);
        v.Add(sharedRet);
        if(ReachableReturnValueFlow(valueGetter)!="value_mixed_or_joined")
            throw new InvalidOperationException("return_stack_phi_must_not_be_proven_same");
        v[1].Operand=Instruction.Create(OpCodes.Nop);
        if(ReachableReturnValueFlow(valueGetter)!="value_bad_target")
            throw new InvalidOperationException("return_bad_branch_target_not_rejected");
        v[1].Operand=ifTrue;
        valueGetter.Body.ExceptionHandlers.Add(new ExceptionHandler(ExceptionHandlerType.Finally));
        if(ReachableReturnValueFlow(valueGetter)!="value_exception_regions")
            throw new InvalidOperationException("return_eh_region_must_not_be_traced");
        var opaqueGetter=new MethodDefinition("OpaqueNestedSyntheticCall",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,tex);
        owner.Methods.Add(opaqueGetter);
        opaqueGetter.Body.Instructions.Add(Instruction.Create(OpCodes.Call,getter));
        opaqueGetter.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        if(ReachableReturnValueFlow(opaqueGetter)!="value_nested_call_untraced")
            throw new InvalidOperationException("nested_call_not_instance_proof");

    }

    public static int Main(string[] args)
    {
        if(args.Length==1 && args[0]=="--selftest")
        {
            try{ SelfTest(); Console.WriteLine("T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS"); return 0; }
            catch { Console.WriteLine("T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_BLOCKED");return 2;}
        }
        try
        {
            if(args.Length!=4)throw new InvalidOperationException();
            var dll=new FileInfo(args[0]);
            var name=new FileInfo(args[1]);
            var output=new FileInfo(args[2]);
            if(!dll.Exists||dll.Length!=3211776||!name.Exists||name.Length is <1 or >1024 ||
               output.Exists||output.Directory is null||!output.Directory.Exists||
               !System.Text.RegularExpressions.Regex.IsMatch(args[3], "^[a-f0-9]{64}$"))
                throw new InvalidOperationException();
            string actual=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(dll.FullName))).ToLowerInvariant();
            if(!string.Equals(actual,args[3],StringComparison.Ordinal))throw new InvalidOperationException();
            string originalName=File.ReadAllText(name.FullName);
            if(originalName.Length is <1 or >256 || originalName.IndexOfAny(new[]{'\0','\r','\n'})>=0)
                throw new InvalidOperationException();
            using var asm=AssemblyDefinition.ReadAssembly(dll.FullName,new ReaderParameters{InMemory=true,ReadSymbols=false});
            string safe=JsonSerializer.Serialize(Scan(asm,originalName));
            if(safe.Length>4096)throw new InvalidOperationException();
            File.WriteAllText(output.FullName,safe+"\n");
            Console.WriteLine("T2_CECIL_ORIGINAL_BLIT_SAFE_RESULT_READY private_content_not_printed=true");
            return 0;
        }
        catch
        {
            Console.WriteLine("T2_CECIL_ORIGINAL_BLIT_BLOCKED private_content_not_printed=true");
            return 2;
        }
    }
}
