"""GFX092: bounded original input-lane uses at the 12 actual SPV reads.

Only anonymous relations leave the caller. Numeric Location coincidence is a
candidate, not semantic identity. Missing Component is never interpreted as x.
Unknown opcodes remain uncovered; this is not a complete def-use proof.
"""
from collections import Counter
import struct
from gfxlab.tools.multi_shader_spv_actual_input_mask_width091 import authenticated_spv_CB_index_actual_input_component_width091
from gfxlab.tools.multi_shader_original_cb_relative_expression067 import decode_original_operand_tree
from gfxlab.tools.multi_shader_original_cb_access_shapes import KNOWN_ARITHMETIC_ARITY
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import MAX_DWORDS, MAX_INST, CUSTOMDATA, SAMPLE_LAYOUTS

# Public documented one-destination ALU operand arities; not arbitrary word scans.
ARITIES={**KNOWN_ARITHMETIC_ARITY,1:3,27:2,28:2,30:3,35:4,41:3,42:3,
         43:2,55:4,59:2,60:3,85:3,86:2,87:3,
         **{op:nsrc+1 for op,(_,_,nsrc) in SAMPLE_LAYOUTS.items()}}

def selected_source_lanes(tree):
    """Syntactically selected lanes, not instruction-consumed vector lanes."""
    if tree['components']!=2:return None
    mode=tree['selection'];bits=tree['component_token_bits']
    if mode==2:return {bits&3}
    if mode==1:return {(bits>>(2*i))&3 for i in range(4)}
    # Masks are destination/declaration syntax, not an assumed source swizzle.
    return None

def private_source_input_use_summary(shdr,reg,mask):
    if (not isinstance(shdr,bytes) or not 8<=len(shdr)<=MAX_DWORDS*4 or len(shdr)%4
        or type(reg)!=int or not 0<=reg<=65535 or type(mask)!=int
        or not 0<mask<=15 or mask.bit_count()!=1):
        raise ValueError('GFX092_INVALID_PRIVATE_INPUT')
    words=struct.unpack('<%dI'%(len(shdr)//4),shdr)
    if words[1]!=len(words):raise ValueError('GFX092_LENGTH')
    lane=mask.bit_length()-1
    counts=Counter();at=2;steps=0
    while at<len(words):
        tok=words[at];op=tok&2047
        n=(words[at+1] if at+1<len(words) else 0) if op==CUSTOMDATA else (tok>>24)&127
        if n<1 or at+n>len(words) or steps>=MAX_INST:raise ValueError('GFX092_INSTRUCTION_BOUNDS')
        if op in ARITIES:
            pos=at+1;ext=bool(tok&0x80000000);ne=0
            while ext:
                if pos>=at+n or ne>=4:raise ValueError('GFX092_EXTENDED_OPCODE')
                extra=words[pos];pos+=1;ne+=1;ext=bool(extra&0x80000000)
            operands=[]
            for _ in range(ARITIES[op]):
                tree,pos=decode_original_operand_tree(words,pos,at+n);operands.append(tree)
            if pos!=at+n:raise ValueError('GFX092_OPERAND_TERMINATION')
            for tree in operands[1:]:
                # Relative children are separately marked, never silently omitted.
                if any(index[0]=='relative' for index in tree['indices']):
                    counts['relative_operand_not_traversed']+=1
                if tree['type']!=1:continue
                if (tree['dimension']!=1 or len(tree['indices'])!=1 or
                    tree['indices'][0][0]!='literal32'):
                    counts['input_operand_unresolved_index']+=1;continue
                if tree['indices'][0][1]!=reg:continue
                lanes=selected_source_lanes(tree)
                if lanes is None:counts['matched_register_unresolved_selection']+=1
                elif lanes=={lane}:counts['matched_register_only_signature_lane_selected']+=1
                elif lane in lanes:counts['matched_register_signature_lane_and_other_lanes_selected']+=1
                else:counts['matched_register_signature_lane_not_selected']+=1
                if tree['extensions']:counts['matched_register_operand_modifier_present']+=1
            counts['covered_alu_or_sample_instructions']+=1
        elif 88<=op<=106 or op==CUSTOMDATA:
            counts['declaration_or_customdata_not_scanned']+=1
        else:counts['unsupported_instructions_not_scanned']+=1
        at+=n;steps+=1
    return counts

def audit_actual_input_lanes092(dis,auth,shdr,source_cb,dxbc,stage):
    counts=Counter()
    def observe(load_id,defs,decs,source_mask,target_width):
        counts['actual_input_candidates']+=1
        op,args=defs.get(load_id,(None,[]))
        if op!='OpLoad' or len(args)!=2:
            counts['untrusted_actual_input_load']+=1;return
        root=args[1];rop,ra=defs.get(root,(None,[]))
        if rop!='OpVariable' or len(ra)<2 or ra[1]!='Input':
            counts['untrusted_actual_input_root']+=1;return
        loc=decs.get((root,'Location'),set())
        if len(loc)!=1 or len(next(iter(loc)))!=1 or not next(iter(loc))[0].isdigit():
            counts['untrusted_Location']+=1;return
        location=int(next(iter(loc))[0]);mask=source_mask(location)
        if mask is None or mask.bit_count()!=1:
            counts['no_unique_single_component_source_mask']+=1;return
        width,_=target_width(load_id)
        if width!=1:counts['target_not_verified_scalar32']+=1;return
        lane=mask.bit_length()-1
        # Class only: never export the original lane number or mask bits.
        counts['source_single_lane_first' if lane==0 else 'source_single_lane_nonfirst']+=1
        comp=decs.get((root,'Component'),set())
        if not comp:counts['target_Component_absent_lane_identity_unproven']+=1
        elif (len(comp)==1 and len(next(iter(comp)))==1 and
              next(iter(comp))[0].isdigit() and 0<=int(next(iter(comp))[0])<=3):
            target=int(next(iter(comp))[0])
            counts['explicit_Component_equals_source_lane_candidate' if target==lane
                   else 'explicit_Component_differs_source_lane']+=1
        else:counts['target_Component_ambiguous_or_invalid']+=1
        uses=private_source_input_use_summary(shdr,location,mask)
        counts.update(uses)
        hit=sum(uses[k] for k in ('matched_register_only_signature_lane_selected',
                  'matched_register_signature_lane_and_other_lanes_selected',
                  'matched_register_signature_lane_not_selected',
                  'matched_register_unresolved_selection'))
        counts['candidate_with_source_input_uses' if hit else 'candidate_without_covered_source_input_uses']+=1
    previous=authenticated_spv_CB_index_actual_input_component_width091(
        dis,auth,shdr,source_cb,dxbc,stage,private_input_observer=observe)
    return {**dict(counts),'authenticated_dynamic_CB_loads':previous.get(
          'SPV_original_b_authenticated_actual_dynamic_CB_OpLoads',0),
          'source_lane_to_translated_value_identity_proven':False,
          'complete_DXBC_input_use_coverage':False,
          'Unity_Material_CB_bytes_proven':False,
          'originalShaderRestored':False,'phase_closed':False}
