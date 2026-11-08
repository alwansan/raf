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
                    if(DirectMaterialBlit(m,i,materialField))exactMaterialDirect[lit.Value]++;
                    else if(OriginalMaterialLocalAliasBlit(m,i,materialField))
                        exactMaterialLocalAlias[lit.Value]++;
                    var match=DirectFieldBlit(m,i,materialField);
                    if(match is not null){candidates[lit.Value].Add(match);linked++;}
                }
        }
        var pass0=candidates[0].Count==1?candidates[0][0]:null;
        var pass1=candidates[1].Count==1?candidates[1][0]:null;
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
