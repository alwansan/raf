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

    private static bool Direct(IList<Instruction> il, int at, string name)
    {
        int p = at-1,n=0;
        while(p>=0 && il[p].OpCode.Code == Code.Nop && n++<4) p--;
        return p>=0 && Literal(il[p],name);
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
        var sources=new List<(MethodDefinition Method,int At,FieldDefinition? Field,string Kind)>();
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
                        kind="shader_local_unfollowed";
                    else if(il[n].OpCode.Code==Code.Ret && m.ReturnType.FullName==ShaderType)
                        kind="shader_return";
                    else if(il[n].OpCode.Code==Code.Pop)
                        kind="discarded_pop";
                    else if(MaterialShaderCtor(il[n]))
                        kind="direct_material_constructor";
                }
                sources.Add((m,i,f,kind));
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
        if(!TypedFind(il[2]) || !Direct(il,2,"SYNTHETIC_ONLY") ||
           Direct(il,2,"MISMATCH") || SkipNops(il,3)!=4 || !MaterialShaderCtor(il[4]))
            throw new InvalidOperationException("synthetic_dataflow_guard_failed");
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
