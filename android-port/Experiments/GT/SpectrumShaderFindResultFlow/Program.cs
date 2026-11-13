// GT: count source-authentic Spectrum Shader.Find return consumption in managed IL.
// SHA-original source input; no class/method/field names, IL or Shader source exported.
// Field->Material ctor is a source-IL candidate, NOT Unity rendering proof.
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const string ShaderType = "UnityEngine.Shader";
    private static bool TypedFind(Instruction x) =>
        x.OpCode.Code == Code.Call && x.Operand is MethodReference m &&
        m.Name == "Find" && m.DeclaringType.FullName == ShaderType &&
        m.ReturnType.FullName == ShaderType && !m.HasThis &&
        m.Parameters.Count == 1 &&
        m.Parameters[0].ParameterType.FullName == "System.String";

    private static bool Literal(Instruction x, string target) =>
        x.OpCode.Code == Code.Ldstr && x.Operand is string s &&
        string.Equals(s, target, StringComparison.Ordinal);

    private static bool MaterialShaderCtor(Instruction x) =>
        x.OpCode.Code == Code.Newobj && x.Operand is MethodReference m &&
        m.DeclaringType.FullName == "UnityEngine.Material" &&
        m.Name == ".ctor" && m.Parameters.Count == 1 &&
        m.Parameters[0].ParameterType.FullName == ShaderType;

    private static int SkipNops(IList<Instruction> il, int idx)
    {
        int n = 0;
        while(idx < il.Count && il[idx].OpCode.Code == Code.Nop && n++ < 4) idx++;
        return idx;
    }


    private static VariableDefinition? TypedShaderLocal(MethodDefinition method, Instruction ins, bool load)
    {
        if(!method.HasBody) return null;
        int idx = ins.OpCode.Code switch
        {
            Code.Stloc_0 when !load => 0, Code.Stloc_1 when !load => 1,
            Code.Stloc_2 when !load => 2, Code.Stloc_3 when !load => 3,
            Code.Ldloc_0 when load => 0, Code.Ldloc_1 when load => 1,
            Code.Ldloc_2 when load => 2, Code.Ldloc_3 when load => 3,
            _ => -1
        };
        if(idx<0)
        {
            var code=ins.OpCode.Code;
            if(load ? code is Code.Ldloc or Code.Ldloc_S
                    : code is Code.Stloc or Code.Stloc_S)
                idx=ins.Operand is VariableDefinition v ? v.Index : -1;
        }
        if(idx<0 || idx>=method.Body.Variables.Count)return null;
        var local=method.Body.Variables[idx];
        return local.VariableType.FullName==ShaderType ? local : null;
    }

    private static bool TypedSingleShaderCall(Instruction x) =>
        x.OpCode.Code is Code.Call or Code.Callvirt &&
        x.Operand is MethodReference m &&
        m.Parameters.Count==1 &&
        m.Parameters[0].ParameterType.FullName==ShaderType;

    private static bool Direct(IList<Instruction> il, int at, string name)
    {
        int p = at-1,n=0;
        while(p>=0 && il[p].OpCode.Code == Code.Nop && n++<4) p--;
        return p>=0 && Literal(il[p],name);
    }

    // Only classify the immediate, typed consumer shape of a source-local
    // load. No method/field/IL identifiers leave this tool. A predicate is
    // not a Material/Graphics binding and an alias still needs more tracing.
    private static string SafeShaderLocalConsumer(IList<Instruction> il, int load)
    {
        int idx = SkipNops(il, load+1);
        if(idx>=il.Count)return "unclassified";
        var inst=il[idx];
        if(inst.OpCode.Code is Code.Brtrue or Code.Brtrue_S or
            Code.Brfalse or Code.Brfalse_S)return "reference_branch_guard";
        if(inst.OpCode.Code==Code.Pop)return "discard";
        if(inst.OpCode.Code is Code.Stloc or Code.Stloc_S or
            Code.Stloc_0 or Code.Stloc_1 or Code.Stloc_2 or Code.Stloc_3)
            return "local_alias_candidate";
        if(inst.OpCode.Code==Code.Ldnull)
        {
            int pair=SkipNops(il,idx+1);
            if(pair<il.Count)
            {
                var c=il[pair];
                if(c.OpCode.Code==Code.Ceq)return "null_equality_check";
                if(c.OpCode.Code is Code.Call or Code.Callvirt &&
                    c.Operand is MethodReference comparison &&
                    comparison.DeclaringType.FullName=="UnityEngine.Object" &&
                    comparison.Name is "op_Equality" or "op_Inequality" &&
                    comparison.Parameters.Count==2 &&
                    comparison.Parameters.All(p=>p.ParameterType.FullName=="UnityEngine.Object"))
                    return "unity_object_null_comparison";
            }
        }
        if(inst.OpCode.Code is Code.Call or Code.Callvirt &&
            inst.Operand is MethodReference method)
        {
            if(method.DeclaringType.FullName=="UnityEngine.Object" &&
                method.Name=="op_Implicit" &&
                method.ReturnType.FullName=="System.Boolean" &&
                method.Parameters.Count==1 &&
                method.Parameters[0].ParameterType.FullName=="UnityEngine.Object")
                return "unity_object_truthiness";
            if(method.HasThis && (method.DeclaringType.FullName==ShaderType ||
                method.DeclaringType.FullName=="UnityEngine.Object"))
                return "shader_instance_receiver";
            if(method.Parameters.Any(p=>p.ParameterType.FullName==ShaderType))
                return "multi_parameter_shader_call_candidate";
            return "other_method_call_unproven_stack_binding";
        }
        if(inst.OpCode.Code is Code.Ldarg or Code.Ldarg_S or
            Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3 or
            Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or Code.Ldloc_1 or
            Code.Ldloc_2 or Code.Ldloc_3 or Code.Ldnull or Code.Ldstr or
            Code.Ldc_I4 or Code.Ldc_I4_S or Code.Ldc_I4_0 or Code.Ldc_I4_1 or
            Code.Ldc_I4_2 or Code.Ldc_I4_3 or Code.Ldc_I4_4 or Code.Ldc_I4_5 or
            Code.Ldc_I4_6 or Code.Ldc_I4_7 or Code.Ldc_I4_8 or
            Code.Ldc_I4_M1 or Code.Ldc_I8 or Code.Ldc_R4 or Code.Ldc_R8)
            return "additional_stack_operand_pending";
        if(inst.OpCode.Code is Code.Ldfld or Code.Ldsfld)
            return "field_read_candidate";
        if(inst.OpCode.Code is Code.Stfld or Code.Stsfld)
            return "field_store_candidate";
        if(inst.OpCode.Code is Code.Newobj) return "constructor_candidate";
        if(inst.OpCode.Code is Code.Dup) return "duplicate_stack_reference";
        if(inst.OpCode.Code is Code.Ceq or Code.Cgt or Code.Clt)
            return "comparison_consumer";
        if(inst.OpCode.Code is Code.Castclass or Code.Isinst)
            return "runtime_reference_type_check";
        if(inst.OpCode.Code is Code.Box or Code.Unbox_Any)
            return "boxing_or_unboxing_candidate";
        if(inst.OpCode.Code is Code.Br or Code.Br_S or Code.Leave or Code.Leave_S)
            return "unconditional_branch_after_load";
        return "unclassified";
    }

    private static bool ImmediateCtorOwnShaderFieldStore(
        IList<Instruction> il, int storeAt, MethodDefinition ctor)
    {
        if(ctor.IsStatic || ctor.Parameters.Count!=3 || storeAt<2 ||
           il[storeAt].OpCode.Code!=Code.Stfld ||
           il[storeAt].Operand is not FieldReference fr ||
           fr.FieldType.FullName!=ShaderType)
            return false;
        int value=storeAt-1;
        for(int n=0;value>=0 && il[value].OpCode.Code==Code.Nop && n<4;n++)
            value--;
        if(value<1)return false;
        var last=il[value];
        // Instance ctor uses ldarg.3 for the third formal parameter.
        bool lastArg=last.OpCode.Code==Code.Ldarg_3 ||
            (last.OpCode.Code is Code.Ldarg or Code.Ldarg_S &&
             last.Operand is ParameterDefinition p && p.Index==2 &&
             p.ParameterType.FullName==ShaderType);
        int receiver=value-1;
        for(int n=0;receiver>=0 && il[receiver].OpCode.Code==Code.Nop && n<4;n++)
            receiver--;
        if(!lastArg || receiver<0 || il[receiver].OpCode.Code!=Code.Ldarg_0)
            return false;
        return fr.DeclaringType.FullName==ctor.DeclaringType.FullName;
    }

    private static FieldDefinition? ResolvedShaderField(Instruction x, ModuleDefinition module)
    {
        if(x.OpCode.Code is not (Code.Stfld or Code.Stsfld or Code.Ldfld or Code.Ldsfld))
            return null;
        if(x.Operand is not FieldReference fr || fr.FieldType.FullName != ShaderType)
            return null;
        try
        {
            var def=fr.Resolve();
            return def is not null && def.Module==module && def.FieldType.FullName==ShaderType
                ? def : null;
        }
        catch(AssemblyResolutionException) { return null; }
        catch(ResolutionException) { return null; }
    }

    private static IEnumerable<TypeDefinition> Types(TypeDefinition t)
    {
        yield return t;
        foreach(var n in t.NestedTypes)
            foreach(var item in Types(n)) yield return item;
    }

    private static object Scan(AssemblyDefinition asm, string target)
    {
        var methods=asm.Modules.SelectMany(m=>m.Types.SelectMany(Types))
            .SelectMany(t=>t.Methods).Where(m=>m.HasBody).ToArray();
        int sourceLiterals=0,totalTypedFind=0,directFind=0;
        var sources=new List<(MethodDefinition Method,int At,FieldDefinition? Field,VariableDefinition? Local,string Kind)>();
        foreach(var m in methods)
        {
            var il=m.Body.Instructions;
            for(int i=0;i<il.Count;i++)
            {
                if(Literal(il[i],target)) sourceLiterals++;
                if(!TypedFind(il[i])) continue;
                totalTypedFind++;
                if(!Direct(il,i,target)) continue;
                directFind++;
                int n=SkipNops(il,i+1);
                string kind="unresolved";
                FieldDefinition? f=null;
                VariableDefinition? local=null;
                if(n<il.Count)
                {
                    if(il[n].OpCode.Code is Code.Stfld or Code.Stsfld)
                    {
                        f=ResolvedShaderField(il[n],m.Module);
                        kind=f is null ? "unresolved" :
                            (il[n].OpCode.Code==Code.Stfld ? "instance_shader_field" : "static_shader_field");
                    }
                    else if(il[n].OpCode.Code is Code.Stloc or Code.Stloc_S or
                            Code.Stloc_0 or Code.Stloc_1 or Code.Stloc_2 or Code.Stloc_3)
                    {
                        local=TypedShaderLocal(m,il[n],false);
                        kind=local is null?"unresolved":"shader_local_unfollowed";
                    }
                    else if(il[n].OpCode.Code==Code.Ret && m.ReturnType.FullName==ShaderType)
                        kind="shader_return";
                    else if(il[n].OpCode.Code==Code.Pop)
                        kind="discarded_pop";
                    else if(MaterialShaderCtor(il[n]))
                        kind="direct_material_constructor";
                }
                sources.Add((m,i,f,local,kind));
            }
        }
        // Fail closed if new source identity/permutation changed. This count is
        // independently established by CI43300958608 and is not a guessed call.
        if(sourceLiterals!=1 || directFind!=1 || sources.Count!=1)
            throw new InvalidOperationException("source_Spectrum_typed_Find_identity_drift");
        var source=sources[0];
        int resolvedField=source.Field is null?0:1;
        int fieldReads=0,fieldReadMethods=0,fieldToMaterialCtor=0;
        int fieldReaderMethodsWithCtor=0;
        if(source.Field is not null)
        {
            foreach(var method in methods)
            {
                var il=method.Body.Instructions;
                int inMethod=0;
                for(int i=0;i<il.Count;i++)
                {
                    if(il[i].OpCode.Code is not (Code.Ldfld or Code.Ldsfld))
                        continue;
                    var def=ResolvedShaderField(il[i],method.Module);
                    if(def!=source.Field)continue;
                    inMethod++;
                    int j=SkipNops(il,i+1);
                    if(j<il.Count && MaterialShaderCtor(il[j]))fieldToMaterialCtor++;
                }
                if(inMethod>0)
                {
                    fieldReads+=inMethod;fieldReadMethods++;
                    if(il.Any(MaterialShaderCtor))fieldReaderMethodsWithCtor++;
                }
            }
        }
        // Follow the exact typed source shader-local in its original method.
        // Stop at the first control-flow boundary or local overwrite; linear
        // candidates must never be promoted to interprocedural runtime proof.
        int sourceLocalResolved=source.Local is null?0:1;
        int localLinearLoads=0,localLinearReturns=0,localLinearMaterialCtors=0;
        int localLinearShaderFieldStores=0,localLinearOneShaderCallArgs=0;
        int localLinearOtherConsumers=0,localLinearBoundaries=0,localOverwrites=0;
        int localCfgReachedInstructionCount=0,localCfgBranchNodes=0;
        int localCfgLoadsWithNoOverwriteOnSomePath=0;
        int localCfgShaderReturnCandidates=0,localCfgMaterialCtorCandidates=0;
        int localCfgFieldStoreCandidates=0,localCfgTypedShaderCallCandidates=0;
        int localCfgUnclassifiedConsumers=0,localCfgOverwriteBoundaries=0;
        int localCfgBranchGuardConsumers=0,localCfgUnityObjectTruthiness=0;
        int localCfgNullEqualityConsumers=0,localCfgUnityObjectNullComparison=0;
        int localCfgShaderInstanceReceivers=0,localCfgAliases=0,localCfgDiscards=0;
        int localCfgExtraStackOperand=0,localCfgFieldRead=0,localCfgFieldStore=0;
        int localCfgConstructor=0,localCfgDuplicate=0,localCfgComparison=0;
        int localCfgRuntimeTypeCheck=0,localCfgBoxing=0,localCfgUnconditionalBranch=0;
        int localCfgOtherMethodCall=0,localCfgMultiArgShaderCall=0;
        int localCfgCtorExactMaterial=0,localCfgCtorLastExactShader=0;
        int localCfgCtorHasExactShader=0,localCfgCtorGameOwned=0;
        int localCfgCtorUnityEngineOther=0,localCfgCtorOther=0;
        int localCfgCtorParameterCount=0;
        int localCfgOwnCtorResolvedWithBody=0,localCfgOwnCtorBodyInstructions=0;
        int localCfgOwnCtorShaderFieldStoreCandidates=0;
        int localCfgOwnCtorDirectLastShaderArgFieldStores=0;
        int localCfgOwnCtorNewUnityMaterialShader=0;
        int localCfgOwnCtorUnityMaterialShaderSetterCalls=0;
        int localCfgOwnCtorGraphicsCalls=0,localCfgOwnCtorRenderTextureCalls=0;
        if(source.Local is not null)
        {
            var il=source.Method.Body.Instructions;
            int store=SkipNops(il,source.At+1);
            for(int i=store+1;i<il.Count;i++)
            {
                if(il[i].OpCode.FlowControl is FlowControl.Branch
                    or FlowControl.Cond_Branch or FlowControl.Return
                    or FlowControl.Throw)
                {
                    localLinearBoundaries++;
                    break;
                }
                if(TypedShaderLocal(source.Method,il[i],false)==source.Local)
                {
                    localOverwrites++;
                    break;
                }
                if(TypedShaderLocal(source.Method,il[i],true)!=source.Local)
                    continue;
                localLinearLoads++;
                int j=SkipNops(il,i+1);
                if(j>=il.Count){localLinearOtherConsumers++;continue;}
                Instruction next=il[j];
                if(MaterialShaderCtor(next))localLinearMaterialCtors++;
                else if(next.OpCode.Code==Code.Ret &&
                        source.Method.ReturnType.FullName==ShaderType)
                    localLinearReturns++;
                else if(next.OpCode.Code is Code.Stfld or Code.Stsfld &&
                        ResolvedShaderField(next,source.Method.Module) is not null)
                    localLinearShaderFieldStores++;
                else if(TypedSingleShaderCall(next))
                    localLinearOneShaderCallArgs++;
                else localLinearOtherConsumers++;
            }
            // A conservative intra-procedural graph traversal. Branches and
            // loops are traversed, but local overwrites terminate that path.
            // Source-local loads are CANDIDATES, never runtime truth: CFG
            // path-existence is not proof of actual execution or SSA parity.
            var instructionIndex=il.Select((instruction,index)=>(instruction,index))
                .ToDictionary(x=>x.instruction,x=>x.index);
            var pending=new Stack<int>();
            var visited=new HashSet<int>();
            var recordedLoads=new HashSet<int>();
            pending.Push(store+1);
            void Enqueue(Instruction? instruction)
            {
                if(instruction is null || !instructionIndex.TryGetValue(instruction,out int index))
                    throw new InvalidOperationException("source_CIL_branch_target_unverified");
                pending.Push(index);
            }
            while(pending.Count>0)
            {
                int i=pending.Pop();
                if(i<0 || i>=il.Count || !visited.Add(i))continue;
                if(visited.Count>16384)
                    throw new InvalidOperationException("source_CIL_Cfg_probe_budget_exceeded");
                var inst=il[i];
                if(TypedShaderLocal(source.Method,inst,false)==source.Local)
                {
                    localCfgOverwriteBoundaries++;
                    continue;
                }
                var localLoad=TypedShaderLocal(source.Method,inst,true)==source.Local;
                if(localLoad && recordedLoads.Add(i))
                {
                    localCfgLoadsWithNoOverwriteOnSomePath++;
                    string shape=SafeShaderLocalConsumer(il,i);
                    if(shape=="reference_branch_guard")localCfgBranchGuardConsumers++;
                    if(shape=="unity_object_truthiness")localCfgUnityObjectTruthiness++;
                    if(shape=="null_equality_check")localCfgNullEqualityConsumers++;
                    if(shape=="unity_object_null_comparison")localCfgUnityObjectNullComparison++;
                    if(shape=="shader_instance_receiver")localCfgShaderInstanceReceivers++;
                    if(shape=="local_alias_candidate")localCfgAliases++;
                    if(shape=="discard")localCfgDiscards++;
                    if(shape=="additional_stack_operand_pending")localCfgExtraStackOperand++;
                    if(shape=="field_read_candidate")localCfgFieldRead++;
                    if(shape=="field_store_candidate")localCfgFieldStore++;
                    if(shape=="constructor_candidate")localCfgConstructor++;
                    if(shape=="constructor_candidate")
                    {
                        int ctorAt=SkipNops(il,i+1);
                        if(il[ctorAt].Operand is not MethodReference constructor ||
                           constructor.Name!=".ctor")
                            throw new InvalidOperationException("source_CIL_ctor_operand_invalid");
                        localCfgCtorParameterCount+=constructor.Parameters.Count;
                        if(constructor.DeclaringType.FullName=="UnityEngine.Material")
                            localCfgCtorExactMaterial++;
                        else if(constructor.DeclaringType.Namespace.StartsWith("UnityEngine",
                                 StringComparison.Ordinal))
                            localCfgCtorUnityEngineOther++;
                        else if(constructor.DeclaringType.Scope is ModuleDefinition)
                            localCfgCtorGameOwned++;
                        else
                            localCfgCtorOther++;
                        if(constructor.Parameters.Any(p=>p.ParameterType.FullName==ShaderType))
                            localCfgCtorHasExactShader++;
                        if(constructor.Parameters.Count>0 &&
                           constructor.Parameters[^1].ParameterType.FullName==ShaderType)
                            localCfgCtorLastExactShader++;
                        // Follow the *original* same-module constructor, never
                        // infer its implementation from a Unity API guess.
                        if(constructor.DeclaringType.Scope is ModuleDefinition)
                        {
                            MethodDefinition? originalCtor;
                            try {originalCtor=constructor.Resolve();}
                            catch(AssemblyResolutionException) {originalCtor=null;}
                            catch(ResolutionException) {originalCtor=null;}
                            if(originalCtor is not null &&
                               originalCtor.Module==source.Method.Module &&
                               originalCtor.HasBody)
                            {
                                localCfgOwnCtorResolvedWithBody++;
                                var ctorIl=originalCtor.Body.Instructions;
                                localCfgOwnCtorBodyInstructions+=ctorIl.Count;
                                for(int j=0;j<ctorIl.Count;j++)
                                {
                                    var ci=ctorIl[j];
                                    if(ci.OpCode.Code==Code.Stfld &&
                                       ci.Operand is FieldReference fr &&
                                       fr.FieldType.FullName==ShaderType)
                                    {
                                        localCfgOwnCtorShaderFieldStoreCandidates++;
                                        if(ImmediateCtorOwnShaderFieldStore(
                                            ctorIl,j,originalCtor))
                                            localCfgOwnCtorDirectLastShaderArgFieldStores++;
                                    }
                                    if(MaterialShaderCtor(ci))
                                        localCfgOwnCtorNewUnityMaterialShader++;
                                    if(ci.OpCode.Code is Code.Call or Code.Callvirt &&
                                       ci.Operand is MethodReference call)
                                    {
                                        if(call.DeclaringType.FullName=="UnityEngine.Material" &&
                                           call.Name=="set_shader" &&
                                           call.Parameters.Count==1 &&
                                           call.Parameters[0].ParameterType.FullName==ShaderType)
                                            localCfgOwnCtorUnityMaterialShaderSetterCalls++;
                                        if(call.DeclaringType.FullName=="UnityEngine.Graphics")
                                            localCfgOwnCtorGraphicsCalls++;
                                        if(call.DeclaringType.FullName=="UnityEngine.RenderTexture")
                                            localCfgOwnCtorRenderTextureCalls++;
                                    }
                                }
                            }
                        }
                    }
                    if(shape=="duplicate_stack_reference")localCfgDuplicate++;
                    if(shape=="comparison_consumer")localCfgComparison++;
                    if(shape=="runtime_reference_type_check")localCfgRuntimeTypeCheck++;
                    if(shape=="boxing_or_unboxing_candidate")localCfgBoxing++;
                    if(shape=="unconditional_branch_after_load")localCfgUnconditionalBranch++;
                    if(shape=="other_method_call_unproven_stack_binding")localCfgOtherMethodCall++;
                    if(shape=="multi_parameter_shader_call_candidate")localCfgMultiArgShaderCall++;
                    int next=SkipNops(il,i+1);
                    if(next>=il.Count)localCfgUnclassifiedConsumers++;
                    else if(MaterialShaderCtor(il[next]))localCfgMaterialCtorCandidates++;
                    else if(il[next].OpCode.Code==Code.Ret &&
                            source.Method.ReturnType.FullName==ShaderType)
                        localCfgShaderReturnCandidates++;
                    else if(il[next].OpCode.Code is Code.Stfld or Code.Stsfld &&
                            ResolvedShaderField(il[next],source.Method.Module) is not null)
                        localCfgFieldStoreCandidates++;
                    else if(TypedSingleShaderCall(il[next]))
                        localCfgTypedShaderCallCandidates++;
                    else localCfgUnclassifiedConsumers++;
                }
                var flow=inst.OpCode.FlowControl;
                if(flow is FlowControl.Return or FlowControl.Throw)continue;
                if(flow==FlowControl.Branch)
                {
                    localCfgBranchNodes++;
                    Enqueue(inst.Operand as Instruction);
                    continue;
                }
                if(flow==FlowControl.Cond_Branch)
                {
                    localCfgBranchNodes++;
                    if(inst.Operand is Instruction branchTarget) Enqueue(branchTarget);
                    else if(inst.Operand is Instruction[] targets)
                    {
                        foreach(var targetOfSwitch in targets)Enqueue(targetOfSwitch);
                    }
                    else throw new InvalidOperationException("source_conditional_branch_target_invalid");
                }
                if(i+1<il.Count)pending.Push(i+1);
            }
            localCfgReachedInstructionCount=visited.Count;
        }
        return new {
            status="SOURCE_AUTHENTIC_SPECTRUM_TYPED_SHADERFIND_RESULT_FLOW_CENSUS",
            original_Spectrum_Shader_mName_SHA_authenticated=true,
            original_Assembly_CSharp_DLL_SHA_authenticated=true,
            original_compiled_method_bodies_scanned=methods.Length,
            total_typed_UnityEngine_Shader_Find_calls=totalTypedFind,
            exact_original_name_literal_sites=sourceLiterals,
            exact_original_name_direct_typed_Shader_Find_calls=directFind,
            source_return_immediate_instance_shader_field=source.Kind=="instance_shader_field"?1:0,
            source_return_immediate_static_shader_field=source.Kind=="static_shader_field"?1:0,
            source_return_immediate_shader_local_unfollowed=source.Kind=="shader_local_unfollowed"?1:0,
            source_return_immediate_shader_return=source.Kind=="shader_return"?1:0,
            source_return_immediate_direct_material_constructor=source.Kind=="direct_material_constructor"?1:0,
            source_return_immediate_discarded=source.Kind=="discarded_pop"?1:0,
            source_return_immediate_unresolved=source.Kind=="unresolved"?1:0,
            original_Shader_field_definition_resolved=resolvedField,
            original_Shader_field_loads=fieldReads,
            original_Shader_field_reader_methods=fieldReadMethods,
            original_Shader_field_reader_methods_containing_Material_Shader_ctor=fieldReaderMethodsWithCtor,
            original_Shader_field_loads_directly_into_Material_ctor=fieldToMaterialCtor,
            original_source_Shader_local_resolved=sourceLocalResolved,
            source_local_linear_basic_block_loads=localLinearLoads,
            source_local_linear_shader_returns=localLinearReturns,
            source_local_linear_Material_Shader_ctor_candidates=localLinearMaterialCtors,
            source_local_linear_typed_Shader_field_store_candidates=localLinearShaderFieldStores,
            source_local_linear_typed_oneShader_argument_call_candidates=localLinearOneShaderCallArgs,
            source_local_linear_unclassified_uses=localLinearOtherConsumers,
            source_local_linear_control_flow_boundaries=localLinearBoundaries,
            source_local_linear_overwrites=localOverwrites,
            source_local_interprocedural_runtime_equivalence_proven=false,
            source_local_cfg_reached_instructions=localCfgReachedInstructionCount,
            source_local_cfg_branch_nodes=localCfgBranchNodes,
            source_local_cfg_loads_before_overwrite_on_some_path=localCfgLoadsWithNoOverwriteOnSomePath,
            source_local_cfg_shader_return_candidates=localCfgShaderReturnCandidates,
            source_local_cfg_Material_ctor_candidates=localCfgMaterialCtorCandidates,
            source_local_cfg_typed_Shader_field_store_candidates=localCfgFieldStoreCandidates,
            source_local_cfg_typed_Shader_argument_call_candidates=localCfgTypedShaderCallCandidates,
            source_local_cfg_unclassified_uses=localCfgUnclassifiedConsumers,
            source_local_cfg_actual_next_reference_branch_guard=localCfgBranchGuardConsumers,
            source_local_cfg_actual_next_Unity_Object_truthiness=localCfgUnityObjectTruthiness,
            source_local_cfg_actual_next_null_equality_check=localCfgNullEqualityConsumers,
            source_local_cfg_actual_next_Unity_Object_null_comparison=localCfgUnityObjectNullComparison,
            source_local_cfg_actual_next_Shader_instance_receiver=localCfgShaderInstanceReceivers,
            source_local_cfg_actual_next_local_alias_candidate=localCfgAliases,
            source_local_cfg_actual_next_discarded=localCfgDiscards,
            source_local_cfg_actual_next_additional_stack_operand_pending=localCfgExtraStackOperand,
            source_local_cfg_actual_next_field_read_candidate=localCfgFieldRead,
            source_local_cfg_actual_next_field_store_candidate=localCfgFieldStore,
            source_local_cfg_actual_next_constructor_candidate=localCfgConstructor,
            source_local_cfg_next_ctor_declaring_type_is_UnityEngine_Material=localCfgCtorExactMaterial,
            source_local_cfg_next_ctor_declaring_type_is_other_UnityEngine=localCfgCtorUnityEngineOther,
            source_local_cfg_next_ctor_declaring_type_is_own_managed_module=localCfgCtorGameOwned,
            source_local_cfg_next_ctor_declaring_type_other=localCfgCtorOther,
            source_local_cfg_next_ctor_parameter_count_sum=localCfgCtorParameterCount,
            source_local_cfg_next_ctor_has_exact_UnityEngine_Shader_parameter=localCfgCtorHasExactShader,
            source_local_cfg_next_ctor_last_parameter_exact_Shader=localCfgCtorLastExactShader,
            source_local_cfg_next_own_ctor_resolved_body=localCfgOwnCtorResolvedWithBody,
            source_local_cfg_next_own_ctor_body_instructions=localCfgOwnCtorBodyInstructions,
            source_local_cfg_next_own_ctor_shader_field_stores=localCfgOwnCtorShaderFieldStoreCandidates,
            source_local_cfg_next_own_ctor_direct_last_shader_arg_field_stores=localCfgOwnCtorDirectLastShaderArgFieldStores,
            source_local_cfg_next_own_ctor_Unity_Material_Shader_newobj=localCfgOwnCtorNewUnityMaterialShader,
            source_local_cfg_next_own_ctor_Unity_Material_set_shader_calls=localCfgOwnCtorUnityMaterialShaderSetterCalls,
            source_local_cfg_next_own_ctor_Unity_Graphics_calls=localCfgOwnCtorGraphicsCalls,
            source_local_cfg_next_own_ctor_Unity_RenderTexture_calls=localCfgOwnCtorRenderTextureCalls,
            source_local_cfg_actual_next_duplicate_stack_reference=localCfgDuplicate,
            source_local_cfg_actual_next_comparison_consumer=localCfgComparison,
            source_local_cfg_actual_next_runtime_reference_type_check=localCfgRuntimeTypeCheck,
            source_local_cfg_actual_next_boxing_or_unboxing=localCfgBoxing,
            source_local_cfg_actual_next_unconditional_branch=localCfgUnconditionalBranch,
            source_local_cfg_actual_next_other_method_call=localCfgOtherMethodCall,
            source_local_cfg_actual_next_multi_parameter_Shader_call=localCfgMultiArgShaderCall,
            source_local_cfg_typed_consumer_only_not_Material_or_pixel_proof=true,
            source_local_cfg_local_overwrite_boundaries=localCfgOverwriteBoundaries,
            source_local_cfg_path_existence_only_not_runtime_proof=true,
            exact_original_Material_renderer_assignment_verified=false,
            original_CB0_sampler_RT_binding_verified=false,
            actual_Unity_Shader_Find_executed=false,
            Adreno_water_pixels_verified=false,
            original_identifier_and_IL_exported=false
        };
    }

    private static void SelfTest()
    {
        using var m=ModuleDefinition.CreateModule("synthetic-only",ModuleKind.Dll);
        var shader=new TypeReference("UnityEngine","Shader",m,m.TypeSystem.CoreLibrary);
        var material=new TypeReference("UnityEngine","Material",m,m.TypeSystem.CoreLibrary);
        var find=new MethodReference("Find",shader,shader){HasThis=false};
        find.Parameters.Add(new ParameterDefinition(m.TypeSystem.String));
        var ctor=new MethodReference(".ctor",m.TypeSystem.Void,material){HasThis=true};
        ctor.Parameters.Add(new ParameterDefinition(shader));
        var il=new List<Instruction>{
            Instruction.Create(OpCodes.Ldstr,"SYNTHETIC_ONLY"),
            Instruction.Create(OpCodes.Nop),Instruction.Create(OpCodes.Call,find),
            Instruction.Create(OpCodes.Nop),Instruction.Create(OpCodes.Newobj,ctor)
        };
        var demo=new MethodDefinition("SyntheticControl",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,shader);
        demo.Body.Variables.Add(new VariableDefinition(shader));
        if(!TypedFind(il[2]) || !Direct(il,2,"SYNTHETIC_ONLY") ||
           Direct(il,2,"MISMATCH") || SkipNops(il,3)!=4 || !MaterialShaderCtor(il[4]) ||
           TypedShaderLocal(demo,Instruction.Create(OpCodes.Stloc_0),false) is null ||
           TypedShaderLocal(demo,Instruction.Create(OpCodes.Ldloc_0),true) is null ||
           TypedShaderLocal(demo,Instruction.Create(OpCodes.Ldloc_0),false) is not null ||
           !TypedSingleShaderCall(Instruction.Create(OpCodes.Call,
               new MethodReference("TakeShader",m.TypeSystem.Void,shader){HasThis=false,
                   Parameters={new ParameterDefinition(shader)}})))
            throw new InvalidOperationException("synthetic_dataflow_guard_failed");
        // Synthetic positive and negative source-local consumer controls:
        // same Source Shader local, no original symbol/Shader source output.
        var boolBranch=Instruction.Create(OpCodes.Brtrue_S,Instruction.Create(OpCodes.Ret));
        var nullEq=new List<Instruction>{
            Instruction.Create(OpCodes.Ldloc_0),Instruction.Create(OpCodes.Ldnull),
            Instruction.Create(OpCodes.Ceq)};
        var implicitObject=new TypeReference("UnityEngine","Object",m,m.TypeSystem.CoreLibrary);
        var implicitCall=new MethodReference("op_Implicit",m.TypeSystem.Boolean,implicitObject){
            HasThis=false};
        implicitCall.Parameters.Add(new ParameterDefinition(implicitObject));
        var truthy=new List<Instruction>{
            Instruction.Create(OpCodes.Ldloc_0),Instruction.Create(OpCodes.Call,implicitCall)};
        var nonShader=new List<Instruction>{
            Instruction.Create(OpCodes.Ldloc_0),Instruction.Create(OpCodes.Ldc_I4_1)};
        var syntheticExtraCtor=new MethodReference(".ctor",m.TypeSystem.Void,
            new TypeReference("Synthetic","NotMaterial",m,m.TypeSystem.CoreLibrary)){
            HasThis=true};
        syntheticExtraCtor.Parameters.Add(new ParameterDefinition(shader));
        if(SafeShaderLocalConsumer(new List<Instruction>{
            Instruction.Create(OpCodes.Ldloc_0),
            Instruction.Create(OpCodes.Newobj,syntheticExtraCtor)},0)!="constructor_candidate")
            throw new InvalidOperationException("synthetic_ctor_consumer_classification_failed");
        if(SafeShaderLocalConsumer(new List<Instruction>{
                Instruction.Create(OpCodes.Ldloc_0),boolBranch},0)!="reference_branch_guard" ||
           SafeShaderLocalConsumer(nullEq,0)!="null_equality_check" ||
           SafeShaderLocalConsumer(truthy,0)!="unity_object_truthiness" ||
           SafeShaderLocalConsumer(nonShader,0)!="additional_stack_operand_pending")
            throw new InvalidOperationException("synthetic_source_shader_consumer_guard_failed");
        Console.WriteLine("GT_SPECTRUM_TYPED_RESULTFLOW_SYNTHETIC_PASS");
    }

    private static int Main(string[] args)
    {
        if(args.Length==1 && args[0]=="--selftest")
        {
            try {SelfTest();return 0;}
            catch {Console.WriteLine("GT_SPECTRUM_TYPED_RESULTFLOW_SYNTHETIC_FAIL");return 2;}
        }
        try
        {
            if(args.Length!=3)throw new InvalidOperationException();
            var dll=new FileInfo(args[0]);
            var name=new FileInfo(args[1]);
            var output=new FileInfo(args[2]);
            if(!dll.Exists || dll.Length!=3211776 || !name.Exists ||
               name.Length<1 || name.Length>1024 || output.Exists ||
               output.Directory is null || !output.Directory.Exists)
                throw new InvalidOperationException();
            string target=File.ReadAllText(name.FullName);
            if(string.IsNullOrEmpty(target) || target.Length>256 ||
               target.IndexOfAny(new[]{'\0','\r','\n'})>=0)
                throw new InvalidOperationException();
            using var asm=AssemblyDefinition.ReadAssembly(dll.FullName,
                new ReaderParameters{InMemory=true,ReadSymbols=false});
            string report=JsonSerializer.Serialize(Scan(asm,target));
            if(report.Length>8192)throw new InvalidOperationException();
            File.WriteAllText(output.FullName,report+"\n");
            Console.WriteLine("GT_SPECTRUM_TYPED_RESULTFLOW_SAFE "+report);
            return 0;
        }
        catch
        {
            Console.WriteLine("GT_SPECTRUM_TYPED_RESULTFLOW_BLOCKED source_metadata_private=true");
            return 2;
        }
    }
}
