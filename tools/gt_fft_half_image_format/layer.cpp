// Diagnostic-only Vulkan loader layer. Never print or export program bytes.
// Loader chaining follows Khronos Vulkan-Loader LoaderLayerInterface.md.
#include <vulkan/vulkan.h>
#include <vulkan/vk_layer.h>
#include <openssl/sha.h>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <memory>
#include <mutex>
#include <string>
#include <unordered_map>
#include <vector>
#include <fcntl.h>
#include <unistd.h>

namespace {
struct Instance {
    VkInstance instance{};
    PFN_vkGetInstanceProcAddr gipa{};
    PFN_GetPhysicalDeviceProcAddr pgpa{};
    PFN_vkDestroyInstance destroy{};
};
using Words=std::vector<uint32_t>;
struct Pipeline {
    std::shared_ptr<const Words> code;
    std::string entry;
    uint32_t spec_count=0;
    size_t spec_bytes=0;
    std::shared_ptr<const Words> before;
};
struct Device {
    VkDevice device{};
    bool extended_enabled=false;
    PFN_vkGetDeviceProcAddr gdpa{};
    std::unordered_map<std::string,PFN_vkVoidFunction> next;
    std::unordered_map<VkShaderModule,std::shared_ptr<const Words>> modules;
    std::unordered_map<VkPipeline,Pipeline> pipelines;
    std::unordered_map<VkCommandBuffer,VkPipeline> bound;
};
std::mutex mu;
std::unordered_map<void*,Instance> instances;
std::unordered_map<void*,std::shared_ptr<Device>> devices;
template<class T> void* key(T value){return value?*reinterpret_cast<void* const*>(value):nullptr;}
template<class T> Instance inst(T handle){
    std::lock_guard<std::mutex> lock(mu);
    auto it=instances.find(key(handle));return it==instances.end()?Instance{}:it->second;
}
template<class T> std::shared_ptr<Device> dev(T handle){
    std::lock_guard<std::mutex> lock(mu);
    auto it=devices.find(key(handle));return it==devices.end()?nullptr:it->second;
}
template<class F> F downstream(const std::shared_ptr<Device>& d,const char* name){
    auto i=d->next.find(name);
    return i==d->next.end()?nullptr:reinterpret_cast<F>(i->second);
}
template<class T,class C> T* link_info(const C* c,VkStructureType st){
    auto p=reinterpret_cast<const VkBaseInStructure*>(c->pNext);
    while(p){
        if(p->sType==st){
            auto q=reinterpret_cast<const T*>(p);
            if(q->function==VK_LAYER_LINK_INFO)return const_cast<T*>(q);
        }
        p=p->pNext;
    }
    return nullptr;
}
bool token(const std::string& s,size_t limit){
    return !s.empty()&&s.size()<=limit&&std::all_of(s.begin(),s.end(),[](unsigned char c){return std::isalnum(c)||c=='-'||c=='_';});
}
bool exclusive_write(const std::string& p,const void* data,size_t size){
    int fd=open(p.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(fd<0)return false;
    auto b=static_cast<const char*>(data);size_t off=0;
    while(off<size){ssize_t n=write(fd,b+off,size-off);if(n<=0){close(fd);return false;}off+=size_t(n);}
    return close(fd)==0;
}
void capture(const Pipeline& p,uint32_t x,uint32_t y,uint32_t z){
    const char* root=std::getenv("GT_FFT_CAPTURE_DIR");
    if(!root||std::strcmp(root,"/github/workspace/gt-fft-bank-private/vktrace")!=0)return;
    if(!((x==1&&y==512&&z==1)||(x==64&&y==64&&z==1)))return;
    std::string dir(root),label,extra;uint32_t gx=0,gy=0,gz=0;
    std::ifstream marker(dir+"/capture.marker");
    if(!(marker>>label>>gx>>gy>>gz)||marker>>extra||gx!=x||gy!=y||gz!=z||!token(label,48))return;
    if(label!="control"&&label!="indexed-6"&&label!="indexed-7"&&label!="indexed-16"&&label!="indexed-17"&&
       label!="standalone-6"&&label!="standalone-7"&&label!="standalone-16"&&label!="standalone-17")return;
    if(!p.code||p.code->empty()||!token(p.entry,128))return;
    std::string stem=dir+"/"+label;
    if(!exclusive_write(stem+".spv",p.code->data(),p.code->size()*sizeof(uint32_t))){
        const char v='1';exclusive_write(stem+".duplicate",&v,1);return;
    }
    std::string meta=std::to_string(x)+" "+std::to_string(y)+" "+std::to_string(z)+" "+
        std::to_string(p.spec_count)+" "+std::to_string(p.spec_bytes)+" "+p.entry+"\n";
    exclusive_write(stem+".meta",meta.data(),meta.size());
    if(p.before)exclusive_write(stem+".before.spv",p.before->data(),p.before->size()*sizeof(uint32_t));
}
PFN_vkVoidFunction device_intercept(const char*);
VKAPI_ATTR VkResult VKAPI_CALL create_instance(const VkInstanceCreateInfo* c,const VkAllocationCallbacks* a,VkInstance* out){
    auto chain=link_info<VkLayerInstanceCreateInfo>(c,VK_STRUCTURE_TYPE_LOADER_INSTANCE_CREATE_INFO);
    if(!chain||!chain->u.pLayerInfo)return VK_ERROR_INITIALIZATION_FAILED;
    auto g=chain->u.pLayerInfo->pfnNextGetInstanceProcAddr;
    auto pg=chain->u.pLayerInfo->pfnNextGetPhysicalDeviceProcAddr;
    auto next=reinterpret_cast<PFN_vkCreateInstance>(g(nullptr,"vkCreateInstance"));
    chain->u.pLayerInfo=chain->u.pLayerInfo->pNext;
    if(!next)return VK_ERROR_INITIALIZATION_FAILED;
    VkResult result=next(c,a,out);
    if(result==VK_SUCCESS){
        auto destroy=reinterpret_cast<PFN_vkDestroyInstance>(g(*out,"vkDestroyInstance"));
        if(!destroy)return VK_ERROR_INITIALIZATION_FAILED;
        std::lock_guard<std::mutex> lock(mu);instances[key(*out)]={*out,g,pg,destroy};
    }
    return result;
}
VKAPI_ATTR void VKAPI_CALL destroy_instance(VkInstance h,const VkAllocationCallbacks* a){
    auto i=inst(h);if(!i.gipa)return;
    auto next=i.destroy;
    {std::lock_guard<std::mutex> lock(mu);instances.erase(key(h));}
    if(next)next(h,a);
}
VKAPI_ATTR VkResult VKAPI_CALL create_device(VkPhysicalDevice gpu,const VkDeviceCreateInfo* c,const VkAllocationCallbacks* a,VkDevice* out){
    auto i=inst(gpu);
    auto chain=link_info<VkLayerDeviceCreateInfo>(c,VK_STRUCTURE_TYPE_LOADER_DEVICE_CREATE_INFO);
    if(!i.instance||!chain||!chain->u.pLayerInfo)return VK_ERROR_INITIALIZATION_FAILED;
    auto g=chain->u.pLayerInfo->pfnNextGetInstanceProcAddr;
    auto dg=chain->u.pLayerInfo->pfnNextGetDeviceProcAddr;
    auto next=reinterpret_cast<PFN_vkCreateDevice>(g(i.instance,"vkCreateDevice"));
    chain->u.pLayerInfo=chain->u.pLayerInfo->pNext;
    if(!next||!dg)return VK_ERROR_INITIALIZATION_FAILED;
    bool enabled=c->pEnabledFeatures&&c->pEnabledFeatures->shaderStorageImageExtendedFormats;
    for(auto p=reinterpret_cast<const VkBaseInStructure*>(c->pNext);p;p=p->pNext)
        if(p->sType==VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2)
            enabled=reinterpret_cast<const VkPhysicalDeviceFeatures2*>(p)->features.shaderStorageImageExtendedFormats;
    VkResult result=next(gpu,c,a,out);
    if(result==VK_SUCCESS){
        auto d=std::make_shared<Device>();d->device=*out;d->gdpa=dg;d->extended_enabled=enabled;
        // Resolve each downstream core entry once, while the loader is still
        // initializing the chain. Do not resolve intercepted commands again
        // through the live device dispatch table after vkCreateDevice returns.
        static const char* names[]={"vkDestroyDevice","vkCreateShaderModule","vkDestroyShaderModule",
            "vkCreateComputePipelines","vkDestroyPipeline","vkBeginCommandBuffer","vkFreeCommandBuffers",
            "vkCmdBindPipeline","vkCmdDispatch"};
        for(const char* name:names){
            auto p=dg(*out,name);
            if(!p||p==device_intercept(name)){
                auto destroy=reinterpret_cast<PFN_vkDestroyDevice>(dg(*out,"vkDestroyDevice"));
                if(destroy&&reinterpret_cast<PFN_vkVoidFunction>(destroy)!=device_intercept("vkDestroyDevice"))destroy(*out,a);
                return VK_ERROR_INITIALIZATION_FAILED;
            }
            d->next.emplace(name,p);
        }
        std::lock_guard<std::mutex> lock(mu);devices[key(*out)]=d;
    }
    return result;
}
VKAPI_ATTR void VKAPI_CALL destroy_device(VkDevice h,const VkAllocationCallbacks* a){
    auto d=dev(h);if(!d)return;auto next=downstream<PFN_vkDestroyDevice>(d,"vkDestroyDevice");
    {std::lock_guard<std::mutex> lock(mu);devices.erase(key(h));}
    if(next)next(h,a);
}
VKAPI_ATTR VkResult VKAPI_CALL create_shader(VkDevice h,const VkShaderModuleCreateInfo* c,const VkAllocationCallbacks* a,VkShaderModule* out){
    auto d=dev(h);if(!d)return VK_ERROR_INITIALIZATION_FAILED;
    auto result=downstream<PFN_vkCreateShaderModule>(d,"vkCreateShaderModule")(h,c,a,out);
    if(result==VK_SUCCESS&&c->pCode&&c->codeSize>=20&&c->codeSize<=1048576&&c->codeSize%4==0&&c->pCode[0]==0x07230203){
        std::lock_guard<std::mutex> lock(mu);
        if(d->modules.size()<256)d->modules[*out]=std::make_shared<Words>(c->pCode,c->pCode+c->codeSize/4);
    }
    return result;
}
VKAPI_ATTR void VKAPI_CALL destroy_shader(VkDevice h,VkShaderModule s,const VkAllocationCallbacks* a){
    auto d=dev(h);if(!d)return;
    {std::lock_guard<std::mutex> lock(mu);d->modules.erase(s);}
    downstream<PFN_vkDestroyShaderModule>(d,"vkDestroyShaderModule")(h,s,a);
}
// Diagnostic only: substitute exact SHA-pinned modules in isolated Unity.
std::string digest(const Words& w){
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(w.data()),w.size()*sizeof(uint32_t),hash);
    std::ostringstream s;s<<std::hex<<std::setfill('0');
    for(auto b:hash)s<<std::setw(2)<<unsigned(b);
    return s.str();
}
bool hash_token(const std::string& s){
    return s.size()==64&&std::all_of(s.begin(),s.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');});
}
// Only this isolated experiment: change one image format word, never an entrypoint.
bool half_patch(const Words& original,uint32_t from,uint32_t to,bool extended_enabled,std::shared_ptr<const Words>& out){
    if(original.size()<5||original[0]!=0x07230203||original[3]==0||original[4]!=0)return false;
    if(!((from==1&&to==2)||(from==6&&to==7)))return false;
    bool ext=false,formatless=false;size_t at=0;unsigned outputs=0;
    for(size_t i=5;i<original.size();){
        uint32_t n=original[i]>>16,op=original[i]&65535;
        if(!n||i+n>original.size())return false;
        if(op==17&&n==2&&original[i+1]==49)ext=true;
        if(op==17&&n==2&&original[i+1]==56)formatless=true;
        if(op==25&&(n==9||n==10)&&original[i+7]==2){
            if(original[i+8]!=from)return false;
            at=i+8;++outputs;
        }
        i+=n;
    }
    if(outputs!=1||formatless||(ext&&!extended_enabled)||(to==7&&(!ext||!extended_enabled)))return false;
    auto w=std::make_shared<Words>(original);(*w)[at]=to;out=w;return true;
}
bool replacement_for(const Words& original,bool extended_enabled,std::shared_ptr<const Words>& out){
    const char* root=std::getenv("GT_FFT_CAPTURE_DIR");
    if(!root||std::strcmp(root,"/github/workspace/gt-fft-bank-private/vktrace")!=0)return true;
    std::ifstream map("/github/workspace/gt-fft-bank-private/half-map.txt");
    if(!map)return true; // source-free smoke only; actual dispatch gate requires patch.
    unsigned from=0,to=0;
    if(!(map>>from>>to)||!((from==1&&to==2)||(from==6&&to==7)))return false;
    std::vector<std::string> pins;std::string pin;
    while(map>>pin){
        if(pins.size()>=8||!hash_token(pin)||std::find(pins.begin(),pins.end(),pin)!=pins.end())return false;
        pins.push_back(pin);
    }
    if(!map.eof()||pins.size()!=8)return false;
    if(std::find(pins.begin(),pins.end(),digest(original))==pins.end())return true;
    return half_patch(original,from,to,extended_enabled,out);
}
VKAPI_ATTR VkResult VKAPI_CALL create_compute(VkDevice h,VkPipelineCache cache,uint32_t n,const VkComputePipelineCreateInfo* c,const VkAllocationCallbacks* a,VkPipeline* out){
    auto d=dev(h);if(!d)return VK_ERROR_INITIALIZATION_FAILED;
    if(!n||n>256)return VK_ERROR_INITIALIZATION_FAILED;
    std::vector<VkComputePipelineCreateInfo> infos(c,c+n);
    std::vector<std::shared_ptr<const Words>> programs(n),before(n);
    std::vector<VkShaderModule> temporary(n,VK_NULL_HANDLE);
    const auto destroy=downstream<PFN_vkDestroyShaderModule>(d,"vkDestroyShaderModule");
    const auto create=downstream<PFN_vkCreateShaderModule>(d,"vkCreateShaderModule");
    auto release=[&](){for(auto module:temporary)if(module)destroy(h,module,a);};
    {
        std::lock_guard<std::mutex> lock(mu);
        for(uint32_t j=0;j<n;j++){
            auto i=d->modules.find(c[j].stage.module);
            if(i!=d->modules.end())programs[j]=i->second;
        }
    }
    for(uint32_t j=0;j<n;j++){
        if(!programs[j])continue;
        std::shared_ptr<const Words> replacement;
        if(!replacement_for(*programs[j],d->extended_enabled,replacement)){release();return VK_ERROR_INITIALIZATION_FAILED;}
        if(!replacement)continue;
        const auto spec=c[j].stage.pSpecializationInfo;
        if(spec&&(spec->mapEntryCount!=0||spec->dataSize!=0)){release();return VK_ERROR_INITIALIZATION_FAILED;}
        VkShaderModuleCreateInfo ci{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
        ci.codeSize=replacement->size()*4;ci.pCode=replacement->data();
        const auto rc=create(h,&ci,a,&temporary[j]);
        if(rc!=VK_SUCCESS){release();return rc;}
        infos[j].stage.module=temporary[j]; // preserve the actual entrypoint
        before[j]=programs[j];programs[j]=replacement;
    }
    const auto result=downstream<PFN_vkCreateComputePipelines>(d,"vkCreateComputePipelines")(h,cache,n,infos.data(),a,out);
    release();
    if(result!=VK_SUCCESS)return result;
    std::lock_guard<std::mutex> lock(mu);
    for(uint32_t j=0;j<n&&d->pipelines.size()<256;j++){
        if(!out[j]||!programs[j]||!infos[j].stage.pName)continue;
        const auto spec=infos[j].stage.pSpecializationInfo;
        d->pipelines[out[j]]={programs[j],infos[j].stage.pName,spec?spec->mapEntryCount:0,spec?spec->dataSize:0,before[j]};
    }
    return result;
}
VKAPI_ATTR void VKAPI_CALL destroy_pipeline(VkDevice h,VkPipeline p,const VkAllocationCallbacks* a){
    auto d=dev(h);if(!d)return;
    {std::lock_guard<std::mutex> lock(mu);d->pipelines.erase(p);}
    downstream<PFN_vkDestroyPipeline>(d,"vkDestroyPipeline")(h,p,a);
}
VKAPI_ATTR VkResult VKAPI_CALL begin_cmd(VkCommandBuffer c,const VkCommandBufferBeginInfo* i){
    auto d=dev(c);if(!d)return VK_ERROR_INITIALIZATION_FAILED;
    {std::lock_guard<std::mutex> lock(mu);d->bound.erase(c);}
    return downstream<PFN_vkBeginCommandBuffer>(d,"vkBeginCommandBuffer")(c,i);
}
VKAPI_ATTR void VKAPI_CALL free_cmd(VkDevice h,VkCommandPool pool,uint32_t n,const VkCommandBuffer* c){
    auto d=dev(h);if(!d)return;
    {std::lock_guard<std::mutex> lock(mu);for(uint32_t j=0;j<n;j++)d->bound.erase(c[j]);}
    downstream<PFN_vkFreeCommandBuffers>(d,"vkFreeCommandBuffers")(h,pool,n,c);
}
VKAPI_ATTR void VKAPI_CALL bind_pipeline(VkCommandBuffer c,VkPipelineBindPoint point,VkPipeline p){
    auto d=dev(c);if(!d)return;
    downstream<PFN_vkCmdBindPipeline>(d,"vkCmdBindPipeline")(c,point,p);
    if(point==VK_PIPELINE_BIND_POINT_COMPUTE){
        std::lock_guard<std::mutex> lock(mu);
        if(d->bound.size()<4096||d->bound.count(c))d->bound[c]=p;
    }
}
VKAPI_ATTR void VKAPI_CALL dispatch(VkCommandBuffer c,uint32_t x,uint32_t y,uint32_t z){
    auto d=dev(c);if(!d)return;
    Pipeline p;
    {std::lock_guard<std::mutex> lock(mu);auto b=d->bound.find(c);if(b!=d->bound.end()){auto q=d->pipelines.find(b->second);if(q!=d->pipelines.end())p=q->second;}}
    if(p.code)capture(p,x,y,z);
    const char* root=std::getenv("GT_FFT_CAPTURE_DIR");
    if(root&&std::strcmp(root,"/github/workspace/gt-fft-bank-private/vktrace")==0&&x==1&&y==512&&z==1){
        const bool ok=bool(p.before)&&bool(p.code)&&p.spec_count==0&&p.spec_bytes==0;
        const char f=d->extended_enabled?'1':'0',v=ok?'1':'0';
        exclusive_write(std::string(root)+"/half-extended-feature",&f,1);
        exclusive_write(std::string(root)+(ok?"/half-patched":"/half-blocked"),&v,1);
        if(!ok)return;
    }
    downstream<PFN_vkCmdDispatch>(d,"vkCmdDispatch")(c,x,y,z);
}
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL gipa(VkInstance,const char*);
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL gdpa(VkDevice,const char*);
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL pgpa(VkInstance h,const char* name){
    if(!h||!name)return nullptr;
    auto i=inst(h);return i.pgpa?i.pgpa(h,name):nullptr;
}
PFN_vkVoidFunction device_intercept(const char* n){
#define HOOK(s,f) if(std::strcmp(n,s)==0)return reinterpret_cast<PFN_vkVoidFunction>(f)
    HOOK("vkGetDeviceProcAddr",gdpa);
    HOOK("vkDestroyDevice",destroy_device);
    HOOK("vkCreateShaderModule",create_shader);
    HOOK("vkDestroyShaderModule",destroy_shader);
    HOOK("vkCreateComputePipelines",create_compute);
    HOOK("vkDestroyPipeline",destroy_pipeline);
    HOOK("vkBeginCommandBuffer",begin_cmd);
    HOOK("vkFreeCommandBuffers",free_cmd);
    HOOK("vkCmdBindPipeline",bind_pipeline);
    HOOK("vkCmdDispatch",dispatch);
#undef HOOK
    return nullptr;
}
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL gdpa(VkDevice h,const char* n){
    if(!n||!h)return nullptr;
    if(std::strcmp(n,"vkGetDeviceProcAddr")==0)return reinterpret_cast<PFN_vkVoidFunction>(gdpa);
    auto d=dev(h);
    if(auto p=device_intercept(n))return d&&d->next.count(n)?p:nullptr;
    return d?d->gdpa(h,n):nullptr;
}
VKAPI_ATTR PFN_vkVoidFunction VKAPI_CALL gipa(VkInstance h,const char* n){
    if(!n)return nullptr;
#define HOOK(s,f) if(std::strcmp(n,s)==0)return reinterpret_cast<PFN_vkVoidFunction>(f)
    HOOK("vkGetInstanceProcAddr",gipa);
    HOOK("vkCreateInstance",create_instance);
    if(!h)return nullptr;
    HOOK("vk_layerGetPhysicalDeviceProcAddr",pgpa);
    HOOK("vkDestroyInstance",destroy_instance);
    HOOK("vkCreateDevice",create_device);
#undef HOOK
    if(auto p=device_intercept(n))return p;
    auto i=inst(h);return i.gipa?i.gipa(h,n):nullptr;
}
}
extern "C" __attribute__((visibility("default"))) VKAPI_ATTR VkResult VKAPI_CALL
vkNegotiateLoaderLayerInterfaceVersion(VkNegotiateLayerInterface* version){
    if(!version||version->sType!=LAYER_NEGOTIATE_INTERFACE_STRUCT||version->loaderLayerInterfaceVersion<2)return VK_ERROR_INITIALIZATION_FAILED;
    version->loaderLayerInterfaceVersion=2;
    version->pfnGetInstanceProcAddr=gipa;version->pfnGetDeviceProcAddr=gdpa;version->pfnGetPhysicalDeviceProcAddr=pgpa;
    return VK_SUCCESS;
}
