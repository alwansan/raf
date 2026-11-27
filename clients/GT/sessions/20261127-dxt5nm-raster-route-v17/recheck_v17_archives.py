#!/usr/bin/env python3
"""Offline V17 replay of actual V16/V17 authored archives, independent of CI verifier.
No original assets, Unity license, network, or metadata mutation.
"""
import argparse, hashlib, io, json, math, re, zipfile
from pathlib import Path
from PIL import Image

HEAD='1fb6a0be70ead8c48915c24b73b520c88a1423b9'
RUN=45979650728
PINS=((41374,'f98bc0633789aa43fba1f7a20c26554ba6df30bacfa2172d33ca6d3d964cc5d7',45),(72201,'f4f94ad3cc8223582bbc14b4438a6448ed9486998fa5893299697e6deeccc44a',47))
W,H=32,16
CLEAR=(-4.,)*4
DIMS=((5,7),(2,3),(1,1))
def need(q,msg):
    if not q:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def load_zip(path,pin):
    b=Path(path).read_bytes();need((len(b),sha(b))==pin[:2],'archive SHA/size')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        n=z.namelist();need(len(n)==len(set(n))==pin[2] and z.testzip() is None,'archive population/CRC')
        need(all('/' not in x and '\\' not in x for x in n),'archive name scope')
        return {k:z.read(k) for k in n}
def norm(b):
    for pat,repl in ((rb'(?m)^guid: [0-9a-f]{32}\r?$',b'guid: VOLATILE'),(rb'(?m)^timeCreated: [0-9]+\r?$',b'timeCreated: VOLATILE')):
        b,n=re.subn(pat,repl,b);need(n==1,'volatile header')
    return b
def delta(a,b):
    need(len(a)==len(b) and all(math.isfinite(x) for x in a),'float population')
    return max(abs(x-y) for x,y in zip(a,b,strict=True))
def px(a):
    need(len(a)==W*H*4,'pixel extent')
    return [tuple(a[i:i+4]) for i in range(0,len(a),4)]
def region(slot,i,orientation):
    # Analytic UV in this fixture's two axis-aligned right triangles, not
    # a copy of the CI verifier's barycentric inverse-matrix implementation.
    x,y=i%W,i//W
    if orientation=='top_first':y=H-1-y
    X=(x+.5)*4/W-2;Y=(y+.5)*2/H-1
    u=(X+2)/1.5 if slot==0 else (2-X)/2.5
    v=(Y+1)/2
    if min(u,v,1-u-v)<-1e-7:return 'outside',None
    if min(u,v,1-u-v)<=1e-7:return 'edge',None
    return 'inside',(u,v)
def st(uv,t):return uv[0]*t[0]+t[2],uv[1]*t[1]+t[3]
def pixel(raw,uv,mip):
    w,h=DIMS[mip];x,y=[(v%1)*d for v,d in zip(uv,(w,h),strict=True)]
    if min(abs(x-round(x)),abs(y-round(y)))<2e-5:return None
    j=(int(y)*w+int(x))*4
    return tuple(v/255 for v in raw[j:j+4])
def normal(p,marker):
    x=2*p[0]*p[3]-1;y=2*p[1]-1
    return x,y,math.sqrt(max(0,1-x*x-y*y)),marker
def ident(a,b):
    need(all(a[k]==b[k] for k in ('path','guid','file_id','sha256','meta_sha256')),'actual identity')
def inspect(a,b):
    def j(z,k):return json.loads(z[k])
    v16=j(a,'normalmap-exporter-reimport-raw.json');m16=j(a,'normalmap-exporter-reimport-manifest.json')
    old=j(a,'normalmap-exporter-reimport-verified.json');r=j(b,'normalmap-raster-raw.json');m=j(b,'normalmap-raster-manifest.json');base=j(b,'normalmap-exporter-reimport-manifest.json');v=j(b,'normalmap-raster-verified.json')
    need(old['status']=='PASS_ACTUAL_AUTHORED_V15_EXPORTER_DIRECT_UNITY_REIMPORT' and v16['route_manifest_sha256']==sha(a['normalmap-exporter-reimport-manifest.json']),'V16 actual')
    need(v['status']=='PASS_ACTUAL_AUTHORED_V16_CANDIDATE_RASTER_ROUTE' and r['status']=='OBSERVED_AUTHORED_DIRECT_RASTER_ROUTE' and not r['error'],'V17 actual')
    need(r['run_id']==m['run_id']==base['run_id']==f'{RUN}-1-{HEAD}' and r['raster_manifest_sha256']==sha(b['normalmap-raster-manifest.json']) and m['base_V16_stage_manifest_sha256']==sha(b['normalmap-exporter-reimport-manifest.json']),'manifest identity')
    build=j(b,'build.json');need(build['head']==HEAD and build['run_id']==str(RUN) and build['original_assets_read'] is False,'build identity')
    need(r['editor']=='2021.3.45f2' and r['backend']=='Vulkan' and r['active_color_space']=='Linear' and r['width']==W and r['height']==H and r['exact_candidate_metadata_unchanged'] is True and r['explicit_fragment_integer_repeat_load'] is True,'runtime boundary')
    for k in ('original_assets_read','production_activation','native_sampler_parity_verified','original_shader_program_parity_verified','scene_import_verified','source_lower_mip_parity_verified','Android_device','XAPK'):need(v[k] is False,'scope '+k)
    need(m['schema_version']==17 and m['manual_alpha_edit'] is False and m['textures']==base['textures'] and m['candidate_rows']==base['candidate_rows'],'candidate binding')
    adapters={x['path']:x for x in m['raster_adapters']};need(len(adapters)==2,'adapter scope')
    need(set(m['staged_files'])-set(base['staged_files'])=={'Assets/Editor/SyntheticNormalRasterRoute.cs'},'new file scope')
    for k,h in base['staged_files'].items():
        if k in adapters:need(h==adapters[k]['baseline_shader_sha256'] and m['staged_files'][k]==adapters[k]['diagnostic_shader_sha256'],'adapter hash')
        else:need(m['staged_files'][k]==h,'nonadapter hash')
    for fn,key in (('alpha-exporter-actual.json','exporter_receipt_sha256'),('alpha-policy-patch.json','exporter_patch_receipt_sha256')):need(sha(b[fn])==m[key]==base[key],'export receipt')
    need(a['alpha-policy-patch.json']==b['alpha-policy-patch.json'],'patch bytes')
    e16=j(a,'alpha-exporter-actual.json');e17=j(b,'alpha-exporter-actual.json')
    pairs=0
    for mode in ('normal','bc3','rgba'):
        need(e16['scopes'][mode]['provider_sha256']==e17['scopes'][mode]['provider_sha256'],'provider')
        for x,y in zip(e16['scopes'][mode]['rows'],e17['scopes'][mode]['rows'],strict=True):
            for side in ('before','after'):
                q,t=x[side],y[side];need(q['key']==t['key'] and q['ptr'][1:]==t['ptr'][1:] and q['alpha']==t['alpha'] and q['png_sha256']==t['png_sha256'] and q['rgba_hex']==t['rgba_hex'] and sha(bytes.fromhex(t['rgba_hex']))==q['rgba_sha256']==t['rgba_sha256'] and norm(q['metadata'].encode())==norm(t['metadata'].encode()),'actual export replay')
            pairs+=1
    need(pairs==6 and e17['actual_compiled_exporter_modes']==6 and e17['actual_normalmap_policy_changes']==2 and e17['actual_ordinary_policy_unchanged']==4 and e17['actual_metadata_control_count']==6,'export coverage')
    tex={};source_rows=[]
    for i,(t,c,h,raw) in enumerate(zip(m['textures'],m['candidate_rows'],old['rows'],v16['phases'][0]['textures'],strict=True)):
        png=b[f'candidate-{i}.png'];meta=b[f'candidate-{i}.png.meta'];orig=a[f'candidate-{i}.png.meta'];p=e17['scopes']['normal']['rows'][i]['after']
        need(png==a[f'candidate-{i}.png'] and sha(png)==t['sha256']==c['png_sha256']==h['png_sha256']==p['png_sha256'],'PNG identity')
        need(meta==p['metadata'].encode() and sha(meta)==t['meta_sha256']==c['meta_sha256'] and norm(meta)==norm(orig) and sha(norm(meta))==h['normalized_meta_sha256']==c['normalized_meta_sha256'],'meta bytes')
        need([t['guid'],t['file_id']]==p['ptr'][:2] and p['key']==c['source_key']==h['source_key'] and p['alpha']==0,'texture pointer')
        with Image.open(io.BytesIO(png)) as im:need(im.mode=='RGBA' and im.size==(5,7),'PNG format');rgba=im.tobytes()
        need(sha(rgba)==p['rgba_sha256']==h['rgba_sha256']==c['rgba_sha256'] and rgba.hex()==t['expected_rgba_hex'],'RGBA bytes')
        mips=[]
        for k,q in enumerate(raw['mips']):
            d=bytes.fromhex(q['rgba_hex']);need(sha(d)==h['actual_mip_sha256'][k] and q['rgba_hex']==h['actual_mip_RGBA_hex'][k] and (q['width'],q['height'])==DIMS[k],'V16 actual mip binding');mips.append(d)
        tex[t['guid']]=mips;source_rows.append(dict(source_key=c['source_key'],guid=t['guid'],file_id=t['file_id'],png_sha256=c['png_sha256'],meta_sha256=c['meta_sha256'],normalized_meta_sha256=c['normalized_meta_sha256'],V16_mip_sha256=[sha(d) for d in mips]))
    task=[]
    for route,ex,be in zip(r['routes'],m['routes'],base['routes'],strict=True):
        need(route['key']==ex['key']==be['key'] and route['vertex_count']==6 and route['base_vertices']==[0,3] and route['index_counts']==[3,3],'mesh population')
        ident(route['mesh'],ex['mesh']);ident(ex['mesh'],be['mesh'])
        need(route['positions']==[-2,-1,0,-.5,-1,0,-2,1,0,-.5,-1,0,2,-1,0,2,1,0] and route['uv0']==[0,0,1,0,0,1,1,0,0,0,0,1],'mesh geometry')
        for i,s in enumerate(route['slots']):
            need(s['slot']==i and s['indices']==([0,1,2] if i==0 else [3,5,4]) and s['alpha_transparency'] is False and s['mip_count']==3 and s['format']=='RGBA32' and s['graphics_format']=='R8G8B8A8_UNorm','slot state')
            for k in ('material','texture','shader'):ident(s[k],ex[k+'s'][i])
            for k in ('materials','textures'):ident(ex[k][i],be[k][i])
            sh=s['shader'];ad=adapters[sh['path']];need(sh['sha256']==ad['diagnostic_shader_sha256'] and sh['guid']==ad['guid']==be['shaders'][i]['guid'] and sh['file_id']==ad['file_id']==be['shaders'][i]['file_id'] and sh['meta_sha256']==ad['meta_sha256']==be['shaders'][i]['meta_sha256'],'adapter identity')
            need(s['uv_transform']==ex['uv'][i*4:i*4+4]==be['uv'][i*4:i*4+4],'UV state')
            task.append((route['key'],i,s,ad['marker']))
    need(len(task)==4,'slot count')
    def uv_check(orientation):
        for _,slot,s,_ in task:
            for i,a in enumerate(px(s['uv_pixels'])):
                kind,uv=region(slot,i,orientation)
                if kind=='outside':need(a==CLEAR,'UV outside')
                if kind=='inside':need(delta(a,(*uv,*st(uv,s['uv_transform'])))<=3e-5,'UV interpolation')
    orientations=[]
    for o in ('top_first','bottom_first'):
        try:uv_check(o)
        except ValueError:continue
        orientations.append(o)
    need(orientations==[v['geometry_anchored_RT_orientation']],'unique orientation');o=orientations[0]
    def draw(slot,t,raw,mip,vals,marker=None):
        out={};mx=0
        for i,a in enumerate(px(vals)):
            kind,uv=region(slot,i,o)
            if kind=='outside':need(a==CLEAR,'outside fragment')
            if kind!='inside':continue
            need(a!=CLEAR,'missing fragment');p=pixel(raw,st(uv,t),mip)
            if p is None:continue
            e=delta(a,p if marker is None else normal(p,marker));need(e<=(1e-6 if marker is None else .004),'fragment value');mx=max(mx,e);out[i]=a
        return out,mx
    counts=[];controls={};total=0;maxp=maxn=0
    for key,slot,s,marker in task:
        t=s['uv_transform'];raw=tex[s['texture']['guid']];rows=[]
        for n,mip in enumerate(s['mips']):
            need(mip['level']==n,'mip index');p,ep=draw(slot,t,raw[n],n,mip['packed']);q,en=draw(slot,t,raw[n],n,mip['normal'],marker);need(p.keys()==q.keys(),'pixel population');total+=len(p);maxp=max(maxp,ep);maxn=max(maxn,en);rows.append(len(p))
        inside=sum(region(slot,i,o)[0]=='inside' for i in range(W*H));outside=sum(region(slot,i,o)[0]=='outside' for i in range(W*H));counts.append(dict(route=key,slot=slot,texture_guid=s['texture']['guid'],shader_guid=s['shader']['guid'],geometry_inside=inside,geometry_outside=outside,checked_pixels=rows))
        if key=='level1' and slot==0:
            other=next(d for g,d in tex.items() if g!=s['texture']['guid']);p,_=draw(slot,t,raw[0],0,s['mips'][0]['packed']);q,_=draw(slot,t,other[0],0,s['wrong_texture']);shift=t[:];shift[2]+=.3125;u,_=draw(slot,shift,raw[0],0,s['wrong_uv']);controls={'wrong_texture_changed_pixels':sum(delta(p[i],q[i])>1e-6 for i in p.keys()&q.keys()),'wrong_UV_changed_pixels':sum(delta(p[i],u[i])>1e-6 for i in p.keys()&u.keys())};need(s['restored_packed']==s['mips'][0]['packed'],'exact restoration')
        else:need(not s['wrong_texture'] and not s['wrong_uv'] and not s['restored_packed'],'control scope')
    need(total==v['actual_packed_pixels']==v['actual_normal_pixels']==1288 and controls==v['actual_pixel_controls'] and min(controls.values())==94,'pixel totals')
    for c,vv in zip(counts,v['rows'],strict=True):
        need(all(c[k]==vv[k] for k in ('route','slot','texture_guid','shader_guid','geometry_inside','geometry_outside')) and c['checked_pixels']==[x['checked_pixels'] for x in vv['mips']],'verified row counts')
    logs={}
    for k,d in b.items():
        if k.startswith('test_') and k.endswith('.log'):
            s=d.decode();n=re.search(r'^Ran (\d+) tests? in ',s,re.M);need(n and re.search(r'^OK$',s,re.M),'regression '+k);logs[k]=int(n[1])
    report=j(b,'normalmap-importer-report.json');need(logs==report['tests'] and len(logs)==20 and sum(logs.values())==306 and report['counterfactual_count']==37 and len(v['actual_receipt_negative_controls'])==7,'regressions and controls')
    return dict(status=v['status'],run=RUN,head=HEAD,actual_source_regressions=sum(logs.values()),actual_historical_V11_V12_controls=37,actual_V15_controls=6,actual_V17_receipt_falsifiers=v['actual_receipt_negative_controls'],actual_pixel_controls=controls,actual_packed_pixels=total,actual_normal_pixels=total,actual_Unity_raster_verified=True,renderer_routes=2,submesh_draw_routes=4,geometry_anchored_RT_orientation=o,independent_max_packed_error=maxp,independent_max_normal_error=maxn,actual_RT_restored=True,exact_candidate_metadata_unchanged=True,independent_export_pairs=6,source_rows=source_rows,rows=counts,member_sha256={k:sha(d) for k,d in sorted(b.items())},original_assets_read=False,production_activation=False,native_sampler_parity_verified=False,original_shader_program_parity_verified=False,scene_import_verified=False,source_lower_mip_parity_verified=False,Android_device=False,XAPK=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('v16');p.add_argument('v17');p.add_argument('--out',type=Path);args=p.parse_args();r=inspect(load_zip(args.v16,PINS[0]),load_zip(args.v17,PINS[1]));r['archive']={'id':15188827195,'bytes':PINS[1][0],'sha256':PINS[1][1],'members':47,'crc_verified':True};r['historical_archive']={'id':15187423558,'bytes':PINS[0][0],'sha256':PINS[0][1],'members':45,'crc_verified':True};r['job']=140439999714;r['guard']={'id':45979650667,'conclusion':'success'}
    if args.out:
        need(not args.out.exists(),'fresh output');args.out.write_text(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('member_sha256','source_rows','rows')},sort_keys=True))
