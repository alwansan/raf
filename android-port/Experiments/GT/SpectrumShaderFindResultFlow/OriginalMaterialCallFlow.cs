// GT: conservative, source-authentic IL stack lineage of a Material field load.
// No original method/type/field names or IL bytes are emitted. Only same-block,
// typed argument use is a proof candidate; never claim device pixels from CIL.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class OriginalMaterialCallFlow
{
    internal sealed class Receipt
    {
        public int GraphicsMaterialArguments { get; set; }
        public int GraphicsBlitMaterialArguments { get; set; }
        public int GraphicsOtherMaterialArguments { get; set; }
        public int RenderTextureMaterialArguments { get; set; }
        public int OtherMethodMaterialArguments { get; set; }
        public int MaterialReceiverCalls { get; set; }
        public int MaterialFieldStores { get; set; }
        public int MaterialLocalStores { get; set; }
        public bool ReachedBranchBoundary { get; set; }
        public bool UnsupportedInstruction { get; set; }
        public int InstructionsObserved { get; set; }
    }

    private static bool IsLoadLocal(Instruction ins, out int index)
    {
        index = ins.OpCode.Code switch
        {
            Code.Ldloc_0 => 0, Code.Ldloc_1 => 1,
            Code.Ldloc_2 => 2, Code.Ldloc_3 => 3,
            Code.Ldloc or Code.Ldloc_S when ins.Operand is VariableDefinition v => v.Index,
            _ => -1
        };
        return index >= 0;
    }

    private static bool IsStoreLocal(Instruction ins, out int index)
    {
        index = ins.OpCode.Code switch
        {
            Code.Stloc_0 => 0, Code.Stloc_1 => 1,
            Code.Stloc_2 => 2, Code.Stloc_3 => 3,
            Code.Stloc or Code.Stloc_S when ins.Operand is VariableDefinition v => v.Index,
            _ => -1
        };
        return index >= 0;
    }

    private static bool CountBehaviour(string name, string empty, out int count)
    {
        count = 0;
        if(name == empty) return true;
        if(name is "Varpop" or "Varpush" or "PopAll") return false;
        count = name.Split('_', StringSplitOptions.RemoveEmptyEntries).Length;
        return count is >= 1 and <= 3;
    }

    // A field load preserves the lower part of the CIL stack, which may hold
    // already-pushed Graphics arguments. Unknown lower slots are represented
    // as false, so only the exact newly loaded Material can prove an argument.
    private static bool[] Take(List<bool> stack, int count)
    {
        if(count < 0 || count > 64) throw new InvalidOperationException("invalid_CIL_stack_pop_budget");
        if(stack.Count < count)
            stack.InsertRange(0, Enumerable.Repeat(false, count - stack.Count));
        var result = stack.GetRange(stack.Count - count, count).ToArray();
        stack.RemoveRange(stack.Count - count, count);
        return result;
    }

    private static void InspectCall(MethodReference call, bool[] arguments, Receipt receipt)
    {
        int prefix = call.HasThis ? 1 : 0;
        if(arguments.Length != call.Parameters.Count + prefix)
            throw new InvalidOperationException("typed_call_signature_stack_mismatch");
        if(prefix == 1 && arguments[0] &&
           call.DeclaringType.FullName == "UnityEngine.Material")
            receipt.MaterialReceiverCalls++;
        for(int i = 0; i < call.Parameters.Count; i++)
        {
            if(!arguments[prefix+i] ||
               call.Parameters[i].ParameterType.FullName != "UnityEngine.Material")
                continue;
            if(call.DeclaringType.FullName == "UnityEngine.Graphics")
            {
                receipt.GraphicsMaterialArguments++;
                if(call.Name == "Blit") receipt.GraphicsBlitMaterialArguments++;
                else receipt.GraphicsOtherMaterialArguments++;
            }
            else if(call.DeclaringType.FullName == "UnityEngine.RenderTexture")
                receipt.RenderTextureMaterialArguments++;
            else
                receipt.OtherMethodMaterialArguments++;
        }
    }

    internal static Receipt Trace(MethodDefinition method, int sourceFieldLoadIndex)
    {
        if(!method.HasBody || sourceFieldLoadIndex < 0 ||
           sourceFieldLoadIndex >= method.Body.Instructions.Count)
            throw new ArgumentOutOfRangeException(nameof(sourceFieldLoadIndex));
        var source = method.Body.Instructions[sourceFieldLoadIndex];
        if(source.OpCode.Code is not (Code.Ldfld or Code.Ldsfld) ||
           source.Operand is not FieldReference f ||
           f.FieldType.FullName != "UnityEngine.Material")
            throw new InvalidOperationException("source_Material_field_load_not_typed");

        var receipt = new Receipt();
        var stack = new List<bool> {true};
        var locals = new Dictionary<int, bool>();
        var il = method.Body.Instructions;
        for(int i = sourceFieldLoadIndex + 1; i < il.Count && receipt.InstructionsObserved < 256; i++)
        {
            var ins = il[i];
            receipt.InstructionsObserved++;
            if(ins.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw ||
                ins.OpCode.Code is Code.Leave or Code.Leave_S or Code.Endfinally)
            {
                receipt.ReachedBranchBoundary = true;
                break;
            }
            if(ins.OpCode.Code == Code.Nop) continue;
            if(ins.OpCode.Code == Code.Dup)
            {
                var top = Take(stack,1)[0];
                stack.Add(top);
                stack.Add(top);
            }
            else if(ins.OpCode.Code == Code.Pop)
                Take(stack,1);
            else if(IsLoadLocal(ins,out var loadIndex))
                stack.Add(locals.GetValueOrDefault(loadIndex,false));
            else if(IsStoreLocal(ins,out var storeIndex))
            {
                var value = Take(stack,1)[0];
                locals[storeIndex]=value;
                if(value)receipt.MaterialLocalStores++;
            }
            else if(ins.OpCode.Code is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if(ins.Operand is not MethodReference call)
                {
                    receipt.UnsupportedInstruction = true;
                    break;
                }
                var args = Take(stack,call.Parameters.Count +
                    ((call.HasThis && ins.OpCode.Code != Code.Newobj) ? 1 : 0));
                if(ins.OpCode.Code != Code.Newobj)
                    InspectCall(call,args,receipt);
                if(ins.OpCode.Code == Code.Newobj ||
                   call.ReturnType.FullName != "System.Void")
                    stack.Add(false);
            }
            else if(ins.OpCode.Code is Code.Stfld or Code.Stsfld)
            {
                var args = Take(stack,ins.OpCode.Code == Code.Stfld ? 2 : 1);
                if(args[^1] && ins.Operand is FieldReference field &&
                   field.FieldType.FullName=="UnityEngine.Material")
                    receipt.MaterialFieldStores++;
            }
            else
            {
                var popName = ins.OpCode.StackBehaviourPop.ToString();
                var pushName = ins.OpCode.StackBehaviourPush.ToString();
                if(!CountBehaviour(popName,"Pop0",out int pops) ||
                   !CountBehaviour(pushName,"Push0",out int pushes))
                {
                    receipt.UnsupportedInstruction = true;
                    break;
                }
                // Other instructions produce unknown values. In particular
                // no arithmetic, cast, field fetch or helper return propagates
                // the source Material without a type-preserving proof.
                Take(stack,pops);
                for(int n=0;n<pushes;n++) stack.Add(false);
            }
            if(!stack.Any(x=>x) && !locals.Values.Any(x=>x))
                break;
        }
        return receipt;
    }

    internal static void SelfTest()
    {
        using var module = ModuleDefinition.CreateModule("gt-synthetic-CIL-only",ModuleKind.Dll);
        var material = new TypeReference("UnityEngine","Material",module,module.TypeSystem.CoreLibrary);
        var graphics = new TypeReference("UnityEngine","Graphics",module,module.TypeSystem.CoreLibrary);
        var renderTexture = new TypeReference("UnityEngine","RenderTexture",module,module.TypeSystem.CoreLibrary);
        var texture = new TypeReference("UnityEngine","Texture",module,module.TypeSystem.CoreLibrary);
        var owner = new TypeDefinition("Synthetic","Holder",
            Mono.Cecil.TypeAttributes.Class|Mono.Cecil.TypeAttributes.Public,module.TypeSystem.Object);
        module.Types.Add(owner);
        var f = new FieldDefinition("SyntheticOnly",
            Mono.Cecil.FieldAttributes.Public,material);
        owner.Fields.Add(f);
        var blit = new MethodReference("Blit",module.TypeSystem.Void,graphics){HasThis=false};
        blit.Parameters.Add(new ParameterDefinition(texture));
        blit.Parameters.Add(new ParameterDefinition(renderTexture));
        blit.Parameters.Add(new ParameterDefinition(material));

        MethodDefinition Demo(params Instruction[] code)
        {
            var method = new MethodDefinition("Synthetic",
                Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
                module.TypeSystem.Void);
            method.Body.Variables.Add(new VariableDefinition(material));
            foreach(var op in code)method.Body.Instructions.Add(op);
            return method;
        }
        Instruction Ldfld() => Instruction.Create(OpCodes.Ldfld,f);
        var success=Demo(Instruction.Create(OpCodes.Ldnull),
            Instruction.Create(OpCodes.Ldnull),Instruction.Create(OpCodes.Ldnull),
            Ldfld(),Instruction.Create(OpCodes.Call,blit),Instruction.Create(OpCodes.Ret));
        var good=Trace(success,3);
        if(good.GraphicsMaterialArguments!=1 ||
           good.GraphicsBlitMaterialArguments!=1 || good.UnsupportedInstruction)
            throw new InvalidOperationException("synthetic_positive_graphics_material_stack_failed");

        var dropped=Demo(Instruction.Create(OpCodes.Ldnull),Ldfld(),
            Instruction.Create(OpCodes.Pop),Instruction.Create(OpCodes.Ldnull),
            Instruction.Create(OpCodes.Call,blit),Instruction.Create(OpCodes.Ret));
        if(Trace(dropped,1).GraphicsMaterialArguments!=0)
            throw new InvalidOperationException("synthetic_dropped_material_false_positive");

        var alias=Demo(Instruction.Create(OpCodes.Ldnull),Ldfld(),
            Instruction.Create(OpCodes.Stloc_0),Instruction.Create(OpCodes.Ldloc_0),
            Instruction.Create(OpCodes.Call,blit),Instruction.Create(OpCodes.Ret));
        if(Trace(alias,1).GraphicsMaterialArguments!=1 ||
           Trace(alias,1).MaterialLocalStores!=1)
            throw new InvalidOperationException("synthetic_local_alias_flow_failed");

        var tail=Instruction.Create(OpCodes.Call,blit);
        var branched=Demo(Instruction.Create(OpCodes.Ldnull),Ldfld(),
            Instruction.Create(OpCodes.Br_S,tail),tail,Instruction.Create(OpCodes.Ret));
        if(Trace(branched,1).GraphicsMaterialArguments!=0 ||
           !Trace(branched,1).ReachedBranchBoundary)
            throw new InvalidOperationException("synthetic_branch_non_proof_failed");

        var unrelated=new MethodReference("NotGraphics",module.TypeSystem.Void,owner)
            {HasThis=false};
        unrelated.Parameters.Add(new ParameterDefinition(material));
        var other=Demo(Instruction.Create(OpCodes.Ldnull),Ldfld(),
            Instruction.Create(OpCodes.Call,unrelated),Instruction.Create(OpCodes.Ret));
        if(Trace(other,1).GraphicsMaterialArguments!=0 ||
           Trace(other,1).OtherMethodMaterialArguments!=1)
            throw new InvalidOperationException("synthetic_non_graphics_no_false_claim_failed");
        Console.WriteLine("GT_SPECTRUM_MATERIAL_FLOW_SYNTHETIC_PASS");
    }
}
