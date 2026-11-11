"""GFX103: source-exact DXBC interpolation versus generated GLES3, fail-closed.

Original Shader48 data is parsed only in private execution. Never prints
proprietary code, registers, keywords, source text, or source paths.
"""
import re
import struct
from collections import Counter

NV="GL_NV_shader_noperspective_interpolation"
MODES={0:"undefined",1:"constant",2:"linear",3:"linear_centroid",
       4:"linear_noperspective",5:"linear_noperspective_centroid",
       6:"linear_sample",7:"linear_noperspective_sample"}
# Drop comments/quoted strings before detecting qualifiers; a diagnostic comment
# must never masquerade as an actual GLSL input/output declaration.
COMMENT_OR_STRING=re.compile(r'/\\*[\\s\\S]*?\\*/|//[^\\n]*|"(?:\\\\.|[^"\\\\])*"')
NATIVE=re.compile(r"\\b(?:noperspective\\s+(?:(?:centroid|sample)\\s+)?|(?:centroid|sample)\\s+noperspective\\s+)(?:in|out)\\b")
def has_native_interpolation(source):
    return bool(NATIVE.search(COMMENT_OR_STRING.sub("",source)))
VERSION=re.compile(r"\A#version\s+(300|310|320)\s+es\s*\n")
DIRECTIVE=re.compile(r"(?m)^#extension\s+"+NV+r"\s*:\s*(require|enable|warn|disable)\s*$")

def dxbc_fragment_input_classes(chunk):
    """Classify only DCL_INPUT_PS (98), SIV (100), SGV (99) input modes.

    D3D10 tokenized program: opcode bits 10:0, length bits 30:24,
    interpolation bits 14:11. SIV is a system-interpreted input; it
    cannot be equated with an ordinary varying without semantic proof.
    """
    if not isinstance(chunk,bytes) or len(chunk)<12 or len(chunk)%4:
        raise ValueError("GFX103_INVALID_SHDR_BYTES")
    words=struct.unpack("<%dI"%(len(chunk)//4),chunk)
    if words[1]!=len(words) or len(words)>2_000_000:
        raise ValueError("GFX103_DECLARED_SHDR_LENGTH")
    ordinary=Counter();siv=Counter();sgv=0;i=2;steps=0
    while i<len(words):
        token=words[i];opcode=token&2047
        if opcode==53:
            if i+1>=len(words):raise ValueError("GFX103_CUSTOM_LENGTH_MISSING")
            length=words[i+1]
            if length<2:raise ValueError("GFX103_CUSTOM_LENGTH_INVALID")
        else:
            length=(token>>24)&127
            if length<1:raise ValueError("GFX103_INSTRUCTION_LENGTH_ZERO")
        if i+length>len(words):raise ValueError("GFX103_INSTRUCTION_OVERRUN")
        if opcode in (98,100):
            target=ordinary if opcode==98 else siv
            target[MODES[(token>>11)&7]]+=1
        elif opcode==99:sgv+=1
        i+=length;steps+=1
        if steps>250000:raise ValueError("GFX103_TOO_MANY_INSTRUCTIONS")
    if i!=len(words):raise ValueError("GFX103_INCOMPLETE_SHDR")
    ordinary_np=sum(n for k,n in ordinary.items() if "noperspective" in k)
    siv_np=sum(n for k,n in siv.items() if "noperspective" in k)
    return {
       "ordinary_modes":dict(ordinary),"system_interpreted_modes":dict(siv),
       "system_generated_count":sgv,
       "ordinary_noperspective_declarations":ordinary_np,
       "system_interpreted_noperspective_declarations":siv_np,
       "original_android_interpolation_proven":False,
    }

def enforce_native_gles_qualifier(glsl,stage,source_fragment_classes=None):
    """Require NV extension for native qualifiers; never downgrade to smooth.

    ES300 is excluded by the owner's GFX101+102 real GPU compile evidence;
    310 and 320 succeeded in original-free GFX102. Does NOT establish
    end-to-end Shader48 semantics, hardware pixels or sampler parity.
    """
    if stage not in ("vertex","fragment") or not isinstance(glsl,str):
        raise ValueError("GFX103_STAGE_INVALID")
    m=VERSION.match(glsl)
    if not m:raise ValueError("GFX103_GLSL_VERSION_UNSUPPORTED")
    version=int(m.group(1));native=has_native_interpolation(glsl)
    ordinary=0;siv=0
    if stage=="fragment":
        if not isinstance(source_fragment_classes,dict):
            raise ValueError("GFX103_ORIGINAL_FRAGMENT_DECLARATIONS_REQUIRED")
        ordinary=source_fragment_classes.get("ordinary_noperspective_declarations")
        siv=source_fragment_classes.get("system_interpreted_noperspective_declarations")
        if type(ordinary)!=int or ordinary<0 or type(siv)!=int or siv<0:
            raise ValueError("GFX103_ORIGINAL_FRAGMENT_COUNTS_INVALID")
        if ordinary and not native:raise ValueError("GFX103_NATIVE_ORDINARY_INTERPOLATION_LOST")
    directives=list(DIRECTIVE.finditer(glsl))
    if len(directives)>1:raise ValueError("GFX103_DUPLICATE_EXTENSION")
    if directives and directives[0].group(1)!="require":
        raise ValueError("GFX103_EXTENSION_NOT_REQUIRED")
    if native and version<310:raise ValueError("GFX103_NATIVE_ES300_REJECTED_ON_ADRENO")
    if native and not directives:
        glsl=glsl[:m.end()]+"#extension "+NV+" : require\n"+glsl[m.end():]
    return glsl,{
       "stage":stage,"glsl_es_version":version,"native_qualifier_seen":native,
       "nv_extension_required":native,
       "ordinary_noperspective_count":ordinary,
       "siv_noperspective_count":siv,
       "siv_builtin_mapping_verified":False,
       "material_cb_binding_verified":False,
       "original_pixel_parity_verified":False,
       "original_shader_restored":False,"phase_closed":False,
    }

def source_pair_gate(fragment_shdr,vertex_glsl,fragment_glsl):
    source=dxbc_fragment_input_classes(fragment_shdr)
    vert,v=enforce_native_gles_qualifier(vertex_glsl,"vertex")
    frag,f=enforce_native_gles_qualifier(fragment_glsl,"fragment",source)
    if source["ordinary_noperspective_declarations"] and not v["native_qualifier_seen"]:
        raise ValueError("GFX103_VERTEX_NATIVE_VARYING_MISSING")
    return (vert,frag),{"source":source,"vertex":v,"fragment":f,
           "stage_linked_on_device":False,"original_shader_restored":False,
           "phase_closed":False}
