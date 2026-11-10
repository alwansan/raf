"""Strict owner GFX094 device compile/link ZIP audit; anonymous aggregates only."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
BUILD='66b2968673f410cbf58d5b255216c5e3c9c175ef'
SOURCE='15964ea8f246b6e076ce26b60931ee2e1a9a2385'

def audit_records(summary,rows):
    if not isinstance(summary,dict) or not isinstance(rows,list) or len(rows)>2000:raise ValueError('GFX097_INPUT')
    if summary.get('experiment')!='GFX-MULTI-094' or summary.get('source_sha')!=SOURCE or summary.get('build_source_sha')!=BUILD:raise ValueError('GFX097_IDENTITY')
    if not summary.get('all_pairs_tested') or summary.get('completed_pairs')!=157 or summary.get('expected_pairs')!=157:raise ValueError('GFX097_INCOMPLETE')
    if any(summary.get(k) is not False for k in ('originalShaderRestored','phase_closed','model_rendered','PC_pixel_parity')):raise ValueError('GFX097_FALSE_PHASE_CLAIM')
    compiled={};linked={};unavailable={};env=0;errors=0;driver_logs=0
    allowed={'environment','compile','link','CPU_translation_unavailable'}
    for row in rows:
        if not isinstance(row,dict) or row.get('event') not in allowed:raise ValueError('GFX097_UNEXPECTED_EVENT')
        kind=row['event'];errors+=int(bool(row.get('gl_error')));driver_logs+=int(bool(row.get('driver_log')))
        if kind=='environment':env+=1;continue
        pair=row.get('pair')
        if not isinstance(pair,str) or pair not in {'P%03d'%i for i in range(157)}:raise ValueError('GFX097_PAIR_ID')
        if kind=='compile':
            stage=row.get('stage');key=(pair,stage)
            if stage not in ('vert','frag') or key in compiled or type(row.get('success')) is not bool:raise ValueError('GFX097_COMPILE_DUPLICATE_OR_SHAPE')
            compiled[key]=row['success']
        elif kind=='CPU_translation_unavailable':
            reason=row.get('reason')
            if pair in unavailable or reason!={'vertex':'BaseInstance_ES_unsupported'}:raise ValueError('GFX097_CPU_UNAVAILABLE_SHAPE')
            unavailable[pair]=True
        else:
            if pair in linked or type(row.get('success')) is not bool:raise ValueError('GFX097_LINK_DUPLICATE')
            if row.get('skipped_compile_failure'):
                if pair not in unavailable and all(compiled.get((pair,s)) for s in ('vert','frag')):raise ValueError('GFX097_SKIP_CONTRADICTION')
            elif not all(compiled.get((pair,s)) for s in ('vert','frag')):raise ValueError('GFX097_LINK_WITHOUT_COMPILED_STAGES')
            linked[pair]=row['success']
    if env!=1 or len(linked)!=157 or len(compiled)!=285 or len(unavailable)!=29:raise ValueError('GFX097_EVENT_COUNT')
    if any((pair,'vert') in compiled for pair in unavailable):raise ValueError('GFX097_UNAVAILABLE_COMPILE_CONTRADICTION')
    counts=Counter(stage for pair,stage in compiled)
    if counts!={'vert':128,'frag':157}:raise ValueError('GFX097_STAGE_COUNT')
    success=sum(compiled.values());links=sum(linked.values());device_failures=sum(not v for v in compiled.values())+sum(not v for p,v in linked.items() if p not in unavailable)
    if summary.get('compiled_stages')!=success or summary.get('linked_pairs')!=links or summary.get('failed_pairs')!=157-links:raise ValueError('GFX097_SUMMARY_CONTRADICTION')
    return {'experiment':'GFX-MULTI-097','source_sha':SOURCE,'tested_build_sha':BUILD,'all_expected_pairs_accounted':True,'actual_compiled_stages':success,'actual_linked_pairs':links,'CPU_BaseInstance_unavailable_pairs':len(unavailable),'actual_device_compile_or_link_failures':device_failures,'nonzero_GL_error_events':errors,'nonempty_driver_log_events':driver_logs,'event_count':len(rows),'Android_SDK':summary.get('android_sdk'),'owner_device_Adreno730':summary.get('renderer')=='Adreno (TM) 730','source_original_stage_programs_on_device':True,'original_Material_payload_or_model_pixels_proven':False,'originalShaderRestored':False,'phase_closed':False}

def audit_zip(path):
    path=Path(path)
    with ZipFile(path) as z:
        if set(z.namelist())!={'summary.json','events.jsonl','LIMITS.txt'} or z.testzip() is not None or sum(i.file_size for i in z.infolist())>5*1024*1024:raise ValueError('GFX097_ZIP')
        summary=json.loads(z.read('summary.json'));rows=[json.loads(s) for s in z.read('events.jsonl').splitlines() if s]
    result=audit_records(summary,rows);result['owner_zip_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();return result

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('zip',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=audit_zip(a.zip);a.out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
