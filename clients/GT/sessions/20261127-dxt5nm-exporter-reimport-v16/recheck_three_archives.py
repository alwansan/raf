#!/usr/bin/env python3
"""Recheck V16 PASS from exact V14, V15, V16 authored Actions archives.
Requires Pillow. No Unity, original assets, or metadata changes.
"""
import argparse, hashlib, io, json, re, zipfile
from pathlib import Path
from PIL import Image


def sha(b): return hashlib.sha256(b).hexdigest()
def need(ok, why):
    if not ok: raise ValueError(why)
def archive(path, proof):
    b=Path(path).read_bytes();need(len(b)==proof['bytes'] and sha(b)==proof['sha256'],'archive_identity')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names=z.namelist();need(len(names)==len(set(names))==proof['member_count'] and z.testzip() is None,'archive_crc')
        files={n:z.read(n) for n in names}
    if 'member_sha256' in proof:need({n:sha(b) for n,b in files.items()}==proof['member_sha256'],'member_sha256')
    return files
def norm(raw):
    for pat,val in ((rb'(?m)^guid: [0-9a-f]{32}\r?$',b'guid: VOLATILE'),(rb'(?m)^timeCreated: [0-9]+\r?$',b'timeCreated: VOLATILE')):
        raw,n=re.subn(pat,val,raw);need(n==1,'volatile_header')
    return raw
def verify(receipt,v14,v15,v16):
    p=json.loads(Path(receipt).read_bytes());a,b,c=[archive(path,proof) for path,proof in zip((v14,v15,v16),(*p['historical_archives'],p['archive']),strict=True)]
    def j(z,n):return json.loads(z[n])
    r14=j(a,'normalmap-texel-policy-raw.json');r16=j(c,'normalmap-exporter-reimport-raw.json');m16=j(c,'normalmap-exporter-reimport-manifest.json');v=j(c,'normalmap-exporter-reimport-verified.json')
    need(r14['run_id']=='45972362899-1-db5952b6fae2d6878214c2d9bf748bc63dd14ff8' and r14['v13_manifest_sha256']==sha(a['normalmap-unity-manifest.json']) and r14['policy_manifest_sha256']==sha(a['normalmap-texel-policy-manifest.json']),'V14_binding')
    need(r16['run_id']==m16['run_id']==f"{p['run']}-1-{p['head']}" and r16['route_manifest_sha256']==sha(c['normalmap-exporter-reimport-manifest.json']),'V16_binding')
    need(m16['exporter_receipt_sha256']==sha(c['alpha-exporter-actual.json']) and m16['exporter_patch_receipt_sha256']==sha(c['alpha-policy-patch.json']) and c['alpha-policy-patch.json']==b['alpha-policy-patch.json'],'export_receipt')
    need(r16['exact_exporter_meta_unchanged'] is True and m16['manual_alpha_edit'] is False and m16['historical_V12_opt_out_verified'] is True and m16['source_V12_verified'] is False,'export_policy')
    need(v['status']==p['status']=='PASS_ACTUAL_AUTHORED_V15_EXPORTER_DIRECT_UNITY_REIMPORT' and v['actual_Unity_reimport_verified'] is True,'verified_PASS')
    for k in ('source_lower_mip_parity_verified','original_assets_read','production_activation','original_shader_program_parity_verified','scene_import_verified','Android_device','XAPK','manual_alpha_edit'):need(v[k] is False and p[k] is False,'scope:'+k)
    for raw in (r14,r16):need(raw['editor']=='2021.3.45f2' and raw['backend']=='Vulkan' and raw['active_color_space']=='Linear' and raw['unfiltered_compute_load'] is True and not raw['error'],'Unity_scope')
    e15=j(b,'alpha-exporter-actual.json');e16=j(c,'alpha-exporter-actual.json');pairs=0
    for mode in ('normal','bc3','rgba'):
        need(e15['scopes'][mode]['provider_sha256']==e16['scopes'][mode]['provider_sha256'],'provider')
        for old,new in zip(e15['scopes'][mode]['rows'],e16['scopes'][mode]['rows'],strict=True):
            for side in ('before','after'):
                x,y=old[side],new[side]
                need(x['key']==y['key'] and x['ptr'][1:]==y['ptr'][1:] and x['png_sha256']==y['png_sha256'] and x['rgba_hex']==y['rgba_hex'] and sha(bytes.fromhex(x['rgba_hex']))==x['rgba_sha256']==y['rgba_sha256'] and norm(x['metadata'].encode())==norm(y['metadata'].encode()),'historical_export_bytes')
            x,y=(norm(new[k]['metadata'].encode()) for k in ('before','after'))
            if mode=='normal':
                expect,n=re.subn(rb'(?m)^  alphaIsTransparency: 1$',b'  alphaIsTransparency: 0',x);need(n==1 and expect==y and new['before']['alpha']==1 and new['after']['alpha']==0,'normal_delta')
            else:need(x==y and new['before']['alpha']==new['after']['alpha']==1,'ordinary_policy')
            pairs+=1
    need(pairs==6,'export_pair_count')
    q14=next(q for q in r14['phases'] if q['name']=='alpha_off');q16=r16['phases'][0];need(q16['name']=='exporter_candidate','phase')
    def identity(o,e):need(all(o[k]==e[k] for k in ('path','guid','file_id','sha256','meta_sha256')),'asset_identity')
    slots=0
    for x,y,z in zip(q14['routes'],q16['routes'],m16['routes'],strict=True):
        for k in ('key','vertex_count','index_counts','base_vertices','uv'):need(x[k]==y[k]==z[k],'route_layout')
        identity(y['mesh'],z['mesh']);need(x['mesh']['sha256']==y['mesh']['sha256'],'mesh_bytes')
        for k in ('textures','materials','shaders'):
            for i,o,e in zip(x[k],y[k],z[k],strict=True):
                identity(o,e);need(i['file_id']==o['file_id'],'historical_fileID')
                if k!='materials':need(i['sha256']==o['sha256'],'historical_asset_bytes')
        slots+=len(y['textures'])
    texels=top_count=mips=0;err=0
    for i,(x,y,e,row) in enumerate(zip(q14['textures'],q16['textures'],m16['textures'],p['rows'],strict=True)):
        identity(y['identity'],e);png=c[f'candidate-{i}.png'];meta=c[f'candidate-{i}.png.meta'];pair=e16['scopes']['normal']['rows'][i]['after']
        need(sha(png)==e['sha256']==row['png_sha256']==pair['png_sha256'] and sha(meta)==e['meta_sha256']==row['meta_sha256'] and meta==pair['metadata'].encode() and pair['ptr'][:2]==[e['guid'],e['file_id']] and pair['key']==row['source_key'],'direct_candidate_bytes')
        need(png==a[f'normalmap-authored-{i}.png']==b[f'normalmap-authored-{i}.png'],'historical_PNG')
        with Image.open(io.BytesIO(png)) as im:need(im.mode=='RGBA' and im.size==(5,7),'PNG_shape');rgba=im.tobytes()
        need(sha(rgba)==row['rgba_sha256']==pair['rgba_sha256'] and rgba.hex()==e['expected_rgba_hex'],'PNG_RGBA')
        need({k:v for k,v in x.items() if k not in ('identity','mips')}=={k:v for k,v in y.items() if k not in ('identity','mips')} and y['alpha_transparency'] is False,'importer_runtime_state')
        for n,(u,w,hx,hs) in enumerate(zip(x['mips'],y['mips'],row['actual_mip_RGBA_hex'],row['actual_mip_sha256'],strict=True)):
            need((u['level'],u['width'],u['height'])==(w['level'],w['width'],w['height'])==(n,*row['observed_mip_dimensions'][n]),'mip_dimensions')
            need(u['rgba_hex']==w['rgba_hex']==hx and sha(bytes.fromhex(hx))==hs,'mip_bytes_and_hash');texels+=len(bytes.fromhex(hx))//4;mips+=1;err=max(err,w['max_unorm_error'])
        top=bytes.fromhex(y['mips'][0]['rgba_hex']);packed=bytes(q for r,g,b,a in zip(*[iter(rgba)]*4) for q in (255,g,g,r))
        need(b''.join(top[j*20:(j+1)*20] for j in range(6,-1,-1))==packed,'top_repack');top_count+=35
        if y['readable']:need(bytes.fromhex(y['cpu_top_rgba_hex'])==top,'CPU_orientation')
        else:need(y['cpu_top_rgba_hex']=='' and y['cpu_status']=='not_readable_as_imported','nonreadable')
    report=j(c,'normalmap-importer-report.json');tests={}
    for n,data in c.items():
        if n.startswith('test_') and n.endswith('.log'):
            s=data.decode();match=re.search(r'^Ran (\d+) tests? in ',s,re.M);need(match and re.search(r'^OK$',s,re.M),'regression');tests[n]=int(match[1])
    need(tests==report['tests'] and len(tests)==19 and sum(tests.values())==296 and report['counterfactual_count']==37 and v['actual_receipt_negative_control_count']==10,'regressions_controls')
    need((texels,mips,top_count,slots)==(84,6,70,4) and err==p['maximum_unorm_error'],'coverage')
    print(json.dumps(dict(status=p['status'],texels=texels,mips=mips,top_pixels=top_count,route_slots=slots,regressions=sum(tests.values()),archive_members=len(c)),sort_keys=True))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('receipt');p.add_argument('v14');p.add_argument('v15');p.add_argument('v16');a=p.parse_args();verify(a.receipt,a.v14,a.v15,a.v16)
