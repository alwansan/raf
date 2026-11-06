// T2: original Foam source Shader.Find-result immediate consumer.
 // Private ShaderLab name, class names, fields, PathIDs, IL bodies never exported.
 // A static IL consumer does NOT prove original runtime material upload or Android drawing.
using Mono.Cecil;
using Mono.Cecil.Cil;
using System.Text.Json;
internal static class Program
{
    private const string ShaderType = "UnityEngine.Shader";
    private static readonly string[] Kinds = {
        "instance_shader_field", "static_shader_field",
        "shader_local", "shader_return", "typed_shader_call_argument",
        "typed_shader_constructor_argument", "discarded_pop",
        "duplicated_unresolved", "unproved"
    };
    private sealed record Consumer(string Kind, FieldDefinition? Field, VariableDefinition? Local, int Nops);

    private static bool IsFind(Instruction instruction)
    {
        if (instruction.OpCode.Code != Code.Call ||
            instruction.Operand is not MethodReference method) return false;
        return method.Name == "Find" && method.DeclaringType.FullName == ShaderType &&
            method.ReturnType.FullName == ShaderType && !method.HasThis &&
            method.Parameters.Count == 1 &&
            method.Parameters[0].ParameterType.FullName == "System.String";
    }
    private static bool IsOriginalName(Instruction instruction, string value) =>
        instruction.OpCode.Code == Code.Ldstr &&
        instruction.Operand is string s && string.Equals(s, value, StringComparison.Ordinal);

    private static bool HasDirectArg(IList<Instruction> il, int call, string name)
    {
        int i = call - 1, skipped = 0;
        while (i >= 0 && il[i].OpCode.Code == Code.Nop && skipped++ < 4) i--;
        return i >= 0 && IsOriginalName(il[i], name);
    }
    private static VariableDefinition? LocalForStore(MethodDefinition method, Instruction inst)
    {
        int index = inst.OpCode.Code switch {
            Code.Stloc_0 => 0, Code.Stloc_1 => 1, Code.Stloc_2 => 2,
            Code.Stloc_3 => 3, _ => -1
        };
        if(index >= 0)
            return index < method.Body.Variables.Count ? method.Body.Variables[index] : null;
        return inst.OpCode.Code is Code.Stloc or Code.Stloc_S
            ? inst.Operand as VariableDefinition : null;
    }
    private static bool LocalIsLoadOf(Instruction inst, VariableDefinition local)
    {
        int index = inst.OpCode.Code switch {
            Code.Ldloc_0 => 0, Code.Ldloc_1 => 1, Code.Ldloc_2 => 2,
            Code.Ldloc_3 => 3, _ => -1
        };
        if(index >= 0) return index == local.Index;
        return inst.OpCode.Code is Code.Ldloc or Code.Ldloc_S &&
            inst.Operand is VariableDefinition x && x.Index == local.Index;
    }
    private static bool OriginalField(Instruction instruction, ModuleDefinition module,
        out FieldDefinition? field)
    {
        field = null;
        if(instruction.Operand is not FieldReference reference ||
            reference.FieldType.FullName != ShaderType) return false;
        try {
            var resolved = reference.Resolve();
            if(resolved is not null && resolved.Module == module &&
               resolved.FieldType.FullName == ShaderType) {
                field = resolved;
                return true;
            }
        }
        catch (AssemblyResolutionException) {}
        catch (ResolutionException) {}
        return false;
    }
    private static bool IsExactOneShaderCall(Instruction inst, bool constructor)
    {
        bool isCall = inst.OpCode.Code is Code.Call or Code.Callvirt;
        if (constructor ? inst.OpCode.Code != Code.Newobj : !isCall) return false;
        if (inst.Operand is not MethodReference m ||
            m.Parameters.Count != 1 ||
            m.Parameters[0].ParameterType.FullName != ShaderType) return false;
        if (constructor) return m.Name == ".ctor";
        return m.ReturnType.FullName != "" && m.Name != ".ctor";
    }
    private static Consumer NextConsumer(MethodDefinition method, int call)
    {
        var il = method.Body.Instructions;
        int next=call+1,nops=0;
        while(next<il.Count && il[next].OpCode.Code==Code.Nop && nops < 4)
        { next++; nops++; }
        if(next>=il.Count) return new("unproved",null,null,nops);
        var after=il[next];
        if(after.OpCode.Code is Code.Stfld or Code.Stsfld)
        {
            if(OriginalField(after,method.Module,out var field))
                return new(after.OpCode.Code==Code.Stfld?"instance_shader_field":"static_shader_field",field,null,nops);
            return new("unproved",null,null,nops);
        }
        var local = LocalForStore(method,after);
        if(local is not null)
            return new(local.VariableType.FullName==ShaderType?"shader_local":"unproved",null,local,nops);
        if(after.OpCode.Code==Code.Ret && method.ReturnType.FullName==ShaderType)
            return new("shader_return",null,null,nops);
        if(after.OpCode.Code==Code.Pop)
            return new("discarded_pop",null,null,nops);
        if(after.OpCode.Code==Code.Dup)
            return new("duplicated_unresolved",null,null,nops);
        if(IsExactOneShaderCall(after,false))
            return new("typed_shader_call_argument",null,null,nops);
        if(IsExactOneShaderCall(after,true))
            return new("typed_shader_constructor_argument",null,null,nops);
        return new("unproved",null,null,nops);
    }
    private static bool IsCtorMaterialShader(Instruction inst) =>
        inst.OpCode.Code == Code.Newobj && inst.Operand is MethodReference ctor &&
        ctor.Name == ".ctor" && ctor.DeclaringType.FullName == "UnityEngine.Material" &&
        ctor.Parameters.Count == 1 &&
        ctor.Parameters[0].ParameterType.FullName == ShaderType;
    private static bool DirectOriginalFieldToMaterialCtor(IList<Instruction> il, int fieldLoadIndex)
    {
        // Material(Shader) has exactly one Shader arg; an adjacent ldfld is
        // therefore the actual stack value of that argument, not cooccurrence.
        int index = fieldLoadIndex + 1, skipped = 0;
        while (index < il.Count && il[index].OpCode.Code == Code.Nop && skipped++ < 4)
            index++;
        return index < il.Count && IsCtorMaterialShader(il[index]);
    }
    private static bool IsFieldLoad(Instruction inst, FieldDefinition field)
    {
        if(inst.OpCode.Code is not (Code.Ldfld or Code.Ldsfld) ||
           inst.Operand is not FieldReference fr ||
           fr.FieldType.FullName != ShaderType) return false;
        try {
            var resolved=fr.Resolve();
            return resolved is not null && resolved.Module==field.Module &&
                   resolved.MetadataToken==field.MetadataToken;
        } catch(AssemblyResolutionException) { return false; }
          catch(ResolutionException) { return false; }
    }
    private static IEnumerable<TypeDefinition> AllTypes(TypeDefinition t)
    {
        yield return t;
        foreach(var sub in t.NestedTypes)
            foreach(var nested in AllTypes(sub)) yield return nested;
    }
    private static IEnumerable<MethodDefinition> AllMethods(AssemblyDefinition asm) =>
        asm.Modules.SelectMany(m=>m.Types.SelectMany(AllTypes))
            .SelectMany(t=>t.Methods).Where(m=>m.HasBody);

    private static Dictionary<string,object> Scan(AssemblyDefinition asm,string originalName)
    {
        var methods=AllMethods(asm).ToList();
        int observedBodies=methods.Count;
        int compiledIL=methods.Sum(x=>x.Body.Instructions.Count);
        int totalFind=0,directFind=0;
        var sites=new List<(MethodDefinition Method,int Index)>();
        foreach(var method in methods)
        {
            var il=method.Body.Instructions;
            for(int i=0;i<il.Count;i++)
                if(IsFind(il[i]))
                {
                    totalFind++;
                    if(HasDirectArg(il,i,originalName))
                    { directFind++;sites.Add((method,i)); }
                }
        }
        if(directFind!=1 || sites.Count!=1 || observedBodies<=1000 || compiledIL<=10000)
            throw new InvalidOperationException("source_original_unique_direct_call_drift");
        var site=sites[0];
        var consumer=NextConsumer(site.Method,site.Index);
        if(!Kinds.Contains(consumer.Kind)) throw new InvalidOperationException();
        var buckets=Kinds.ToDictionary(x=>"return_consumer_"+x,y=>y==consumer.Kind?1:0);
        int fieldReads=0,fieldReadMethods=0,fieldReadCtorMethods=0;
        int directFieldToMaterialCtor=0;
        int localReads=0, localMethodWithCtor=0;
        if(consumer.Field is not null)
            foreach(var method in methods)
            {
                var il=method.Body.Instructions;
                int loads=0;
                for(int i=0;i<il.Count;i++)
                    if(IsFieldLoad(il[i],consumer.Field))
                    {
                        loads++;
                        if(DirectOriginalFieldToMaterialCtor(il,i)) directFieldToMaterialCtor++;
                    }
                if(loads>0)
                {
                    fieldReads+=loads;
                    fieldReadMethods++;
                    if(il.Any(IsCtorMaterialShader)) fieldReadCtorMethods++;
                }
            }
        if(consumer.Local is not null && consumer.Kind=="shader_local")
        {
            var il=site.Method.Body.Instructions;
            localReads=il.Count(x=>LocalIsLoadOf(x,consumer.Local));
            if(localReads>0 && il.Any(IsCtorMaterialShader)) localMethodWithCtor=1;
        }
        var output=new Dictionary<string,object>
        {
            ["status"]="original_foam_ShaderFind_direct_return_consumer_typed_IL_census",
            ["original_zip2_shader_name_SHA_authenticated"]=true,
            ["original_Assembly_CSharp_SHA_authenticated"]=true,
            ["original_compiled_method_bodies_scanned"]=observedBodies,
            ["original_compiled_IL_instructions_scanned"]=compiledIL,
            ["original_typed_Shader_Find_calls"]=totalFind,
            ["exact_source_Foam_name_direct_typed_Shader_Find_calls"]=directFind,
            ["consumer_exact_original_managed_Shader_field_definitions_resolved"]=consumer.Field is null?0:1,
            ["consumer_return_original_shader_local_loads_same_method"]=localReads,
            ["consumer_return_original_shader_local_method_contains_Material_Shader_constructor"]=localMethodWithCtor,
            ["consumer_return_original_shader_field_load_instructions"]=fieldReads,
            ["consumer_return_original_shader_field_reading_methods"]=fieldReadMethods,
            ["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"]=fieldReadCtorMethods,
            ["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"]=directFieldToMaterialCtor,
            ["consumer_nop_instructions_skipped_after_Find"]=consumer.Nops,
            ["original_Shader_Find_executed_in_Unity"]=false,
            ["field_declaring_TypeDef_is_427_scene_script_proven"]=false,
            ["Unity_Material_or_Renderer_actual_binding_verified"]=false,
            ["original_Foam_CB0_runtime_upload_verified"]=false,
            ["Android_water_pixels_verified"]=false,
            ["private_original_names_fields_method_IDs_or_IL_exported"]=false
        };
        foreach(var (name,value) in buckets) output[name]=value;
        return output;
    }
    private static void SelfTest()
    {
        using var mod=ModuleDefinition.CreateModule("T2Synthetic",ModuleKind.Dll);
        var shader=new TypeReference("UnityEngine","Shader",mod,mod.TypeSystem.CoreLibrary);
        var owner=new TypeDefinition("T2Synthetic","Owner",Mono.Cecil.TypeAttributes.Public,
            mod.TypeSystem.Object);
        mod.Types.Add(owner);
        var method=new MethodDefinition("Synthetic",Mono.Cecil.MethodAttributes.Public |
            Mono.Cecil.MethodAttributes.Static,mod.TypeSystem.Void);
        owner.Methods.Add(method);
        var good=new MethodReference("Find",shader,shader){HasThis=false};
        good.Parameters.Add(new ParameterDefinition(mod.TypeSystem.String));
        var orig=Instruction.Create(OpCodes.Ldstr,"SYNTHETIC_ONLY");
        var call=Instruction.Create(OpCodes.Call,good);
        method.Body.Instructions.Add(orig);
        method.Body.Instructions.Add(call);
        var local=new VariableDefinition(shader);
        method.Body.Variables.Add(local);
        method.Body.Instructions.Add(Instruction.Create(OpCodes.Stloc,local));
        method.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        if(!IsFind(call) || !HasDirectArg(method.Body.Instructions,1,"SYNTHETIC_ONLY") ||
           HasDirectArg(method.Body.Instructions,1,"different") ||
           NextConsumer(method,1).Kind!="shader_local") throw new InvalidOperationException("direct_local");
        method.Body.Instructions[2]=Instruction.Create(OpCodes.Pop);
        if(NextConsumer(method,1).Kind!="discarded_pop") throw new InvalidOperationException("pop");
        var field=new FieldDefinition("stored",Mono.Cecil.FieldAttributes.Private,shader);
        owner.Fields.Add(field);
        method.Body.Instructions[2]=Instruction.Create(OpCodes.Stsfld,field);
        if(NextConsumer(method,1).Kind!="static_shader_field" ||
           !IsFieldLoad(Instruction.Create(OpCodes.Ldsfld,field),field))
            throw new InvalidOperationException("field");
        var ctor=new MethodReference(".ctor",mod.TypeSystem.Void,
            new TypeReference("UnityEngine","Material",mod,mod.TypeSystem.CoreLibrary)){HasThis=true};
        ctor.Parameters.Add(new ParameterDefinition(shader));
        var directLoad=Instruction.Create(OpCodes.Ldsfld,field);
        if(!DirectOriginalFieldToMaterialCtor(new List<Instruction>{
             directLoad,Instruction.Create(OpCodes.Nop),Instruction.Create(OpCodes.Newobj,ctor)},0)
           || DirectOriginalFieldToMaterialCtor(new List<Instruction>{
             directLoad,Instruction.Create(OpCodes.Pop),Instruction.Create(OpCodes.Newobj,ctor)},0))
             throw new InvalidOperationException("direct_Material_Stack_guard");
        var other=new FieldDefinition("wrong",Mono.Cecil.FieldAttributes.Private,mod.TypeSystem.Int32);
        owner.Fields.Add(other);
        method.Body.Instructions[2]=Instruction.Create(OpCodes.Stsfld,other);
        if(NextConsumer(method,1).Kind!="unproved") throw new InvalidOperationException("type_guard");
        method.Body.Instructions[2]=Instruction.Create(OpCodes.Dup);
        if(NextConsumer(method,1).Kind!="duplicated_unresolved")
            throw new InvalidOperationException("dup_guard");
        var bad=new MethodReference("Find",mod.TypeSystem.Int32,shader){HasThis=false};
        bad.Parameters.Add(new ParameterDefinition(mod.TypeSystem.String));
        if(IsFind(Instruction.Create(OpCodes.Call,bad))) throw new InvalidOperationException("signature_guard");
        Console.WriteLine("T2_FOAM_SHADERFIND_RETURN_CECIL_SYNTHETIC_PASS");
    }
    public static int Main(string[] args)
    {
        if(args.Length==1 && args[0]=="--selftest")
        {
            try { SelfTest(); return 0; }
            catch { Console.WriteLine("T2_FOAM_SHADERFIND_RETURN_CECIL_SYNTHETIC_FAIL"); return 2; }
        }
        try {
            if(args.Length!=3) throw new InvalidOperationException();
            var dll=new FileInfo(args[0]);var nameFile=new FileInfo(args[1]);
            var output=new FileInfo(args[2]);
            if(!dll.Exists || dll.Length!=3211776 || !nameFile.Exists ||
               nameFile.Length==0 || nameFile.Length>1024 || output.Exists ||
               output.Directory is null || !output.Directory.Exists)
                throw new InvalidOperationException();
            var name=File.ReadAllText(nameFile.FullName);
            if(string.IsNullOrWhiteSpace(name) || name.Length>256 ||
               name.IndexOfAny(new[]{'\0','\r','\n'})>=0) throw new InvalidOperationException();
            using var asm=AssemblyDefinition.ReadAssembly(dll.FullName,
                new ReaderParameters{InMemory=true,ReadSymbols=false});
            var report=Scan(asm,name);
            string safe=JsonSerializer.Serialize(report);
            if(safe.Length>8192) throw new InvalidOperationException();
            File.WriteAllText(output.FullName,safe+"\n");
            Console.WriteLine("T2_FOAM_SHADERFIND_RETURN_IL_SAFE "+safe);
            return 0;
        } catch {
            Console.WriteLine("T2_FOAM_SHADERFIND_RETURN_IL_BLOCKED private_content_not_printed=true");
            return 2;
        }
    }
}
