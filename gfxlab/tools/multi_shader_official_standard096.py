"""Compare authenticated original metadata to Unity's exact-version source.

This is source schema evidence only, NOT original bytecode or pixel equality.
Public official shader code is downloaded from Unity with a pinned ZIP hash.
"""
import re,struct,hashlib
from collections import Counter
OFFICIAL_URL='https://download.unity3d.com/download_unity/88f88f591b2e/builtin_shaders-2021.3.45f2.zip'
OFFICIAL_ZIP_SHA256='5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5'
TYPES={'Color':0,'Vector':1,'Float':2,'Range':3,'2D':4}

def official_properties(text):
    # Match one authored declaration per line, not arbitrary shader identifiers.
    section=text.split('Properties',1)[1].split('CGINCLUDE',1)[0]
    result={}
    pattern=r'^\s*(?:\[[^\]\r\n]+\]\s*)*([A-Za-z_]\w*)\s*\(\s*"[^"\r\n]*"\s*,\s*(Color|Vector|Float|Range|2D)(?:\s*\([^)]*\))?\s*\)\s*=\s*(.+)$'
    for line in section.splitlines():
        m=re.match(pattern,line)
        if not m:continue
        name,kind,raw=m.groups()
        if name in result:raise ValueError('GFX096_DUPLICATE_OFFICIAL_PROPERTY')
        if kind=='2D':
            match=re.match(r'"([^"]+)"\s*\{\s*\}',raw)
            if not match:raise ValueError('GFX096_TEXTURE_DEFAULT')
            value=match[1]
        else:
            values=raw.strip().strip('()').split(',')
            value=[float(v.strip()) for v in values]
            if kind in ('Float','Range') and len(value)!=1:raise ValueError('GFX096_SCALAR_DEFAULT')
            if kind in ('Color','Vector'):
                if len(value)==3:value.append(1.0)
                if len(value)!=4:raise ValueError('GFX096_VECTOR_DEFAULT')
        result[name]=(TYPES[kind],value)
    if not result:raise ValueError('GFX096_NO_OFFICIAL_PROPERTIES')
    return result

def compare_original_private(tree,official):
    expected=official_properties(official);parsed=tree['m_ParsedForm']
    props=parsed['m_PropInfo']['m_Props'];original={p['m_Name']:p for p in props}
    if len(original)!=len(props):raise ValueError('GFX096_DUPLICATE_ORIGINAL_PROPERTY')
    c=Counter()
    for name,(typ,value) in expected.items():
        p=original.get(name)
        if p is None:c['missing_original_property']+=1;continue
        c['name_match']+=1
        if p['m_Type']==typ:c['type_match']+=1
        else:c['type_mismatch']+=1
        if typ==4:equal=p['m_DefTexture']['m_DefaultName']==value
        else:
            actual=[p['m_DefValue[%d]'%i] for i in range(len(value))]
            equal=struct.pack('<%df'%len(value),*actual)==struct.pack('<%df'%len(value),*value)
        c['default_value_float32_or_texture_name_equal' if equal else 'default_value_different']+=1
    c['original_extra_properties']=len(set(original)-set(expected))
    runtime_names=[p['m_State']['m_Name'] for sub in parsed['m_SubShaders'] for p in sub['m_Passes']]
    source_names=re.findall(r'\bName\s+"([^"]+)"',official)
    runtime_source=[name for name in source_names if name!='META']
    return dict(experiment='GFX-MULTI-096',official_Unity_version='2021.3.45f2',official_zip_SHA256=OFFICIAL_ZIP_SHA256,
        source_shader_name_equals_public_builtin_Standard=parsed['m_Name']=='Standard',
        source_editor_equals_public_StandardShaderGUI=parsed.get('m_CustomEditorName')=='StandardShaderGUI',
        source_fallback_equals_public_VertexLit=parsed.get('m_FallbackName')=='VertexLit',
        official_property_count=len(expected),source_property_count=len(original),safe_counts=dict(c),
        runtime_pass_names_match_official_after_explicit_editor_META_exclusion=runtime_names==runtime_source,
        omitted_official_editor_META_passes=source_names.count('META'),
        original_DXBC_matches_recompiled_official_source=False,
        source_schema_match_alone_proves_original_GPU_code=False,originalShaderRestored=False,phase_closed=False)

def main():
    import argparse,json,urllib.request,zipfile,io
    from pathlib import Path
    from gfxlab.tools.original_model_probe import stage_originals
    from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
    p=argparse.ArgumentParser();p.add_argument('--zip2',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    with urllib.request.urlopen(OFFICIAL_URL,timeout=60) as response:raw=response.read(2*1024*1024)
    if hashlib.sha256(raw).hexdigest()!=OFFICIAL_ZIP_SHA256:raise ValueError('GFX096_OFFICIAL_ZIP_SHA_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=[n for n in z.namelist() if n.endswith('/Standard.shader') or n=='Standard.shader']
        if len(names)!=1:raise ValueError('GFX096_OFFICIAL_STANDARD_PATH')
        text=z.read(names[0]).decode('utf-8-sig')
    tree,_,_=load_original_shader_private(stage_originals(a.zip2,a.stage))
    d=compare_original_private(tree,text);a.out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
