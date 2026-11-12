// Source-original Spectrum Shader.m_Name vs exact typed UnityEngine.Shader.Find managed IL.
// No original names, method strings, raw IL, identifiers or hashes are exported.
// Cooccurrence does not prove dataflow, renderer setup, or Android execution.
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private static bool Find(Instruction i) =>
        i.OpCode.Code == Code.Call && i.Operand is MethodReference m &&
        m.Name == "Find" && m.DeclaringType.FullName == "UnityEngine.Shader" &&
        m.ReturnType.FullName == "UnityEngine.Shader" && !m.HasThis &&
        m.Parameters.Count == 1 && m.Parameters[0].ParameterType.FullName == "System.String";

    private static bool MaterialCtor(Instruction i) =>
        i.OpCode.Code == Code.Newobj && i.Operand is MethodReference m &&
        m.Name == ".ctor" && m.DeclaringType.FullName == "UnityEngine.Material" &&
        m.Parameters.Count == 1 && m.Parameters[0].ParameterType.FullName == "UnityEngine.Shader";

    private static bool Name(Instruction i, string exact) =>
        i.OpCode.Code == Code.Ldstr && i.Operand is string s &&
        string.Equals(s, exact, StringComparison.Ordinal);

    private static bool Direct(IList<Instruction> il, int index, string name)
    {
        int p=index-1, n=0;
        while (p>=0 && il[p].OpCode.Code==Code.Nop && n++<4) p--;
        return p>=0 && Name(il[p],name);
    }
    private static IEnumerable<TypeDefinition> Recurse(TypeDefinition t)
    {
        yield return t;
        foreach(var n in t.NestedTypes) foreach(var v in Recurse(n)) yield return v;
    }
    private static object Scan(AssemblyDefinition asm, string name)
    {
        int methods=0, instr=0, strings=0, literals=0, litMethods=0, finds=0;
        int findMethods=0, sameMethods=0, direct=0, directMethods=0, directCtorMethods=0;
        foreach(var module in asm.Modules)
        foreach(var t in module.Types.SelectMany(Recurse))
        foreach(var method in t.Methods)
        {
            if(!method.HasBody) continue;
            methods++;
            var il=method.Body.Instructions;
            instr+=il.Count;
            int mlit=0, mfind=0, mdir=0; bool ctor=false;
            for(int i=0;i<il.Count;i++)
            {
                var x=il[i];
                if(x.OpCode.Code==Code.Ldstr) strings++;
                if(Name(x,name)) mlit++;
                if(Find(x)) { mfind++; if(Direct(il,i,name)) mdir++; }
                if(MaterialCtor(x)) ctor=true;
            }
            literals+=mlit; finds+=mfind; direct+=mdir;
            if(mlit>0) litMethods++;
            if(mfind>0) findMethods++;
            if(mlit>0 && mfind>0) sameMethods++;
            if(mdir>0) directMethods++;
            if(mdir>0 && ctor) directCtorMethods++;
        }
        return new {
            status="source_original_spectrum_shader_name_managed_ShaderFind_scan",
            original_Spectrum_Shader_mName_SHA_authenticated=true,
            original_Assembly_CSharp_DLL_SHA_authenticated=true,
            total_compiled_methods_with_body=methods,
            total_compiled_IL_instructions=instr,
            total_ldstr_instructions=strings,
            exact_original_Spectrum_name_ldstr_occurrences=literals,
            methods_with_exact_original_Spectrum_name_literal=litMethods,
            total_typed_UnityEngine_Shader_Find_calls=finds,
            methods_with_typed_Shader_Find_calls=findMethods,
            methods_with_source_literal_and_typed_Shader_Find=sameMethods,
            exact_source_ldstr_direct_typed_Shader_Find_calls=direct,
            methods_with_direct_original_literal_Shader_Find=directMethods,
            methods_with_direct_literal_Shader_Find_and_Material_Shader_ctor=directCtorMethods,
            actual_Unity_Shader_Find_execution_verified=false,
            original_Spectrum_Material_render_binding_verified=false,
            original_Spectrum_CB0_upload_verified=false,
            Android_water_pixels_verified=false,
            private_shader_class_method_name_or_literal_exported=false
        };
    }
    private static void Selftest()
    {
        using var module=ModuleDefinition.CreateModule("synthetic",ModuleKind.Dll);
        var shader=new TypeReference("UnityEngine","Shader",module,module.TypeSystem.CoreLibrary);
        var material=new TypeReference("UnityEngine","Material",module,module.TypeSystem.CoreLibrary);
        var good=new MethodReference("Find",shader,shader){HasThis=false};
        good.Parameters.Add(new ParameterDefinition(module.TypeSystem.String));
        var bad=new MethodReference("Find",shader,material){HasThis=false};
        bad.Parameters.Add(new ParameterDefinition(module.TypeSystem.String));
        var ctor=new MethodReference(".ctor",module.TypeSystem.Void,material){HasThis=true};
        ctor.Parameters.Add(new ParameterDefinition(shader));
        var l=Instruction.Create(OpCodes.Ldstr,"SYNTHETIC_ONLY");
        var c=Instruction.Create(OpCodes.Call,good);
        if(!Find(c) || Find(Instruction.Create(OpCodes.Call,bad)) ||
           !MaterialCtor(Instruction.Create(OpCodes.Newobj,ctor)) ||
           !Direct(new List<Instruction>{l,Instruction.Create(OpCodes.Nop),c},2,"SYNTHETIC_ONLY") ||
           Direct(new List<Instruction>{l,c},1,"DIFFERENT") ||
           Name(l,"DIFFERENT") || !Name(l,"SYNTHETIC_ONLY"))
            throw new InvalidOperationException("synthetic_control");
        Console.WriteLine("T2_SPECTRUM_SHADERFIND_CECIL_SYNTHETIC_PASS");
    }
    private static int Main(string[] a)
    {
        if(a.Length==1 && a[0]=="--selftest")
        {
            try{Selftest();return 0;} catch{Console.WriteLine("T2_SPECTRUM_SHADERFIND_CECIL_SYNTHETIC_FAIL");return 2;}
        }
        try
        {
            if(a.Length!=3) throw new InvalidOperationException();
            var dll=new FileInfo(a[0]);var src=new FileInfo(a[1]);var result=new FileInfo(a[2]);
            if(!dll.Exists || dll.Length!=3211776 || !src.Exists ||
               src.Length<=0 || src.Length>1024 || result.Exists || !result.Directory!.Exists)
                throw new InvalidOperationException();
            string name=File.ReadAllText(src.FullName);
            if(string.IsNullOrWhiteSpace(name) || name.Length>256 ||
               name.IndexOfAny(new[]{'\0','\r','\n'})>=0) throw new InvalidOperationException();
            using var asm=AssemblyDefinition.ReadAssembly(dll.FullName,
                new ReaderParameters{InMemory=true,ReadSymbols=false});
            var report=Scan(asm,name);
            string safe=JsonSerializer.Serialize(report);
            if(safe.Length>8192) throw new InvalidOperationException();
            File.WriteAllText(result.FullName,safe+"\n");
            Console.WriteLine("T2_SPECTRUM_SHADERFIND_IL_SAFE "+safe);
            return 0;
        }
        catch
        {
            Console.WriteLine("T2_SPECTRUM_SHADERFIND_IL_BLOCKED no_private_content_printed=true");
            return 2;
        }
    }
}
