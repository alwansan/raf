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
    private sealed record MaterialConsumer(string Kind, FieldDefinition? Field, VariableDefinition? Local, int Nops);
    private static readonly string[] MaterialKinds = {
        "instance_material_field", "static_material_field", "material_local",
        "material_return", "direct_renderer_material_setter",
        "direct_renderer_shared_material_setter", "discarded_pop",
        "duplicated_unresolved", "unproved"
    };
    private const string MaterialType = "UnityEngine.Material";

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
    private static int ImmediateAfterNops(IList<Instruction> il, int previous)
    {
        int next = previous + 1, skips = 0;
        while(next < il.Count && il[next].OpCode.Code == Code.Nop && skips < 4)
        { next++; skips++; }
        return next;
    }
    private static bool DirectOriginalFieldToMaterialCtor(IList<Instruction> il, int fieldLoadIndex)
    {
        // Material(Shader) has exactly one Shader arg; an adjacent ldfld is
        // therefore the actual stack value of that argument, not cooccurrence.
        int index = fieldLoadIndex + 1, skipped = 0;
        while (index < il.Count && il[index].OpCode.Code == Code.Nop && skipped++ < 4)
            index++;
        return index < il.Count && IsCtorMaterialShader(il[index]);
    }
    private static int RendererMaterialSetter(Instruction inst)
    {
        if(inst.OpCode.Code is not (Code.Call or Code.Callvirt)
            || inst.Operand is not MethodReference m
            || !m.HasThis || m.DeclaringType.FullName != "UnityEngine.Renderer"
            || m.ReturnType.FullName != "System.Void"
            || m.Parameters.Count != 1
            || m.Parameters[0].ParameterType.FullName != MaterialType)
            return 0;
        if(m.Name == "set_material") return 1;
        if(m.Name == "set_sharedMaterial") return 2;
        return 0;
    }
    private static int DirectRendererSetter(IList<Instruction> il, int materialValueIndex)
    {
        int next=ImmediateAfterNops(il,materialValueIndex);
        return next < il.Count ? RendererMaterialSetter(il[next]) : 0;
    }
    private static bool ResolveMaterialField(Instruction inst, ModuleDefinition module,
        out FieldDefinition? field)
    {
        field=null;
        if(inst.Operand is not FieldReference fr ||
            fr.FieldType.FullName != MaterialType) return false;
        try {
            var f=fr.Resolve();
            if(f is not null && f.Module==module && f.FieldType.FullName==MaterialType)
            {
                field=f;
                return true;
            }
        } catch(AssemblyResolutionException) {} catch(ResolutionException) {}
        return false;
    }
    private static bool SameMaterialFieldLoad(Instruction inst, FieldDefinition field)
    {
        if(inst.OpCode.Code is not (Code.Ldfld or Code.Ldsfld)
            || inst.Operand is not FieldReference fr
            || fr.FieldType.FullName != MaterialType) return false;
        try {
            var f=fr.Resolve();
            return f is not null && f.Module==field.Module &&
                   f.MetadataToken==field.MetadataToken;
        } catch(AssemblyResolutionException) {return false;}
          catch(ResolutionException) {return false;}
    }

    private sealed record FieldApiTrace(
        int Inspected, int Boundary, int MaterialReceiver,
        int TypedMaterialArgument, int GraphicsArgument,
        int CommandBufferArgument, int RendererArgument, int OtherArgument,
        int GraphicsBlit, int GraphicsDrawMesh, int GraphicsOther, int GraphicsMixed,
        int BlitImplicitPass, int BlitExplicitPass, int BlitOtherSignature, int BlitMixedSignatures,
        int BlitPassLiteral0, int BlitPassLiteral1, int BlitPassOtherLiteral,
        int BlitPassUnknown, int BlitPassMixed,
        int BlitSourceTexture, int BlitSourceRenderTexture, int BlitSourceUnknown,
        int BlitDestinationRenderTexture, int BlitDestinationNull, int BlitDestinationUnknown,
        BlitPass0SourceTexture, BlitPass0SourceRenderTexture, BlitPass0SourceUnknown, BlitPass0DestinationRenderTexture, BlitPass0DestinationNull, BlitPass0DestinationUnknown,
        BlitPass1SourceTexture, BlitPass1SourceRenderTexture, BlitPass1SourceUnknown, BlitPass1DestinationRenderTexture, BlitPass1DestinationNull, BlitPass1DestinationUnknown);

    private static int PublicBlitSignatureKind(MethodReference method)
    {
        // Only public Unity parameter TYPES, not original argument values.
        // 1 = three-argument implicit pass; 2 = four-argument explicit int pass;
        // 3 = other/unsupported. 0 = not the public static Blit API.
        if(method.DeclaringType.FullName!="UnityEngine.Graphics" ||
           method.HasThis || method.Name!="Blit")return 0;
        var p=method.Parameters;
        if(p.Count is 3 or 4 &&
           p[0].ParameterType.FullName=="UnityEngine.Texture" &&
           p[1].ParameterType.FullName=="UnityEngine.RenderTexture" &&
           p[2].ParameterType.FullName==MaterialType)
        {
            if(p.Count==3)return 1;
            if(p[3].ParameterType.FullName=="System.Int32")return 2;
        }
        return 3;
    }

    private static int DirectPublicBlitPassLiteralKind(IList<Instruction> il, int call)
    {
        // The public (Texture, RenderTexture, Material, int pass) overload has
        // its int pass at the TOP of the IL stack. A direct ldc.i4 producer
        // immediately before Call proves that argument's literal. Anything
        // transformed, computed, indirect or >4 NOP away remains unknown.
        int index=call-1,nops=0;
        while(index>=0 && il[index].OpCode.Code==Code.Nop && nops++<4)index--;
        if(index<0)return 4;
        var inst=il[index];
        int? value=inst.OpCode.Code switch
        {
            Code.Ldc_I4_M1 => -1, Code.Ldc_I4_0 => 0,
            Code.Ldc_I4_1 => 1, Code.Ldc_I4_2 => 2,
            Code.Ldc_I4_3 => 3, Code.Ldc_I4_4 => 4,
            Code.Ldc_I4_5 => 5, Code.Ldc_I4_6 => 6,
            Code.Ldc_I4_7 => 7, Code.Ldc_I4_8 => 8,
            Code.Ldc_I4_S when inst.Operand is sbyte signed => signed,
            Code.Ldc_I4 when inst.Operand is int wide => wide,
            _ => null
        };
        if(!value.HasValue)return 4;
        return value.Value==0 ? 1 : value.Value==1 ? 2 : 3;
    }

    private sealed record DirectBlitInputs(int Source, int Destination);

    private static int PreviousNonNop(IList<Instruction> il, int index)
    {
        int skipped=0;
        while(index>=0 && il[index].OpCode.Code==Code.Nop && skipped<4)
        {index--;skipped++;}
        if(index<0 || il[index].OpCode.Code==Code.Nop)return -1;
        return index;
    }

    private static bool SimpleFieldReceiver(Instruction inst)
    {
        return inst.OpCode.Code is
            Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3 or
            Code.Ldarg or Code.Ldarg_S or Code.Ldloc or Code.Ldloc_S or
            Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3 or
            Code.Ldsfld;
    }

    private static bool TryDirectTypedValue(MethodDefinition method,
        IList<Instruction> il, ref int index, out string type)
    {
        type="";
        index=PreviousNonNop(il,index);
        if(index<0)return false;
        var inst=il[index];
        if(inst.OpCode.Code==Code.Ldnull)
        {type="<null>";index--;return true;}
        if(inst.OpCode.Code is Code.Ldloc or Code.Ldloc_S or
           Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3)
        {
            var local=method.Body.Variables.FirstOrDefault(v=>LocalIsLoadOf(inst,v));
            if(local is null)return false;
            type=local.VariableType.FullName;
            index--;
            return true;
        }
        if((inst.OpCode.Code is Code.Ldfld or Code.Ldsfld) &&
           inst.Operand is FieldReference field)
        {
            type=field.FieldType.FullName;
            index--;
            if(inst.OpCode.Code==Code.Ldfld)
            {
                index=PreviousNonNop(il,index);
                if(index<0 || !SimpleFieldReceiver(il[index]))return false;
                index--;
            }
            return true;
        }
        return false;
    }

    private static DirectBlitInputs TraceDirectBlitInputs(MethodDefinition method,
        int materialFieldIndex, int callIndex)
    {
        // Canonical straight-line stack only: source, destination, original
        // Material field, int pass, Graphics.Blit. No private names exported.
        // A call/cast/branch/unknown nested expression fails closed.
        var unknown=new DirectBlitInputs(0,0);
        var il=method.Body.Instructions;
        if(materialFieldIndex<0 || callIndex>=il.Count ||
           materialFieldIndex>=callIndex ||
           il[materialFieldIndex].OpCode.Code is not (Code.Ldfld or Code.Ldsfld))
            return unknown;
        int passIndex=PreviousNonNop(il,callIndex-1);
        if(passIndex<=materialFieldIndex ||
           DirectPublicBlitPassLiteralKind(il,callIndex)==4)return unknown;
        for(int k=materialFieldIndex+1;k<callIndex;k++)
            if(k!=passIndex && il[k].OpCode.Code!=Code.Nop)return unknown;
        int cursor=PreviousNonNop(il,materialFieldIndex-1);
        if(cursor<0)return unknown;
        if(il[materialFieldIndex].OpCode.Code==Code.Ldfld)
        {
            if(!SimpleFieldReceiver(il[cursor]))return unknown;
            cursor--;
        }
        if(!TryDirectTypedValue(method,il,ref cursor,out var destination))
            return unknown;
        if(!TryDirectTypedValue(method,il,ref cursor,out var source))
            return unknown;
        return new(
            source=="UnityEngine.Texture" ? 1 :
              source=="UnityEngine.RenderTexture" ? 2 : 0,
            destination=="UnityEngine.RenderTexture" ? 1 :
              destination=="<null>" ? 2 : 0);
    }

    private static FieldApiTrace TraceExactMaterialFieldRead(MethodDefinition method, int sourceIndex)
    {
        // Forward-only, max 32 original IL instructions per exact FieldDefinition load.
        // The field value, NOT the mere presence of a call, must reach the typed
        // Material parameter or exact UnityEngine.Material/Object instance receiver.
        // Unknown returns, indirect references, CFG branches and stack effects
        // do not inherit the source identity.
        var il=method.Body.Instructions;
        var stack=new List<bool>{true};
        var locals=new Dictionary<int,bool>();
        int inspected=0,boundary=0,receiver=0,arg=0,graphics=0,command=0,renderer=0,other=0;
        int graphicsBlit=0,graphicsDrawMesh=0,graphicsOther=0;
        int blitImplicit=0,blitExplicit=0,blitOther=0;
        int passLiteral0=0,passLiteral1=0,passOtherLiteral=0,passUnknown=0;
        int sourceKind=0,destinationKind=0;
        bool Pop()
        {
            if(stack.Count==0)return false;
            bool a=stack[^1]; stack.RemoveAt(stack.Count-1); return a;
        }
        for(int i=sourceIndex+1;i<il.Count && inspected<32;i++)
        {
            var op=il[i];
            if(op.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw) {boundary=1;break;}
            inspected++;
            if(op.OpCode.Code==Code.Nop)continue;
            if(op.OpCode.Code==Code.Dup)
            {
                if(stack.Count==0){boundary=1;break;}
                bool a=Pop();stack.Add(a);stack.Add(a);
            }
            else if(op.OpCode.Code is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if(op.Operand is not MethodReference callee){boundary=1;break;}
                int param=callee.Parameters.Count;
                bool constructing=op.OpCode.Code==Code.Newobj;
                int n=param+(!constructing && callee.HasThis?1:0);
                if(n>24){boundary=1;break;}
                var consumed=new bool[n];
                for(int j=0;j<n;j++)consumed[j]=Pop();
                bool recv=!constructing && callee.HasThis && consumed[param];
                if(recv && callee.DeclaringType.FullName is
                    ("UnityEngine.Material" or "UnityEngine.Object"))receiver++;
                bool materialArg=false;
                for(int j=0;j<param;j++)
                    if(callee.Parameters[j].ParameterType.FullName==MaterialType &&
                       consumed[param-1-j])materialArg=true;
                if(materialArg)
                {
                    arg++;
                    switch(callee.DeclaringType.FullName)
                    {
                        case "UnityEngine.Graphics":
                            graphics++;
                            // Only public Unity method families enter the safe report.
                            if(!callee.HasThis && callee.Name=="Blit")
                            {
                                graphicsBlit++;
                                switch(PublicBlitSignatureKind(callee))
                                {
                                    case 1: blitImplicit++;break;
                                    case 2:
                                        blitExplicit++;
                                        if(blitExplicit==1)
                                        {
                                            var direct=TraceDirectBlitInputs(method,sourceIndex,i);
                                            sourceKind=direct.Source;
                                            destinationKind=direct.Destination;
                                        }
                                        else {sourceKind=0;destinationKind=0;}
                                        switch(DirectPublicBlitPassLiteralKind(il,i))
                                        {
                                            case 1: passLiteral0++;break;
                                            case 2: passLiteral1++;break;
                                            case 3: passOtherLiteral++;break;
                                            default: passUnknown++;break;
                                        }
                                        break;
                                    default: blitOther++;break;
                                }
                            }
                            else if(!callee.HasThis && callee.Name=="DrawMesh")graphicsDrawMesh++;
                            else graphicsOther++;
                            break;
                        case "UnityEngine.Rendering.CommandBuffer": command++;break;
                        case "UnityEngine.Renderer": renderer++;break;
                        default: other++;break;
                    }
                }
                if(constructing || callee.ReturnType.FullName!="System.Void")stack.Add(false);
            }
            else
            {
                var storeLocal=LocalForStore(method,op);
                if(storeLocal is not null)
                    locals[storeLocal.Index]=Pop() &&
                        storeLocal.VariableType.FullName==MaterialType;
                else
                {
                    VariableDefinition? load=null;
                    if(op.OpCode.Code is Code.Ldloc or Code.Ldloc_S or
                        Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3)
                        load=method.Body.Variables.FirstOrDefault(v=>LocalIsLoadOf(op,v));
                    if(load is not null)
                        stack.Add(locals.GetValueOrDefault(load.Index,false));
                    else
                    {
                        int pop=FixedPopCount(op),push=FixedPushCount(op);
                        if(pop<0 || push<0 || pop>6 || push>2){boundary=1;break;}
                        for(int j=0;j<pop;j++)Pop();
                        for(int j=0;j<push;j++)stack.Add(false);
                    }
                }
            }
            if(!stack.Any(v=>v) && !locals.Values.Any(v=>v))break;
        }
        if(inspected>=32)boundary=1;
        // Per field-read site these public API categories are exclusive.
        int families=(graphicsBlit>0?1:0)+(graphicsDrawMesh>0?1:0)
                     +(graphicsOther>0?1:0);
        int passKinds=(passLiteral0>0?1:0)+(passLiteral1>0?1:0)
                     +(passOtherLiteral>0?1:0)+(passUnknown>0?1:0);
        bool onlyExplicitBlit=(graphics>0 && families==1 && graphicsBlit>0 &&
            blitExplicit>0 && blitImplicit==0 && blitOther==0);
        // Attribute roles to a pass ONLY when this exact field-load site
        // has one authenticated typed Blit call and one literal pass index.
        bool singlePass0=onlyExplicitBlit && blitExplicit==1 &&
            passKinds==1 && passLiteral0==1;
        bool singlePass1=onlyExplicitBlit && blitExplicit==1 &&
            passKinds==1 && passLiteral1==1;
        return new(inspected,boundary,receiver,arg,graphics,command,renderer,other,
            graphics>0 && families==1 && graphicsBlit>0 ? 1 : 0,
            graphics>0 && families==1 && graphicsDrawMesh>0 ? 1 : 0,
            graphics>0 && families==1 && graphicsOther>0 ? 1 : 0,
            graphics>0 && families>1 ? 1 : 0,
            graphics>0 && families==1 && graphicsBlit>0 &&
                blitImplicit>0 && blitExplicit==0 && blitOther==0 ? 1 : 0,
            graphics>0 && families==1 && graphicsBlit>0 &&
                blitExplicit>0 && blitImplicit==0 && blitOther==0 ? 1 : 0,
            graphics>0 && families==1 && graphicsBlit>0 &&
                blitOther>0 && blitImplicit==0 && blitExplicit==0 ? 1 : 0,
            graphics>0 && families==1 && graphicsBlit>0 &&
                ((blitImplicit>0?1:0)+(blitExplicit>0?1:0)+(blitOther>0?1:0)>1) ? 1 : 0,
            onlyExplicitBlit && passKinds==1 && passLiteral0>0 ? 1 : 0,
            onlyExplicitBlit && passKinds==1 && passLiteral1>0 ? 1 : 0,
            onlyExplicitBlit && passKinds==1 && passOtherLiteral>0 ? 1 : 0,
            onlyExplicitBlit && passKinds==1 && passUnknown>0 ? 1 : 0,
            onlyExplicitBlit && passKinds>1 ? 1 : 0,
            onlyExplicitBlit && blitExplicit==1 && sourceKind==1 ? 1 : 0,
            onlyExplicitBlit && blitExplicit==1 && sourceKind==2 ? 1 : 0,
            onlyExplicitBlit && (blitExplicit!=1 || sourceKind==0) ? 1 : 0,
            onlyExplicitBlit && blitExplicit==1 && destinationKind==1 ? 1 : 0,
            onlyExplicitBlit && blitExplicit==1 && destinationKind==2 ? 1 : 0,
            onlyExplicitBlit && (blitExplicit!=1 || destinationKind==0) ? 1 : 0,
            singlePass0 && sourceKind==1 ? 1 : 0,
            singlePass0 && sourceKind==2 ? 1 : 0,
            singlePass0 && sourceKind==3 ? 1 : 0,
            singlePass0 && destinationKind==1 ? 1 : 0,
            singlePass0 && destinationKind==2 ? 1 : 0,
            singlePass0 && destinationKind==3 ? 1 : 0,
            singlePass1 && sourceKind==1 ? 1 : 0,
            singlePass1 && sourceKind==2 ? 1 : 0,
            singlePass1 && sourceKind==3 ? 1 : 0,
            singlePass1 && destinationKind==1 ? 1 : 0,
            singlePass1 && destinationKind==2 ? 1 : 0,
            singlePass1 && destinationKind==3 ? 1 : 0);
    }

    private static MaterialConsumer ConsumeMaterialResult(MethodDefinition method,int ctorIndex)
    {
        var il=method.Body.Instructions;
        int next=ImmediateAfterNops(il,ctorIndex);
        int skipped=next-ctorIndex-1;
        if(next>=il.Count) return new("unproved",null,null,skipped);
        var x=il[next];
        if(x.OpCode.Code is Code.Stfld or Code.Stsfld)
        {
            if(ResolveMaterialField(x,method.Module,out var field))
                return new(x.OpCode.Code==Code.Stfld?"instance_material_field":"static_material_field",
                    field,null,skipped);
            return new("unproved",null,null,skipped);
        }
        var local=LocalForStore(method,x);
        if(local is not null)
            return new(local.VariableType.FullName==MaterialType?"material_local":"unproved",
                null,local,skipped);
        if(x.OpCode.Code==Code.Ret && method.ReturnType.FullName==MaterialType)
            return new("material_return",null,null,skipped);
        int setter=RendererMaterialSetter(x);
        if(setter==1) return new("direct_renderer_material_setter",null,null,skipped);
        if(setter==2) return new("direct_renderer_shared_material_setter",null,null,skipped);
        if(x.OpCode.Code==Code.Pop)
            return new("discarded_pop",null,null,skipped);
        if(x.OpCode.Code==Code.Dup)
            return new("duplicated_unresolved",null,null,skipped);
        return new("unproved",null,null,skipped);
    }
    private sealed record DupMaterialProbe(int TypedInitializerSetterCalls,
        FieldDefinition? MaterialField, VariableDefinition? MaterialLocal, int SkippedNops);

    private static DupMaterialProbe AnalyzeDupMaterialObjectInitializer(MethodDefinition method, int ctorIndex)
    {
        // Deliberately narrow and fail-closed: preserve both aliases after newobj;
        // one duplicate must be consumed by a typed one-string instance setter,
        // leaving the original Material reference for an exact material store.
        // No branch or ambiguous call chain is traversed.
        var il=method.Body.Instructions;
        int dup=ImmediateAfterNops(il,ctorIndex);
        if(dup>=il.Count || il[dup].OpCode.Code!=Code.Dup)
            return new(0,null,null,0);
        int nops=dup-ctorIndex-1;
        int literal=ImmediateAfterNops(il,dup);
        if(literal>=il.Count || il[literal].OpCode.Code!=Code.Ldstr)
            return new(0,null,null,nops);
        nops+=literal-dup-1;
        int setterIndex=ImmediateAfterNops(il,literal);
        if(setterIndex>=il.Count || il[setterIndex].OpCode.Code is not (Code.Call or Code.Callvirt)
            || il[setterIndex].Operand is not MethodReference setter
            || !setter.HasThis || !setter.Name.StartsWith("set_",StringComparison.Ordinal)
            || setter.ReturnType.FullName!="System.Void"
            || setter.Parameters.Count!=1 || setter.Parameters[0].ParameterType.FullName!="System.String"
            || setter.DeclaringType.FullName is not ("UnityEngine.Object" or "UnityEngine.Material"))
            return new(0,null,null,nops);
        nops+=setterIndex-literal-1;
        int storeIndex=ImmediateAfterNops(il,setterIndex);
        nops+=storeIndex-setterIndex-1;
        if(storeIndex>=il.Count)
            return new(1,null,null,nops);
        var store=il[storeIndex];
        if(store.OpCode.Code is Code.Stfld or Code.Stsfld)
        {
            if(ResolveMaterialField(store,method.Module,out var field))
                return new(1,field,null,nops);
            return new(1,null,null,nops);
        }
        var local=LocalForStore(method,store);
        if(local is not null && local.VariableType.FullName==MaterialType)
            return new(1,null,local,nops);
        return new(1,null,null,nops);
    }
    private sealed record LinearMaterialTrace(
        int Inspected, int ConservativeBoundaries, int MaterialInstanceCalls,
        int OriginalMaterialFieldStores, int TypedMaterialLocalStores,
        int RendererSetMaterialArguments, int RendererSetSharedArguments,
        FieldDefinition? OriginalMaterialField);

    private static int FixedPopCount(Instruction inst)
    {
        string name=inst.OpCode.StackBehaviourPop.ToString();
        if(name=="Pop0")return 0;
        if(name=="Varpop" || !name.StartsWith("Pop",StringComparison.Ordinal))return -1;
        return name.Split('_').Length;
    }
    private static int FixedPushCount(Instruction inst)
    {
        string name=inst.OpCode.StackBehaviourPush.ToString();
        if(name=="Push0")return 0;
        if(name=="Varpush" || !name.StartsWith("Push",StringComparison.Ordinal))return -1;
        return name.Split('_').Length;
    }
    private static LinearMaterialTrace TraceMaterialAliasLinear(MethodDefinition m,int ctorIndex)
    {
        // Straight-line, bounded, source-only stack taint. Initial stack contains
        // one authenticated original Material result. Inputs below it are unknown.
        // Stop at any branch or unknown stack behavior; do NOT infer runtime path
        // dominance, Unity material assignment or Android rendering.
        var il=m.Body.Instructions;
        var stack=new List<bool>{true};
        var locals=new Dictionary<int,bool>();
        var knownFields=new HashSet<FieldDefinition>();
        int inspected=0, boundaries=0, materialCalls=0, fieldStores=0,
            localStores=0, rendererCalls=0, sharedCalls=0;
        bool Pop()
        {
            if(stack.Count==0)return false; // unknown preexisting lower stack
            bool v=stack[^1];stack.RemoveAt(stack.Count-1);return v;
        }
        for(int i=ctorIndex+1;i<il.Count && inspected<48;i++)
        {
            var x=il[i];
            if(x.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw)
            {boundaries++;break;}
            inspected++;
            if(x.OpCode.Code==Code.Nop)continue;
            if(x.OpCode.Code==Code.Dup)
            {
                bool last=Pop();stack.Add(last);stack.Add(last);
                continue;
            }
            if(x.OpCode.Code is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if(x.Operand is not MethodReference callee) {boundaries++;break;}
                bool constructing=x.OpCode.Code==Code.Newobj;
                bool hasReceiver=!constructing && callee.HasThis;
                int pops=callee.Parameters.Count+(hasReceiver?1:0);
                if(pops>32){boundaries++;break;}
                var consumed=new List<bool>();
                for(int k=0;k<pops;k++)consumed.Add(Pop());
                bool receiverAlias=hasReceiver && consumed.Count>callee.Parameters.Count
                    && consumed[callee.Parameters.Count];
                if(receiverAlias && callee.DeclaringType.FullName is
                    ("UnityEngine.Material" or "UnityEngine.Object"))materialCalls++;
                if(consumed.Count>0 && consumed[0])
                {
                    int kind=RendererMaterialSetter(x);
                    if(kind==1)rendererCalls++;
                    if(kind==2)sharedCalls++;
                }
                if(constructing || callee.ReturnType.FullName!="System.Void")stack.Add(false);
                continue;
            }
            var storeLocal=LocalForStore(m,x);
            if(storeLocal is not null)
            {
                bool alias=Pop();
                locals[storeLocal.Index]=alias && storeLocal.VariableType.FullName==MaterialType;
                if(locals[storeLocal.Index])localStores++;
                continue;
            }
            VariableDefinition? loadLocal=null;
            if(x.OpCode.Code is Code.Ldloc or Code.Ldloc_S or
                Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3)
                loadLocal=m.Body.Variables.FirstOrDefault(v=>LocalIsLoadOf(x,v));
            if(loadLocal is not null)
            {
                stack.Add(locals.GetValueOrDefault(loadLocal.Index,false));
                continue;
            }
            if(x.OpCode.Code is Code.Stfld or Code.Stsfld)
            {
                bool valueAlias=Pop();
                if(x.OpCode.Code==Code.Stfld)Pop();
                if(valueAlias && ResolveMaterialField(x,m.Module,out var f) && f is not null)
                {
                    fieldStores++;
                    knownFields.Add(f);
                }
                continue;
            }
            int pop=FixedPopCount(x),push=FixedPushCount(x);
            if(pop<0 || push<0 || pop>6 || push>2) {boundaries++;break;}
            for(int k=0;k<pop;k++)Pop();
            for(int k=0;k<push;k++)stack.Add(false);
            if(!stack.Any(v=>v) && !locals.Values.Any(v=>v))break;
        }
        if(inspected>=48)boundaries++;
        // Two distinct destination fields cannot be silently merged into one.
        FieldDefinition? field=knownFields.Count==1?knownFields.Single():null;
        return new(inspected,boundaries,materialCalls,fieldStores,localStores,
            rendererCalls,sharedCalls,field);
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
        var originalMaterialSites=new List<(MethodDefinition Method,int Index)>();
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
                        if(DirectOriginalFieldToMaterialCtor(il,i))
                        {
                            directFieldToMaterialCtor++;
                            int ctorIndex=ImmediateAfterNops(il,i);
                            originalMaterialSites.Add((method,ctorIndex));
                        }
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
        if(originalMaterialSites.Count != 1 || directFieldToMaterialCtor != 1)
            throw new InvalidOperationException("original_Foam_material_direct_constructor_drift");
        var materialSite=originalMaterialSites[0];
        var materialResult=ConsumeMaterialResult(materialSite.Method,materialSite.Index);
        if(!MaterialKinds.Contains(materialResult.Kind))
            throw new InvalidOperationException("original_material_result_partition_drift");
        int materialFieldReads=0, materialFieldReaderMethods=0;
        int materialFieldToRenderer=0, materialFieldToSharedRenderer=0;
        int materialLocalLoads=0, materialLocalToRenderer=0, materialLocalToSharedRenderer=0;
        int directMaterialToRenderer=0, directMaterialToSharedRenderer=0;
        if(materialResult.Field is not null)
            foreach(var m in methods)
            {
                int reads=0;
                var il=m.Body.Instructions;
                for(int i=0;i<il.Count;i++)
                    if(SameMaterialFieldLoad(il[i],materialResult.Field))
                    {
                        reads++;
                        int setter=DirectRendererSetter(il,i);
                        if(setter==1) materialFieldToRenderer++;
                        if(setter==2) materialFieldToSharedRenderer++;
                    }
                if(reads>0) {materialFieldReads+=reads;materialFieldReaderMethods++;}
            }
        if(materialResult.Local is not null && materialResult.Kind=="material_local")
        {
            var il=materialSite.Method.Body.Instructions;
            for(int i=materialSite.Index+1;i<il.Count;i++)
                if(LocalIsLoadOf(il[i],materialResult.Local))
                {
                    materialLocalLoads++;
                    int setter=DirectRendererSetter(il,i);
                    if(setter==1) materialLocalToRenderer++;
                    if(setter==2) materialLocalToSharedRenderer++;
                }
        }
        if(materialResult.Kind=="direct_renderer_material_setter") directMaterialToRenderer=1;
        if(materialResult.Kind=="direct_renderer_shared_material_setter") directMaterialToSharedRenderer=1;
        var materialBuckets=MaterialKinds.ToDictionary(
            x=>"material_result_consumer_"+x,
            y=>y==materialResult.Kind?1:0);
        var dupProbe=AnalyzeDupMaterialObjectInitializer(materialSite.Method,materialSite.Index);
        int dupFieldReads=0, dupFieldMethods=0, dupFieldDirectRenderer=0, dupFieldDirectShared=0;
        int dupLocalReads=0, dupLocalDirectRendererCandidates=0, dupLocalDirectSharedCandidates=0;
        if(dupProbe.MaterialField is not null)
            foreach(var method in methods)
            {
                int loads=0;
                var il=method.Body.Instructions;
                for(int i=0;i<il.Count;i++)
                    if(SameMaterialFieldLoad(il[i],dupProbe.MaterialField))
                    {
                        loads++;
                        var kind=DirectRendererSetter(il,i);
                        if(kind==1) dupFieldDirectRenderer++;
                        if(kind==2) dupFieldDirectShared++;
                    }
                if(loads>0) {dupFieldReads+=loads;dupFieldMethods++;}
            }
        if(dupProbe.MaterialLocal is not null)
        {
            var il=materialSite.Method.Body.Instructions;
            for(int i=materialSite.Index+1;i<il.Count;i++)
                if(LocalIsLoadOf(il[i],dupProbe.MaterialLocal))
                {
                    dupLocalReads++;
                    int kind=DirectRendererSetter(il,i);
                    if(kind==1) dupLocalDirectRendererCandidates++;
                    if(kind==2) dupLocalDirectSharedCandidates++;
                }
        }
        var trace=TraceMaterialAliasLinear(materialSite.Method,materialSite.Index);
        int linearFieldReads=0,linearFieldReaders=0,linearFieldToRenderer=0,linearFieldToShared=0;
        if(trace.OriginalMaterialField is not null)
            foreach(var method in methods)
            {
                var il=method.Body.Instructions;
                int reads=0;
                for(int i=0;i<il.Count;i++)
                    if(SameMaterialFieldLoad(il[i],trace.OriginalMaterialField))
                    {
                        reads++;
                        int renderer=DirectRendererSetter(il,i);
                        if(renderer==1)linearFieldToRenderer++;
                        if(renderer==2)linearFieldToShared++;
                    }
                if(reads>0){linearFieldReads+=reads;linearFieldReaders++;}
            }

        int fieldApiSites=0,fieldApiInstructions=0,fieldApiBoundaries=0,
            fieldApiReceiver=0,fieldApiMaterialArgs=0,fieldApiGraphics=0,
            fieldApiCommand=0,fieldApiRenderer=0,fieldApiOther=0,
            fieldApiGraphicsBlit=0,fieldApiGraphicsDrawMesh=0,
            fieldApiGraphicsOther=0,fieldApiGraphicsMixed=0,
            fieldApiBlitImplicit=0,fieldApiBlitExplicit=0,
            fieldApiBlitOther=0,fieldApiBlitMixed=0,
            fieldApiPassLiteral0=0,fieldApiPassLiteral1=0,
            fieldApiPassOtherLiteral=0,fieldApiPassUnknown=0,fieldApiPassMixed=0,
            fieldApiSourceTexture=0,fieldApiSourceRenderTexture=0,
            fieldApiSourceUnknown=0,fieldApiDestinationRenderTexture=0,
            fieldApiDestinationNull=0,fieldApiDestinationUnknown=0,
            fieldApiPass0SourceTexture=0,fieldApiPass0SourceRenderTexture=0,fieldApiPass0SourceUnknown=0,fieldApiPass0DestinationRenderTexture=0,fieldApiPass0DestinationNull=0,fieldApiPass0DestinationUnknown=0,
            fieldApiPass1SourceTexture=0,fieldApiPass1SourceRenderTexture=0,fieldApiPass1SourceUnknown=0,fieldApiPass1DestinationRenderTexture=0,fieldApiPass1DestinationNull=0,fieldApiPass1DestinationUnknown=0;
        if(trace.OriginalMaterialField is not null)
            foreach(var method in methods)
            {
                var il=method.Body.Instructions;
                for(int i=0;i<il.Count;i++)
                    if(SameMaterialFieldLoad(il[i],trace.OriginalMaterialField))
                    {
                        fieldApiSites++;
                        var api=TraceExactMaterialFieldRead(method,i);
                        fieldApiInstructions+=api.Inspected;
                        fieldApiBoundaries+=api.Boundary;
                        fieldApiReceiver+=api.MaterialReceiver>0?1:0;
                        fieldApiMaterialArgs+=api.TypedMaterialArgument>0?1:0;
                        fieldApiGraphics+=api.GraphicsArgument>0?1:0;
                        fieldApiCommand+=api.CommandBufferArgument>0?1:0;
                        fieldApiRenderer+=api.RendererArgument>0?1:0;
                        fieldApiOther+=api.OtherArgument>0?1:0;
                        fieldApiGraphicsBlit+=api.GraphicsBlit;
                        fieldApiGraphicsDrawMesh+=api.GraphicsDrawMesh;
                        fieldApiGraphicsOther+=api.GraphicsOther;
                        fieldApiGraphicsMixed+=api.GraphicsMixed;
                        fieldApiBlitImplicit+=api.BlitImplicitPass;
                        fieldApiBlitExplicit+=api.BlitExplicitPass;
                        fieldApiBlitOther+=api.BlitOtherSignature;
                        fieldApiBlitMixed+=api.BlitMixedSignatures;
                        fieldApiPassLiteral0+=api.BlitPassLiteral0;
                        fieldApiPassLiteral1+=api.BlitPassLiteral1;
                        fieldApiPassOtherLiteral+=api.BlitPassOtherLiteral;
                        fieldApiPassUnknown+=api.BlitPassUnknown;
                        fieldApiPassMixed+=api.BlitPassMixed;
                        fieldApiSourceTexture+=api.BlitSourceTexture;
                        fieldApiSourceRenderTexture+=api.BlitSourceRenderTexture;
                        fieldApiSourceUnknown+=api.BlitSourceUnknown;
                        fieldApiDestinationRenderTexture+=api.BlitDestinationRenderTexture;
                        fieldApiDestinationNull+=api.BlitDestinationNull;
                        fieldApiDestinationUnknown+=api.BlitDestinationUnknown;
                        fieldApiPass0SourceTexture+=api.BlitPass0SourceTexture;
                        fieldApiPass0SourceRenderTexture+=api.BlitPass0SourceRenderTexture;
                        fieldApiPass0SourceUnknown+=api.BlitPass0SourceUnknown;
                        fieldApiPass0DestinationRenderTexture+=api.BlitPass0DestinationRenderTexture;
                        fieldApiPass0DestinationNull+=api.BlitPass0DestinationNull;
                        fieldApiPass0DestinationUnknown+=api.BlitPass0DestinationUnknown;
                        fieldApiPass1SourceTexture+=api.BlitPass1SourceTexture;
                        fieldApiPass1SourceRenderTexture+=api.BlitPass1SourceRenderTexture;
                        fieldApiPass1SourceUnknown+=api.BlitPass1SourceUnknown;
                        fieldApiPass1DestinationRenderTexture+=api.BlitPass1DestinationRenderTexture;
                        fieldApiPass1DestinationNull+=api.BlitPass1DestinationNull;
                        fieldApiPass1DestinationUnknown+=api.BlitPass1DestinationUnknown;
                    }
            }
        if(fieldApiSites!=linearFieldReads)
            throw new InvalidOperationException("exact_material_field_api_site_coverage");
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
            ["original_Foam_source_field_to_Material_ctor_sites"]=originalMaterialSites.Count,
            ["material_result_exact_original_field_definition_resolved"]=materialResult.Field is null?0:1,
            ["material_result_original_material_field_loads"]=materialFieldReads,
            ["material_result_original_material_field_distinct_readers"]=materialFieldReaderMethods,
            ["material_result_material_field_direct_Renderer_set_material_arguments"]=materialFieldToRenderer,
            ["material_result_material_field_direct_Renderer_set_sharedMaterial_arguments"]=materialFieldToSharedRenderer,
            ["material_result_material_local_loads_after_constructor"]=materialLocalLoads,
            ["material_result_material_local_direct_Renderer_set_material_argument_candidates"]=materialLocalToRenderer,
            ["material_result_material_local_direct_Renderer_set_sharedMaterial_argument_candidates"]=materialLocalToSharedRenderer,
            ["material_result_material_constructor_direct_Renderer_set_material_arguments"]=directMaterialToRenderer,
            ["material_result_material_constructor_direct_Renderer_set_sharedMaterial_arguments"]=directMaterialToSharedRenderer,
            ["material_result_nops_skipped_after_ctor"]=materialResult.Nops,
            ["material_dup_followed_by_authentic_typed_string_instance_setter"]=dupProbe.TypedInitializerSetterCalls,
            ["material_dup_setter_followed_by_original_Material_field_store"]=dupProbe.MaterialField is null?0:1,
            ["material_dup_setter_followed_by_original_Material_local_store"]=dupProbe.MaterialLocal is null?0:1,
            ["material_dup_original_Material_field_read_instructions"]=dupFieldReads,
            ["material_dup_original_Material_field_read_methods"]=dupFieldMethods,
            ["material_dup_original_Material_field_direct_Renderer_set_material_args"]=dupFieldDirectRenderer,
            ["material_dup_original_Material_field_direct_Renderer_set_sharedMaterial_args"]=dupFieldDirectShared,
            ["material_dup_original_Material_local_loads"]=dupLocalReads,
            ["material_dup_original_Material_local_direct_Renderer_set_material_candidates"]=dupLocalDirectRendererCandidates,
            ["material_dup_original_Material_local_direct_Renderer_set_sharedMaterial_candidates"]=dupLocalDirectSharedCandidates,
            ["material_dup_nops_skipped_in_initializer_probe"]=dupProbe.SkippedNops,
            ["material_linear_original_material_alias_instructions_inspected"]=trace.Inspected,
            ["material_linear_original_material_alias_ambiguous_or_branch_boundaries"]=trace.ConservativeBoundaries,
            ["material_linear_original_material_instance_method_calls"]=trace.MaterialInstanceCalls,
            ["material_linear_original_material_field_stores"]=trace.OriginalMaterialFieldStores,
            ["material_linear_original_material_typed_local_stores"]=trace.TypedMaterialLocalStores,
            ["material_linear_original_material_direct_Renderer_set_material_args"]=trace.RendererSetMaterialArguments,
            ["material_linear_original_material_direct_Renderer_set_sharedMaterial_args"]=trace.RendererSetSharedArguments,
            ["material_linear_original_material_unique_field_definition_resolved"]=trace.OriginalMaterialField is null?0:1,
            ["material_linear_original_material_field_read_instructions"]=linearFieldReads,
            ["material_linear_original_material_field_distinct_reader_methods"]=linearFieldReaders,
            ["material_linear_original_material_field_direct_Renderer_set_material_args"]=linearFieldToRenderer,
            ["material_linear_original_material_field_direct_Renderer_set_sharedMaterial_args"]=linearFieldToShared,
            ["field_api_exact_original_material_field_sites_scanned"]=fieldApiSites,
            ["field_api_straightline_total_following_IL_instructions_scanned"]=fieldApiInstructions,
            ["field_api_straightline_sites_with_boundary_or_budget"]=fieldApiBoundaries,
            ["field_api_straightline_sites_with_typed_Material_receiver"]=fieldApiReceiver,
            ["field_api_straightline_sites_with_typed_Material_parameter"]=fieldApiMaterialArgs,
            ["field_api_straightline_sites_with_Graphics_Material_parameter"]=fieldApiGraphics,
            ["field_api_Graphics_material_sites_Blit"]=fieldApiGraphicsBlit,
            ["field_api_Graphics_material_sites_DrawMesh"]=fieldApiGraphicsDrawMesh,
            ["field_api_Graphics_material_sites_Other"]=fieldApiGraphicsOther,
            ["field_api_Graphics_material_sites_Mixed"]=fieldApiGraphicsMixed,
            ["field_api_Graphics_Blit_sites_ImplicitPass"]=fieldApiBlitImplicit,
            ["field_api_Graphics_Blit_sites_ExplicitPass"]=fieldApiBlitExplicit,
            ["field_api_Graphics_Blit_sites_OtherSignature"]=fieldApiBlitOther,
            ["field_api_Graphics_Blit_sites_MixedSignatures"]=fieldApiBlitMixed,
            ["field_api_Graphics_Blit_explicit_sites_pass_literal0"]=fieldApiPassLiteral0,
            ["field_api_Graphics_Blit_explicit_sites_pass_literal1"]=fieldApiPassLiteral1,
            ["field_api_Graphics_Blit_explicit_sites_pass_other_literal"]=fieldApiPassOtherLiteral,
            ["field_api_Graphics_Blit_explicit_sites_pass_unknown"]=fieldApiPassUnknown,
            ["field_api_Graphics_Blit_explicit_sites_pass_mixed"]=fieldApiPassMixed,
            ["field_api_Graphics_Blit_explicit_source_Texture"]=fieldApiSourceTexture,
            ["field_api_Graphics_Blit_explicit_source_RenderTexture"]=fieldApiSourceRenderTexture,
            ["field_api_Graphics_Blit_explicit_source_unknown"]=fieldApiSourceUnknown,
            ["field_api_Graphics_Blit_explicit_destination_RenderTexture"]=fieldApiDestinationRenderTexture,
            ["field_api_Graphics_Blit_explicit_destination_null"]=fieldApiDestinationNull,
            ["field_api_Graphics_Blit_explicit_destination_unknown"]=fieldApiDestinationUnknown,
            ["field_api_Graphics_Blit_pass0_source_Texture"]=fieldApiPass0SourceTexture,
            ["field_api_Graphics_Blit_pass0_source_RenderTexture"]=fieldApiPass0SourceRenderTexture,
            ["field_api_Graphics_Blit_pass0_source_unknown"]=fieldApiPass0SourceUnknown,
            ["field_api_Graphics_Blit_pass0_destination_RenderTexture"]=fieldApiPass0DestinationRenderTexture,
            ["field_api_Graphics_Blit_pass0_destination_null"]=fieldApiPass0DestinationNull,
            ["field_api_Graphics_Blit_pass0_destination_unknown"]=fieldApiPass0DestinationUnknown,
            ["field_api_Graphics_Blit_pass1_source_Texture"]=fieldApiPass1SourceTexture,
            ["field_api_Graphics_Blit_pass1_source_RenderTexture"]=fieldApiPass1SourceRenderTexture,
            ["field_api_Graphics_Blit_pass1_source_unknown"]=fieldApiPass1SourceUnknown,
            ["field_api_Graphics_Blit_pass1_destination_RenderTexture"]=fieldApiPass1DestinationRenderTexture,
            ["field_api_Graphics_Blit_pass1_destination_null"]=fieldApiPass1DestinationNull,
            ["field_api_Graphics_Blit_pass1_destination_unknown"]=fieldApiPass1DestinationUnknown,
            ["field_api_straightline_sites_with_CommandBuffer_Material_parameter"]=fieldApiCommand,
            ["field_api_straightline_sites_with_Renderer_Material_parameter"]=fieldApiRenderer,
            ["field_api_straightline_sites_with_other_typed_Material_parameter"]=fieldApiOther,
            ["original_Shader_Find_executed_in_Unity"]=false,
            ["field_declaring_TypeDef_is_427_scene_script_proven"]=false,
            ["Unity_Material_or_Renderer_actual_binding_verified"]=false,
            ["original_Foam_CB0_runtime_upload_verified"]=false,
            ["Android_water_pixels_verified"]=false,
            ["private_original_names_fields_method_IDs_or_IL_exported"]=false
        };
        foreach(var (name,value) in buckets) output[name]=value;
        foreach(var (name,value) in materialBuckets) output[name]=value;
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
        var material=new TypeReference("UnityEngine","Material",mod,mod.TypeSystem.CoreLibrary);
        var matCtor=new MethodReference(".ctor",mod.TypeSystem.Void,material){HasThis=true};
        matCtor.Parameters.Add(new ParameterDefinition(shader));
        method.Body.Instructions[2]=Instruction.Create(OpCodes.Newobj,matCtor);
        var matLocal=new VariableDefinition(material);
        method.Body.Variables.Add(matLocal);
        method.Body.Instructions.Insert(3,Instruction.Create(OpCodes.Stloc,matLocal));
        if(ConsumeMaterialResult(method,2).Kind!="material_local")
            throw new InvalidOperationException("material_local_source_provenance");
        var matField=new FieldDefinition("materialSynthetic",Mono.Cecil.FieldAttributes.Static,material);
        owner.Fields.Add(matField);
        method.Body.Instructions[3]=Instruction.Create(OpCodes.Stsfld,matField);
        if(ConsumeMaterialResult(method,2).Kind!="static_material_field"
            || !SameMaterialFieldLoad(Instruction.Create(OpCodes.Ldsfld,matField),matField))
            throw new InvalidOperationException("material_field_provenance");
        var renderer=new TypeReference("UnityEngine","Renderer",mod,mod.TypeSystem.CoreLibrary);
        var setter=new MethodReference("set_material",mod.TypeSystem.Void,renderer){HasThis=true};
        setter.Parameters.Add(new ParameterDefinition(material));
        method.Body.Instructions[3]=Instruction.Create(OpCodes.Callvirt,setter);
        if(ConsumeMaterialResult(method,2).Kind!="direct_renderer_material_setter"
           || DirectRendererSetter(method.Body.Instructions,2)!=1)
            throw new InvalidOperationException("material_renderer_signature");
        var impostor=new MethodReference("set_material",mod.TypeSystem.Void,renderer){HasThis=false};
        impostor.Parameters.Add(new ParameterDefinition(material));
        if(RendererMaterialSetter(Instruction.Create(OpCodes.Call,impostor))!=0)
            throw new InvalidOperationException("no_fake_renderer_setter");
        method.Body.Instructions[3]=Instruction.Create(OpCodes.Pop);
        if(ConsumeMaterialResult(method,2).Kind!="discarded_pop")
            throw new InvalidOperationException("material_discarded");
        method.Body.Instructions[3]=Instruction.Create(OpCodes.Dup);
        method.Body.Instructions.Insert(4,Instruction.Create(OpCodes.Ldstr,"SYNTHETIC_ONLY"));
        var objectType=new TypeReference("UnityEngine","Object",mod,mod.TypeSystem.CoreLibrary);
        var setName=new MethodReference("set_name",mod.TypeSystem.Void,objectType){HasThis=true};
        setName.Parameters.Add(new ParameterDefinition(mod.TypeSystem.String));
        method.Body.Instructions.Insert(5,Instruction.Create(OpCodes.Callvirt,setName));
        method.Body.Instructions.Insert(6,Instruction.Create(OpCodes.Stsfld,matField));
        var dupProbe=AnalyzeDupMaterialObjectInitializer(method,2);
        if(dupProbe.TypedInitializerSetterCalls!=1 || dupProbe.MaterialField!=matField)
            throw new InvalidOperationException("typed_dup_original_material_field");
        var wrongSetter=new MethodReference("set_name",mod.TypeSystem.Void,objectType){HasThis=false};
        wrongSetter.Parameters.Add(new ParameterDefinition(mod.TypeSystem.String));
        method.Body.Instructions[5]=Instruction.Create(OpCodes.Call,wrongSetter);
        if(AnalyzeDupMaterialObjectInitializer(method,2).TypedInitializerSetterCalls!=0)
            throw new InvalidOperationException("untyped_dup_setter_rejected");
        method.Body.Instructions[5]=Instruction.Create(OpCodes.Callvirt,setName);
        var linear=TraceMaterialAliasLinear(method,2);
        if(linear.OriginalMaterialField!=matField ||
           linear.OriginalMaterialFieldStores!=1 ||
           linear.MaterialInstanceCalls!=1)
            throw new InvalidOperationException("typed_material_dup_linear_flow");
        method.Body.Instructions[5]=Instruction.Create(OpCodes.Br_S,method.Body.Instructions[6]);
        if(TraceMaterialAliasLinear(method,2).ConservativeBoundaries==0)
            throw new InvalidOperationException("branch_must_stop_original_trace");

        var traceMethod=new MethodDefinition("SyntheticMaterialCall",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
            mod.TypeSystem.Void);
        owner.Methods.Add(traceMethod);
        var gfx=new TypeReference("UnityEngine","Graphics",mod,mod.TypeSystem.CoreLibrary);
        var draw=new MethodReference("DrawSynthetic",mod.TypeSystem.Void,gfx){HasThis=false};
        draw.Parameters.Add(new ParameterDefinition(material));
        draw.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Object));
        traceMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,matField));
        traceMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ldnull));
        traceMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Call,draw));
        traceMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        var exact=TraceExactMaterialFieldRead(traceMethod,0);
        if(exact.TypedMaterialArgument!=1 || exact.GraphicsArgument!=1 ||
           exact.GraphicsOther!=1 || exact.GraphicsBlit!=0 ||
           exact.RendererArgument!=0 || exact.Boundary!=0)
            throw new InvalidOperationException("typed_Graphics_argument_stack_identity");
        var localForTrace=new VariableDefinition(material);
        traceMethod.Body.Variables.Add(localForTrace);
        traceMethod.Body.Instructions.Insert(1,Instruction.Create(OpCodes.Stloc,localForTrace));
        traceMethod.Body.Instructions.Insert(2,Instruction.Create(OpCodes.Ldloc,localForTrace));
        exact=TraceExactMaterialFieldRead(traceMethod,0);
        if(exact.GraphicsArgument!=1 || exact.TypedMaterialArgument!=1 ||
           exact.GraphicsOther!=1 || exact.Inspected<4)
            throw new InvalidOperationException("nonadjacent_original_field_local_alias");
        draw.Name="Blit";
        exact=TraceExactMaterialFieldRead(traceMethod,0);
        if(exact.GraphicsBlit!=1 || exact.GraphicsDrawMesh!=0 ||
           exact.GraphicsOther!=0 || exact.BlitOtherSignature!=1)
            throw new InvalidOperationException("Graphics_Blit_public_typed_route");
        // A Blit name with wrong overload signature must not imply pass semantics.
        var texture=new TypeReference("UnityEngine","Texture",mod,mod.TypeSystem.CoreLibrary);
        var renderTexture=new TypeReference("UnityEngine","RenderTexture",mod,mod.TypeSystem.CoreLibrary);
        var blit3=new MethodReference("Blit",mod.TypeSystem.Void,gfx){HasThis=false};
        blit3.Parameters.Add(new ParameterDefinition(texture));
        blit3.Parameters.Add(new ParameterDefinition(renderTexture));
        blit3.Parameters.Add(new ParameterDefinition(material));
        var blit4=new MethodReference("Blit",mod.TypeSystem.Void,gfx){HasThis=false};
        blit4.Parameters.Add(new ParameterDefinition(texture));
        blit4.Parameters.Add(new ParameterDefinition(renderTexture));
        blit4.Parameters.Add(new ParameterDefinition(material));
        blit4.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Int32));
        var overloadTest=new MethodDefinition("SyntheticBlitOverload",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
            mod.TypeSystem.Void);
        owner.Methods.Add(overloadTest);
        overloadTest.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,matField));
        overloadTest.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit3));
        overloadTest.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        exact=TraceExactMaterialFieldRead(overloadTest,0);
        if(exact.GraphicsBlit!=1 || exact.BlitImplicitPass!=1 ||
           exact.BlitExplicitPass!=0 || exact.BlitOtherSignature!=0)
            throw new InvalidOperationException("Blit_implicit_public_overload");
        overloadTest.Body.Instructions[1]=Instruction.Create(OpCodes.Ldc_I4_1);
        overloadTest.Body.Instructions.Insert(2,Instruction.Create(OpCodes.Call,blit4));
        exact=TraceExactMaterialFieldRead(overloadTest,0);
        if(exact.GraphicsBlit!=1 || exact.BlitExplicitPass!=1 ||
           exact.BlitPassLiteral1!=1 || exact.BlitPassLiteral0!=0 ||
           exact.BlitImplicitPass!=0 || exact.BlitOtherSignature!=0)
            throw new InvalidOperationException("Blit_explicit_int_pass_public_overload");
        overloadTest.Body.Instructions[1]=Instruction.Create(OpCodes.Ldc_I4_0);
        exact=TraceExactMaterialFieldRead(overloadTest,0);
        if(exact.BlitPassLiteral0!=1 || exact.BlitPassLiteral1!=0)
            throw new InvalidOperationException("Blit_pass_literal_zero");
        overloadTest.Body.Instructions[1]=Instruction.Create(OpCodes.Ldc_I4_7);
        exact=TraceExactMaterialFieldRead(overloadTest,0);
        if(exact.BlitPassOtherLiteral!=1 || exact.BlitPassLiteral0!=0)
            throw new InvalidOperationException("Blit_other_public_literal");
        overloadTest.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Int32));
        overloadTest.Body.Instructions[1]=Instruction.Create(OpCodes.Ldarg_0);
        exact=TraceExactMaterialFieldRead(overloadTest,0);
        if(exact.BlitPassUnknown!=1 || exact.BlitPassLiteral1!=0)
            throw new InvalidOperationException("Blit_dynamic_not_guessed");
        // One field source may feed two explicit Blit overload calls:
        // disjoint pass literals must be classified as MIXED, not double count.
        var literalMix=new MethodDefinition("SyntheticTwoPassLiteralSources",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
            mod.TypeSystem.Void);
        owner.Methods.Add(literalMix);
        var sharedMaterialLocal=new VariableDefinition(material);
        literalMix.Body.Variables.Add(sharedMaterialLocal);
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,matField));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Stloc,sharedMaterialLocal));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Ldloc,sharedMaterialLocal));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_0));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit4));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Ldloc,sharedMaterialLocal));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_1));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit4));
        literalMix.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        exact=TraceExactMaterialFieldRead(literalMix,0);
        if(exact.BlitExplicitPass!=1 || exact.BlitPassMixed!=1 ||
           exact.BlitPassLiteral0!=0 || exact.BlitPassLiteral1!=0 ||
           exact.BlitPass0SourceUnknown!=0 || exact.BlitPass1SourceUnknown!=0)
            throw new InvalidOperationException("Blit_pass_mixed_exclusive_source");
        var multiBlit=new MethodDefinition("SyntheticTwoBlitOverloads",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
            mod.TypeSystem.Void);
        owner.Methods.Add(multiBlit);
        var matAlias=new VariableDefinition(material);
        multiBlit.Body.Variables.Add(matAlias);
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,matField));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Stloc,matAlias));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Ldloc,matAlias));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit3));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Ldloc,matAlias));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_1));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit4));
        multiBlit.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        exact=TraceExactMaterialFieldRead(multiBlit,0);
        if(exact.GraphicsBlit!=1 || exact.BlitMixedSignatures!=1 ||
           exact.BlitImplicitPass!=0 || exact.BlitExplicitPass!=0)
            throw new InvalidOperationException("Blit_mixed_overload_exclusive");
        // Exact direct stack operands: source and destination are classified
        // only when adjacent, not from an unrelated instruction or name.
        var syntheticTextureSource=new FieldDefinition("SyntheticTexture",
            Mono.Cecil.FieldAttributes.Static|Mono.Cecil.FieldAttributes.Private,texture);
        var syntheticRenderTarget=new FieldDefinition("SyntheticTarget",
            Mono.Cecil.FieldAttributes.Static|Mono.Cecil.FieldAttributes.Private,renderTexture);
        owner.Fields.Add(syntheticTextureSource);
        owner.Fields.Add(syntheticRenderTarget);
        var imageTrace=new MethodDefinition("SyntheticDirectBlit",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
            mod.TypeSystem.Void);
        owner.Methods.Add(imageTrace);
        imageTrace.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,syntheticTextureSource));
        imageTrace.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,syntheticRenderTarget));
        imageTrace.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,matField));
        imageTrace.Body.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_0));
        imageTrace.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit4));
        imageTrace.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        var roles=TraceExactMaterialFieldRead(imageTrace,2);
        if(roles.BlitSourceTexture!=1 || roles.BlitDestinationRenderTexture!=1 ||
           roles.BlitDestinationUnknown!=0 ||
           roles.BlitPass0SourceTexture!=1 ||
           roles.BlitPass0DestinationRenderTexture!=1 ||
           roles.BlitPass1SourceTexture!=0 ||
           roles.BlitPass1DestinationRenderTexture!=0)
            throw new InvalidOperationException("direct_Texture_RenderTexture_producer");
        imageTrace.Body.Instructions[3]=Instruction.Create(OpCodes.Ldc_I4_1);
        roles=TraceExactMaterialFieldRead(imageTrace,2);
        if(roles.BlitPass1SourceTexture!=1 ||
           roles.BlitPass1DestinationRenderTexture!=1 ||
           roles.BlitPass0SourceTexture!=0 ||
           roles.BlitPass0DestinationRenderTexture!=0)
            throw new InvalidOperationException("pass1_direct_Texture_RenderTexture_producer");
        imageTrace.Body.Instructions[3]=Instruction.Create(OpCodes.Ldc_I4_0);
        imageTrace.Body.Instructions[1]=Instruction.Create(OpCodes.Ldnull);
        roles=TraceExactMaterialFieldRead(imageTrace,2);
        if(roles.BlitSourceTexture!=1 || roles.BlitDestinationNull!=1)
            throw new InvalidOperationException("direct_null_destination");
        imageTrace.Body.Instructions[0]=Instruction.Create(OpCodes.Ldsfld,syntheticRenderTarget);
        roles=TraceExactMaterialFieldRead(imageTrace,2);
        if(roles.BlitSourceRenderTexture!=1 || roles.BlitDestinationNull!=1)
            throw new InvalidOperationException("direct_RenderTexture_source");
        imageTrace.Body.Instructions[1]=Instruction.Create(OpCodes.Ldc_I4_0);
        roles=TraceExactMaterialFieldRead(imageTrace,2);
        if(roles.BlitDestinationUnknown!=1 || roles.BlitDestinationNull!=0)
            throw new InvalidOperationException("non_Texture_destination_unknown");
        imageTrace.Body.Instructions[1]=Instruction.Create(OpCodes.Ldsfld,syntheticRenderTarget);
        imageTrace.Body.Instructions.Insert(3,Instruction.Create(OpCodes.Dup));
        roles=TraceExactMaterialFieldRead(imageTrace,2);
        if(roles.BlitSourceUnknown!=1 || roles.BlitDestinationUnknown!=1)
            throw new InvalidOperationException("noncanonical_stack_unknown");
        draw.Name="DrawMesh";
        exact=TraceExactMaterialFieldRead(traceMethod,0);
        if(exact.GraphicsDrawMesh!=1 || exact.GraphicsBlit!=0 || exact.GraphicsOther!=0)
            throw new InvalidOperationException("Graphics_DrawMesh_public_typed_route");
        draw.Name="DrawSynthetic";
        var blit=new MethodReference("Blit",mod.TypeSystem.Void,gfx){HasThis=false};
        blit.Parameters.Add(new ParameterDefinition(material));
        blit.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Object));
        var mixedMethod=new MethodDefinition("SyntheticTwoGraphicsFamilies",
            Mono.Cecil.MethodAttributes.Static|Mono.Cecil.MethodAttributes.Public,
            mod.TypeSystem.Void);
        owner.Methods.Add(mixedMethod);
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ldsfld,matField));
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Dup));
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ldnull));
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Call,draw));
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ldnull));
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Call,blit));
        mixedMethod.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        exact=TraceExactMaterialFieldRead(mixedMethod,0);
        if(exact.GraphicsArgument!=2 || exact.GraphicsMixed!=1 ||
           exact.GraphicsBlit!=0 || exact.GraphicsOther!=0)
            throw new InvalidOperationException("Graphics_mixed_exclusive_route");
        var fake=new MethodReference("DrawSynthetic",mod.TypeSystem.Void,gfx){HasThis=false};
        fake.Parameters.Add(new ParameterDefinition(shader));
        fake.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Object));
        traceMethod.Body.Instructions[4]=Instruction.Create(OpCodes.Call,fake);
        exact=TraceExactMaterialFieldRead(traceMethod,0);
        if(exact.TypedMaterialArgument!=0 || exact.GraphicsBlit!=0 ||
           exact.GraphicsDrawMesh!=0 || exact.GraphicsOther!=0 ||
           exact.GraphicsMixed!=0)
            throw new InvalidOperationException("reject_untyped_fake_material_argument");
        traceMethod.Body.Instructions[4]=Instruction.Create(OpCodes.Call,draw);
        traceMethod.Body.Instructions[3]=Instruction.Create(OpCodes.Br_S,traceMethod.Body.Instructions[4]);
        exact=TraceExactMaterialFieldRead(traceMethod,0);
        if(exact.Boundary!=1 || exact.GraphicsArgument!=0)
            throw new InvalidOperationException("no_control_flow_crossing");
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
