"""Independent CPU Vulkan native-DXBC vs HLSL bank comparison.
Use exact derived integer lookup table from prior actual source proof, identical
authored 512-square inputs, exact 512x8 lookup extent, both passes and repeats.
Raw programs/images/driver logs never leave the temporary directory.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import tempfile
from scripts import gt_stage_indexed_fft_candidate as indexed
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.probe_original_compute_containers import scan_blob
from tools.gt_fft_source_format_pair import audit as previous
from tools.gt_fft_indexed_pair import audit as old
SIZE=512
STAGES=8
COUNT=SIZE*SIZE
IMAGE_BYTES=COUNT*16
TABLE_BYTES=SIZE*STAGES*16
TABLE_SHA="eff308e614be3187d49c57f27d2bcd9b55945f8cfea69ec28aa3a78c693faed1"
STATUS="OBSERVED_NATIVE_FFT_BANK_ORACLE"
def need(ok,reason):old.need(ok,reason)
def sha(p):return old.sha(p)
def dump(p,o):old.dump(p,o)
def replace(s,a,b):
    need(s.count(a)==1,"host_anchor")
    return s.replace(a,b)
def render_host(s):
    # Keep existing independently exercised descriptors, two-dispatch barrier
    # and CPU device selection. Alter only exact input extents/upload/readback.
    s=replace(s,"dispatchGroupY>=1 && dispatchGroupY<=2","dispatchGroupY==512")
    s=replace(s,'uint32_t w=uint32_t(widthInt),h=uint32_t(heightInt);',r'''uint32_t w=uint32_t(widthInt),h=uint32_t(heightInt);
    require(w==512 && h==512 && imageFormat.token=="rgba32f" && !canary,"Exact bounded diagnostic extent");
    std::array<std::vector<uint8_t>,2> rawInputs;
    for(int i=0;i<2;i++){
        const char* name=i?"butterfly.rgba32f":"source.rgba32f";
        std::ifstream f(name,std::ios::binary|std::ios::ate);
        const size_t n=size_t(w)*(i?8:h)*16;
        require(bool(f) && f.tellg()==std::streamoff(n),"Exact private input size");
        rawInputs[i].resize(n);f.seekg(0);
        f.read(reinterpret_cast<char*>(rawInputs[i].data()),n);
        require(bool(f),"Private input read");
    }''')
    s=replace(s,"ci.extent={w,h,1};","uint32_t texH=t==1?8:h;\n        ci.extent={w,texH,1};")
    s=replace(s,"tex.sub.offset+(h-1)*tex.sub.rowPitch+w*imageFormat.stride()<=required.size","tex.sub.offset+(texH-1)*tex.sub.rowPitch+w*imageFormat.stride()<=required.size")
    s=replace(s,r'''        for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++) {
            std::array<float,4> p{};
            for(int c=0;c<4;c++)p[c]=(t<2)?inputValue(x,y,t,c):sentinel;
            putPixel(tex,x,y,imageFormat,p);
        }''',r'''        if(t<2){
            for(uint32_t y=0;y<texH;y++){
                auto* dst=tex.address+tex.sub.offset+y*tex.sub.rowPitch;
                auto* src=rawInputs[t].data()+size_t(y)*w*16;
                std::memcpy(dst,src,size_t(w)*16);
                require(std::memcmp(dst,src,size_t(w)*16)==0,"Exact upload bytes");
            }
        }else for(uint32_t y=0;y<texH;y++)for(uint32_t x=0;x<w;x++){
            putPixel(tex,x,y,imageFormat,{sentinel,sentinel,sentinel,sentinel});
            require(!isWritten(pixel(tex,x,y,imageFormat),imageFormat),"Output sentinel");
        }''')
    s=replace(s,"std::array<VkImageMemoryBarrier,2> postBarriers{};\n    for(int i=0;i<2;i++){","std::array<VkImageMemoryBarrier,4> postBarriers{};\n    for(int i=0;i<4;i++){")
    s=replace(s,"postBarriers[i].image=images[i?5:3].image;","postBarriers[i].image=images[2+i].image;")
    s=replace(s,"0,0,nullptr,0,nullptr,2,postBarriers.data());","0,0,nullptr,0,nullptr,4,postBarriers.data());")
    s=replace(s,'    check(vkQueueWaitIdle(queue),"vkQueueWaitIdle");',r'''    check(vkQueueWaitIdle(queue),"vkQueueWaitIdle");
    static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559);
    const std::array<const char*,4> names={"native0.rgba32f","native1.rgba32f","round0.rgba32f","round1.rgba32f"};
    for(int i=0;i<4;i++){
        std::ofstream out(names[i],std::ios::binary|std::ios::trunc);
        require(bool(out),"Output file open");
        const auto& tex=images[2+i];
        for(uint32_t y=0;y<h;y++){
            const auto* ptr=tex.address+tex.sub.offset+y*tex.sub.rowPitch;
            out.write(reinterpret_cast<const char*>(ptr),size_t(w)*16);
        }
        out.close();require(bool(out),"Output file write");
    }
    std::cout<<"GT_FFT_NATIVE_HOST exact_mapped_inputs=true intermediate_barrier=true four_raw_outputs=true\n";''')
    return s
def build_host(root):
    source=root/"host.cpp";runner=root/"host"
    source.write_text(render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text()))
    private_command(["g++","-std=c++17","-O2",str(source),"-lvulkan","-o",str(runner)],timeout=90)
    return runner
def input_bytes(mode):
    need(mode in ("signed","zero"),"input_mode")
    if mode=="zero":return bytes(IMAGE_BYTES)
    out=bytearray()
    for y in range(SIZE):
        for x in range(SIZE):
            n=(x*17+y*29+19*19+7)%1021
            out.extend(struct.pack("<4f",(n-510)/1024,(n%113-56)/256,(n%59-29)/128,1))
    return bytes(out)
def cls(bits):
    if bits&0x7f800000!=0x7f800000:return 0
    if bits&0x007fffff:return 1
    return 3 if bits&0x80000000 else 2
def profile(raw):
    need(len(raw)==IMAGE_BYTES,"readback_extent")
    counts=[0]*16;written=0
    for pixel in struct.iter_unpack("<4I",raw):
        written+=int(any(x!=0x46000000 for x in pixel))
        for lane,bits in enumerate(pixel):counts[lane*4+cls(bits)]+=1
    return dict(class_counts=counts,written_pixels=written)
def compare(a,b):
    need(len(a)==len(b)==IMAGE_BYTES,"paired_extent")
    c=CounterZero()
    for (x,),(y,) in zip(struct.iter_unpack("<I",a),struct.iter_unpack("<I",b),strict=True):
        k,l=cls(x),cls(y)
        c["raw_bit_different"]+=int(x!=y)
        c["class_mismatch"]+=int(k!=l)
        if k==l==0 and x!=y:
            u=struct.unpack("<f",struct.pack("<I",x))[0];v=struct.unpack("<f",struct.pack("<I",y))[0]
            c["finite_different"]+=int(u!=v)
            c["finite_over_tolerance"]+=int(abs(u-v)>max(1e-5,1e-5*max(abs(u),abs(v))))
    return c
def CounterZero():return dict(raw_bit_different=0,class_mismatch=0,finite_different=0,finite_over_tolerance=0)
def capture(runner,modules,directory,source,table):
    need(len(source)==IMAGE_BYTES and len(table)==TABLE_BYTES,"input_extent")
    directory.mkdir(mode=0o700)
    (directory/"source.rgba32f").write_bytes(source);(directory/"butterfly.rgba32f").write_bytes(table)
    try:
        with (directory/"driver.log").open("wb") as log:
            proc=subprocess.run([str(runner),*[str(x) for x in modules],"512","512","19","512","rgba32f"],
                                cwd=directory,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        rc=proc.returncode
    except subprocess.TimeoutExpired:return dict(status="timeout"),None
    if rc!=0:return dict(status="native_process_failure",exit_code=rc),None
    text=(directory/"driver.log").read_text(errors="replace")
    need(text.count("GT_FFT_NATIVE_HOST exact_mapped_inputs=true intermediate_barrier=true four_raw_outputs=true")==1,"host_capture_marker")
    need((directory/"source.rgba32f").read_bytes()==source and (directory/"butterfly.rgba32f").read_bytes()==table,"input_changed")
    raw=[]
    for name in ("native0","native1","round0","round1"):
        p=directory/(name+".rgba32f");need(p.is_file() and not p.is_symlink() and p.stat().st_size==IMAGE_BYTES,"output_extent")
        raw.append(p.read_bytes())
    result=dict(status="observed",exit_code=0,source_sha256=hashlib.sha256(source).hexdigest(),table_sha256=hashlib.sha256(table).hexdigest(),
                exact_upload=True,intermediate_barrier=True,profiles=[profile(x) for x in raw],
                native_roundtrip=[compare(raw[0],raw[2]),compare(raw[1],raw[3])])
    return result,raw
GLSL=r'''#version 450
#extension GL_EXT_samplerless_texture_functions : require
layout(local_size_x=512,local_size_y=1,local_size_z=1) in;
layout(set=0,binding=0) uniform texture2D src0;
layout(set=0,binding=1) uniform texture2D src1;
layout(set=0,binding=2,rgba32f) uniform writeonly image2D outputImage;
void main() {
 ivec2 xy=ivec2(gl_GlobalInvocationID.xy);
 imageStore(outputImage,xy,texelFetch(src0,xy,0) + texelFetch(src1,ivec2(xy.x,xy.y%8),0));
}
'''
def canary(root,runner):
    modules=[]
    for name,code in (("add",GLSL),("subtract",GLSL.replace(" + texelFetch"," - texelFetch"))):
        p=root/(name+".comp");q=root/(name+".spv");p.write_text(code)
        private_command(["glslangValidator","-V","-S","comp","-o",str(q),str(p)])
        private_command(["spirv-val","--target-env","vulkan1.1",str(q)]);modules.append(q)
    add,sub=modules;source=input_bytes("zero")
    table=struct.pack("<4f",.25,.5,.75,1)*(SIZE*STAGES)
    result,raw=capture(runner,[add,add,add,sub],root/"canary",source,table)
    need(raw is not None and result["native_roundtrip"][0]==CounterZero(),"canary_first_pass")
    need(raw[0]==raw[2]==struct.pack("<4f",.25,.5,.75,1)*COUNT and
         raw[1]==struct.pack("<4f",.5,1,1.5,2)*COUNT and raw[3]==source,"canary_exact_values")
    need(result["native_roundtrip"][1]["finite_over_tolerance"]==COUNT*4,"canary_wrong_second_rejected")
    return dict(status="PASS",exact_first_pass_pixels=COUNT,exact_native_second_pixels=COUNT,wrong_second_detected_lanes=COUNT*4)
def analyze(src,managed,root,runner,run_id):
    import UnityPy
    project=root/"unused_editor";private=root/"private"
    staged=previous.stage(src,managed,project,private,run_id)
    table=(private/"table-float.f32").read_bytes();need(hashlib.sha256(table).hexdigest()==TABLE_SHA,"historical_table_digest")
    cfg=json.loads((private/"config.json").read_text());env=UnityPy.load(str(src/indexed.OWNER))
    obj=env.file.objects[indexed.PATH_ID];need(obj.type.name=="ComputeShader","typed_source")
    raw=obj.get_raw_data();need(hashlib.sha256(raw).hexdigest()==old.OBJECT_SHA,"source_object_digest")
    containers=scan_blob(raw)["valid_dxbc_containers"];need(len(containers)==20,"source_program_count")
    modules={}
    for row in cfg["rows"]:
        i=row["slot"];rec=containers[i];blob=raw[rec["offset_in_original_object"]:rec["offset_in_original_object"]+rec["bytes"]]
        need(hashlib.sha256(blob).hexdigest()==row["dxbc_sha256"]==rec["binary_sha256"],"source_program_digest")
        dx=root/f"slot{i}.dxbc";native=root/f"native{i}.spv";converted=root/f"round{i}.spv";dx.write_bytes(blob)
        private_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(native),str(dx)])
        private_command(["glslangValidator","-V","-D","-S","comp","-e","main","-o",str(converted),str(private/row["file"])])
        for module in (native,converted):private_command(["spirv-val","--target-env","vulkan1.1",str(module)])
        modules[i]=(native,converted)
    rows=[]
    for slot in (6,16):
        pair=[*modules[slot],*modules[slot+1]]
        for mode in ("signed","zero"):
            source=input_bytes(mode);captures=[];raws=[]
            for repeat in (0,1):
                record,data=capture(runner,pair,root/f"pair{slot}-{mode}-{repeat}",source,table)
                captures.append(record);raws.append(data)
            delta=None if any(x is None for x in raws) else [compare(x,y) for x,y in zip(*raws,strict=True)]
            rows.append(dict(first_slot=slot,input_mode=mode,captures=captures,repeat_comparisons=delta))
    return dict(status=STATUS,source_object_sha256=old.OBJECT_SHA,source_table_sha256=TABLE_SHA,
                source_table_texels=SIZE*STAGES,source_extent=[SIZE,SIZE],table_extent=[SIZE,STAGES],
                native_and_roundtrip_validated_slots=4,attempted_captures=8,
                observed_captures=sum(c["status"]=="observed" for row in rows for c in row["captures"]),
                rows=rows,original_runtime_kernel_mapping_proven=False,original_fft_numeric_parity_verified=False,
                water_rendering_verified=False,android_device=False,production=False,XAPK=False)
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path);p.add_argument("--managed",type=Path)
    p.add_argument("--run-id");p.add_argument("--out",required=True,type=Path);p.add_argument("--canary-only",action="store_true")
    a=p.parse_args();result=dict(status="INCONCLUSIVE",water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        with tempfile.TemporaryDirectory(prefix="gt-native-fft-oracle-") as folder:
            root=Path(folder);runner=build_host(root);control=canary(root,runner)
            if a.canary_only:result=control
            else:
                need(a.source is not None and a.managed is not None and a.run_id is not None,"original_args")
                result=analyze(a.source,a.managed,root,runner,a.run_id);result["canary"]=control
    except Exception as exc:
        result["failure_type"]=type(exc).__name__
        if isinstance(exc,ValueError) and re.fullmatch(r"[a-z_]+",str(exc)):result["failure_reason"]=str(exc)
    dump(a.out,result);print("GT_FFT_NATIVE_BANK_ORACLE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="PASS" or result["status"]==STATUS and result["observed_captures"]>0 else 2
if __name__=="__main__":raise SystemExit(main())
