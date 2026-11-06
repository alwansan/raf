// Source-original Material stfld stack ownership, using public Cecil metadata
// only. The original game DLL is statically read; names, IL, tokens, exact
// numeric values and original assets must never appear in logs/artifacts.
// A compiled IL dataflow path is NOT proof of runtime execution or Foam shader.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class MaterialStoreValueTrace
{
    internal readonly record struct Evidence(string ValueOrigin, string ShaderInputOrigin,
                                              int BasicBlockInstructions,
                                              bool OriginalShaderIdentityVerified,
                                              bool RuntimeCB0UploadVerified);
    private readonly record struct Value(string Origin, string ShaderOrigin = "unproven");
    private const int MaxBlockInstructions = 128;
    private const int MaxStack = 96;
    private const string Unknown = "unproven";

    private static string TypeOrigin(string type, string origin)
    {
        if (type == "UnityEngine.Material") return "typed_Material_" + origin;
        if (type == "UnityEngine.Shader") return "typed_Shader_" + origin;
        return Unknown;
    }
    private static bool IsBoundary(Instruction i) =>
        i.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
            or FlowControl.Return or FlowControl.Throw or FlowControl.Break;

    private static int? IndexSuffix(Instruction i)
    {
        for (int n = 0; n < 4; n++)
            if (i.OpCode.Name.EndsWith("." + n.ToString(), StringComparison.Ordinal))
                return n;
        return null;
    }

    private static int? FormalIndex(Instruction i, MethodDefinition context)
    {
        if (i.Operand is ParameterDefinition parameter)
            return parameter.Index;
        int? index=IndexSuffix(i);
        if (index is null) return null;
        int formal=index.Value-(context.HasThis ? 1 : 0);
        return formal >= 0 ? formal : null;
    }

    private static string TypedMethodArgument(Instruction i, MethodDefinition context)
    {
        int? idx=FormalIndex(i,context);
        if (idx is null || idx < 0 || idx.Value >= context.Parameters.Count)
            return Unknown;
        return TypeOrigin(context.Parameters[idx.Value].ParameterType.FullName,
                          "parameter");
    }

    private static string TypedLocal(Instruction i, MethodDefinition context,
                                     IDictionary<int, Value> locals)
    {
        int? idx=i.Operand is VariableDefinition variable
            ? variable.Index : IndexSuffix(i);
        if (idx is null || idx < 0 || idx.Value >= context.Body.Variables.Count)
            return Unknown;
        // A known local value must have its reaching definition *in this same
        // block*. A local type alone does not prove actual newobj/value source.
        return locals.TryGetValue(idx.Value,out Value provenLocal) ? provenLocal.Origin : Unknown;
    }

    internal static Evidence Trace(IList<Instruction> instructions,
                                   int storePos, MethodDefinition? context)
    {
        Evidence Block(string reason) => new(reason,Unknown,0,false,false);
        if (storePos < 0 || storePos >= instructions.Count ||
            instructions[storePos].OpCode.Code != Code.Stfld ||
            instructions[storePos].Operand is not FieldReference target ||
            target.FieldType.FullName != "UnityEngine.Material" || context?.HasBody != true)
            return Block("invalid_Material_stfld");
        // A branch directly to this store may arrive with a stack from another
        // block. Do not claim any unique producer in that situation.
        var targetInstruction=instructions[storePos];
        if (instructions.Any(i => ReferenceEquals(i.Operand,targetInstruction) ||
            i.Operand is Instruction[] switchTargets &&
            switchTargets.Any(t=>ReferenceEquals(t,targetInstruction))) ||
            context.Body.ExceptionHandlers.Any(e =>
                ReferenceEquals(e.TryStart,targetInstruction) ||
                ReferenceEquals(e.HandlerStart,targetInstruction) ||
                ReferenceEquals(e.FilterStart,targetInstruction)))
            return Block("alternate_entry_at_store");

        var targets = new HashSet<Instruction>();
        foreach (var i in instructions)
        {
            if (i.Operand is Instruction branch) targets.Add(branch);
            if (i.Operand is Instruction[] switches)
                foreach (var switchTarget in switches) targets.Add(switchTarget);
        }
        foreach (var handler in context.Body.ExceptionHandlers)
        {
            if (handler.TryStart is not null) targets.Add(handler.TryStart);
            if (handler.HandlerStart is not null) targets.Add(handler.HandlerStart);
            if (handler.FilterStart is not null) targets.Add(handler.FilterStart);
        }
        int start=Math.Max(0,storePos-MaxBlockInstructions);
        for (int i=start;i<storePos;i++)
        {
            // Do not cross control transfers, branch/switch leader labels or
            // exception entry boundaries. This is *one* basic block only.
            if (IsBoundary(instructions[i])) start=i+1;
            else if (i>start && targets.Contains(instructions[i])) start=i;
        }
        if (storePos-start > MaxBlockInstructions)
            return Block("unbounded_basic_block");
        // If scanning starts from an arbitrary middle of an oversized block,
        // attribution to an earlier producer could be false. Block completely.
        if (start>0 && start==storePos-MaxBlockInstructions &&
            !targets.Contains(instructions[start]) &&
            !IsBoundary(instructions[start-1]))
            return Block("window_truncated");

        var stack = new List<Value>();
        var locals = new Dictionary<int, Value>();
        Value Pop()
        {
            if (stack.Count==0) return new Value(Unknown);
            var last=stack[^1];
            stack.RemoveAt(stack.Count-1);
            return last;
        }
        bool Push(Value v)
        {
            if (stack.Count>=MaxStack) return false;
            stack.Add(v);
            return true;
        }
        int steps=0;
        for (int i=start;i<storePos;i++)
        {
            steps++;
            var ins=instructions[i];
            string opcode=ins.OpCode.Name;
            if (IsBoundary(ins)) return Block("flow_boundary_inside_block");
            if (opcode == "nop") continue;
            if (opcode=="dup")
            {
                if (!Push(stack.Count==0?new Value(Unknown):stack[^1]))
                    return Block("unbounded_stack");
                continue;
            }
            if (opcode=="pop"){Pop();continue;}
            if (opcode.StartsWith("ldarg",StringComparison.Ordinal) &&
                !opcode.StartsWith("ldarga",StringComparison.Ordinal))
            {
                if (!Push(new Value(TypedMethodArgument(ins,context))))
                    return Block("unbounded_stack");
                continue;
            }
            if (opcode.StartsWith("ldloca",StringComparison.Ordinal))
                return Block("local_address_alias_not_proven");
            if (opcode.StartsWith("ldloc",StringComparison.Ordinal))
            {
                if (!Push(new Value(TypedLocal(ins,context,locals))))
                    return Block("unbounded_stack");
                continue;
            }
            if (opcode.StartsWith("stloc",StringComparison.Ordinal))
            {
                int? ix=ins.Operand is VariableDefinition v ? v.Index : IndexSuffix(ins);
                if (ix is null || ix<0 || ix.Value>=context.Body.Variables.Count)
                    return Block("invalid_local_definition");
                locals[ix.Value]=Pop();
                continue;
            }
            if (opcode is "ldfld" or "ldflda")
            {
                Pop(); // instance
                if (ins.Operand is not FieldReference field ||
                    !Push(new Value(opcode=="ldfld"
                        ? TypeOrigin(field.FieldType.FullName,"instance_field")
                        : Unknown)))
                    return Block("malformed_or_unbounded_field_read");
                continue;
            }
            if (opcode is "ldsfld" or "ldsflda")
            {
                if (ins.Operand is not FieldReference field ||
                    !Push(new Value(opcode=="ldsfld"
                        ? TypeOrigin(field.FieldType.FullName,"static_field")
                        : Unknown)))
                    return Block("malformed_or_unbounded_static_field_read");
                continue;
            }
            if (opcode=="stfld"){Pop();Pop();continue;}
            if (opcode=="stsfld"){Pop();continue;}
            if (opcode=="ldnull")
            {
                if(!Push(new Value("null_literal")))return Block("unbounded_stack");
                continue;
            }
            if (opcode.StartsWith("ldc.",StringComparison.Ordinal) ||
                opcode is "ldstr" or "ldtoken")
            {
                if(!Push(new Value(opcode=="ldstr"?"string_literal":Unknown)))
                    return Block("unbounded_stack");
                continue;
            }
            if (ins.OpCode.Code is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if (ins.Operand is not MethodReference method ||
                    method.Parameters.Count>32) return Block("invalid_method_reference");
                var args=new Value[method.Parameters.Count];
                for(int p=args.Length-1;p>=0;p--) args[p]=Pop();
                if (ins.OpCode.Code!=Code.Newobj && method.HasThis) Pop();
                Value result=new(Unknown);
                if (ins.OpCode.Code==Code.Newobj &&
                    method.DeclaringType.FullName=="UnityEngine.Material" &&
                    method.Name==".ctor" && method.HasThis)
                {
                    string origin=method.Parameters.Count==1 &&
                        method.Parameters[0].ParameterType.FullName=="UnityEngine.Shader"
                        ? "exact_Material_ctor_with_Shader_formal"
                        : "exact_Material_ctor_other_formals";
                    result=new Value(origin,args.Length>0?args[0].Origin:Unknown);
                }
                else if (method.DeclaringType.FullName=="UnityEngine.Shader" &&
                    method.Name=="Find" && method.ReturnType.FullName=="UnityEngine.Shader" &&
                    method.Parameters.Count==1 &&
                    method.Parameters[0].ParameterType.FullName=="System.String" &&
                    ins.OpCode.Code!=Code.Newobj)
                    result=new Value("typed_Shader_Find_result");
                else if (ins.OpCode.Code!=Code.Newobj &&
                    method.ReturnType.FullName=="UnityEngine.Material")
                    result=new Value(method.DeclaringType.FullName=="UnityEngine.Renderer" &&
                        method.Name is "get_material" or "get_sharedMaterial"
                            ? "typed_Renderer_Material_getter" : "typed_Material_call_result");
                else if (ins.OpCode.Code!=Code.Newobj &&
                    method.ReturnType.FullName=="UnityEngine.Shader")
                    result=new Value("typed_Shader_other_call_result");
                if (ins.OpCode.Code==Code.Newobj ||
                    method.ReturnType.FullName!="System.Void")
                    if (!Push(result))return Block("unbounded_stack");
                continue;
            }
            if (opcode is "castclass" or "box" or "unbox.any" or "newarr" or
                "ldlen" or "ldelem.ref")
            {
                if (opcode=="ldelem.ref") Pop();
                Pop();
                if(!Push(new Value(Unknown)))return Block("unbounded_stack");
                continue;
            }
            // Any arithmetic, byref mutation, exception, branch, stack access,
            // tailcall/prefix or other operation not modelled blocks proof.
            return Block("unsupported_opcode");
        }
        Value source=Pop();
        // The instance receiver is popped separately and not identified. We
        // make no claim that the object owning this field is Foam.
        Pop();
        return new Evidence(source.Origin,source.ShaderOrigin,steps,false,false);
    }

    internal static void SelfTest()
    {
        using var module=ModuleDefinition.CreateModule("public-material-flow",ModuleKind.Dll);
        var owner=new TypeDefinition("PublicFixture","Owner",
            Mono.Cecil.TypeAttributes.Public|Mono.Cecil.TypeAttributes.Class,
            module.TypeSystem.Object);
        module.Types.Add(owner);
        var material=new TypeReference("UnityEngine","Material",module,module);
        var shader=new TypeReference("UnityEngine","Shader",module,module);
        var field=new FieldReference("publicMaterial",material,owner);
        var ctx=new MethodDefinition("PublicWriter",
            Mono.Cecil.MethodAttributes.Public,module.TypeSystem.Void);
        owner.Methods.Add(ctx);
        ctx.Parameters.Add(new ParameterDefinition(shader));
        ctx.Body=new Mono.Cecil.Cil.MethodBody(ctx);
        ctx.Body.Variables.Add(new VariableDefinition(material));
        var ctor=new MethodReference(".ctor",module.TypeSystem.Void,material)
            {HasThis=true};
        ctor.Parameters.Add(new ParameterDefinition(shader));
        var store=Instruction.Create(OpCodes.Stfld,field);
        var direct=new List<Instruction> {
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldarg_1),
            Instruction.Create(OpCodes.Newobj,ctor),
            store
        };
        var evidence=Trace(direct,3,ctx);
        if (evidence.ValueOrigin!="exact_Material_ctor_with_Shader_formal" ||
            evidence.ShaderInputOrigin!="typed_Shader_parameter")
            throw new InvalidOperationException("Exact new Material(typed Shader) stfld proof");
        var local=new List<Instruction> {
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldarg_1),
            Instruction.Create(OpCodes.Newobj,ctor),
            Instruction.Create(OpCodes.Stloc_0),
            Instruction.Create(OpCodes.Ldloc_0),
            store
        };
        if (Trace(local,5,ctx).ValueOrigin!="exact_Material_ctor_with_Shader_formal")
            throw new InvalidOperationException("Exactly reaching material local must survive");
        var dup=new List<Instruction> {
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldarg_1),
            Instruction.Create(OpCodes.Newobj,ctor),
            Instruction.Create(OpCodes.Dup),
            Instruction.Create(OpCodes.Pop),
            store
        };
        if (Trace(dup,5,ctx).ValueOrigin!="exact_Material_ctor_with_Shader_formal")
            throw new InvalidOperationException("Material ctor alias through dup and pop");
        ctx.Parameters.Add(new ParameterDefinition(material));
        var distractor=new List<Instruction> {
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldarg_1),
            Instruction.Create(OpCodes.Newobj,ctor),
            Instruction.Create(OpCodes.Pop),
            Instruction.Create(OpCodes.Ldarg_2),
            store
        };
        if (Trace(distractor,5,ctx).ValueOrigin!="typed_Material_parameter")
            throw new InvalidOperationException("Nearby Material ctor cannot stand for stfld value");
        var wrong=new List<Instruction>(direct);
        wrong[2]=Instruction.Create(OpCodes.Ldnull);
        if (Trace(wrong,3,ctx).ValueOrigin!="null_literal")
            throw new InvalidOperationException("Null source must not alias Material ctor");
        var branch=new List<Instruction>(direct);
        branch.Insert(0,Instruction.Create(OpCodes.Br_S,store));
        if (Trace(branch,4,ctx).ValueOrigin!="alternate_entry_at_store")
            throw new InvalidOperationException("Branch into stfld invalidates proof");
        var unsupported=new List<Instruction>(direct);
        unsupported.Insert(2,Instruction.Create(OpCodes.Add));
        if (Trace(unsupported,4,ctx).ValueOrigin!="unsupported_opcode")
            throw new InvalidOperationException("Unsupported IL cannot produce attribution");
        var wrongField=new FieldReference("wrong",module.TypeSystem.Object,owner);
        var wrongTarget=new List<Instruction>(direct);
        wrongTarget[3]=Instruction.Create(OpCodes.Stfld,wrongField);
        if (Trace(wrongTarget,3,ctx).ValueOrigin!="invalid_Material_stfld")
            throw new InvalidOperationException("Wrong field type must block");
    }
}
