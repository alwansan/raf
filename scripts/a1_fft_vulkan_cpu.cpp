// Private FFT differential execution on a CPU Vulkan ICD (Mesa lavapipe).
// Only aggregate numeric metrics are printed; no image pixels or shader payloads.
// A successful comparison covers ONE deterministic workload, not all input data,
// Unity shaders, device Vulkan drivers or original mathematical equivalence.
#include <vulkan/vulkan.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

static void require(bool cond, const char* message) {
    if (!cond) throw std::runtime_error(message);
}
static void check(VkResult result, const char* operation) {
    if (result != VK_SUCCESS) throw std::runtime_error(
        std::string(operation) + " VkResult=" + std::to_string(result));
}
static std::vector<uint32_t> spirvFile(const char* path) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    require(bool(f), "Shader file unavailable");
    auto n=static_cast<std::streamoff>(f.tellg());
    require(n >= 20 && n <= 1048576 && n%4 == 0, "Shader length invalid");
    std::vector<uint32_t> result(size_t(n)/4);
    f.seekg(0);
    f.read(reinterpret_cast<char*>(result.data()), n);
    require(bool(f) && result[0]==0x07230203, "Shader SPIR-V invalid");
    return result;
}
static uint32_t inputSeed=0;
static float inputValue(uint32_t x,uint32_t y,int texture,int channel) {
    const float t=float((x*17u+y*13u+texture*19u+channel*7u+inputSeed*101u)%1021u)*0.017f;
    return std::sin(t)*0.3f+std::cos(t*0.27f)*0.15f;
}
// Finite exact half-precision sentinel; counts only stored format channels.
static constexpr float sentinel=8192.f;
struct ImageFormat {
    std::string token;
    VkFormat vk=VK_FORMAT_UNDEFINED;
    uint32_t channels=0, componentBytes=0;
    uint32_t stride() const {return channels*componentBytes;}
};
static ImageFormat selectFormat(const std::string& token) {
    if(token=="rg16f") return {token,VK_FORMAT_R16G16_SFLOAT,2,2};
    if(token=="rg32f") return {token,VK_FORMAT_R32G32_SFLOAT,2,4};
    if(token=="rgba16f") return {token,VK_FORMAT_R16G16B16A16_SFLOAT,4,2};
    if(token=="rgba32f") return {token,VK_FORMAT_R32G32B32A32_SFLOAT,4,4};
    throw std::runtime_error("Unsupported original FFT Vulkan image format");
}
static uint16_t floatToHalf(float value) {
    uint32_t word=0;
    std::memcpy(&word,&value,4);
    const uint32_t sign=(word>>16)&0x8000u;
    uint32_t exp=(word>>23)&255u, mant=word&0x7fffffu;
    if(exp==255u) return uint16_t(sign|0x7c00u|(mant?0x0200u:0u));
    int32_t halfExp=int32_t(exp)-127+15;
    if(halfExp>=31) return uint16_t(sign|0x7c00u);
    if(halfExp<=0) {
        if(halfExp < -10) return uint16_t(sign);
        mant|=0x800000u;
        const uint32_t shift=uint32_t(14-halfExp);
        const uint32_t top=mant>>shift;
        const uint32_t rest=mant&((1u<<shift)-1u);
        const uint32_t midpoint=1u<<(shift-1);
        return uint16_t(sign|top+(rest>midpoint||(rest==midpoint&&(top&1u))));
    }
    // RNE at float32 13-bit precision discarded for binary16, including carry.
    const uint32_t rounded=mant+0x0fffu+((mant>>13)&1u);
    if(rounded&0x800000u) {
        halfExp++;
        if(halfExp>=31) return uint16_t(sign|0x7c00u);
        mant=0;
    } else mant=rounded;
    return uint16_t(sign|(uint32_t(halfExp)<<10)|(mant>>13));
}
static float halfToFloat(uint16_t half) {
    const float sign=(half&0x8000u)?-1.f:1.f;
    const uint32_t exp=(half>>10)&31u, mant=half&1023u;
    if(exp==31u) return mant?std::numeric_limits<float>::quiet_NaN():
                               sign*std::numeric_limits<float>::infinity();
    if(exp==0u) return sign*std::ldexp(float(mant),-24);
    return sign*std::ldexp(float(1024u+mant),int(exp)-25);
}
struct Texture {
    VkImage image=VK_NULL_HANDLE;
    VkImageView view=VK_NULL_HANDLE;
    VkDeviceMemory memory=VK_NULL_HANDLE;
    VkSubresourceLayout sub{};
    uint8_t* address=nullptr;
};
static void putPixel(const Texture& t,uint32_t x,uint32_t y,
                     const ImageFormat& fmt,const std::array<float,4>& values) {
    auto ptr=t.address+t.sub.offset+y*t.sub.rowPitch+x*fmt.stride();
    for(uint32_t c=0;c<fmt.channels;c++) {
        if(fmt.componentBytes==2u) {
            uint16_t bits=floatToHalf(values[c]);
            std::memcpy(ptr+c*2u,&bits,2u);
        } else std::memcpy(ptr+c*4u,&values[c],4u);
    }
}
static std::array<float,4> pixel(const Texture& t,uint32_t x,uint32_t y,
                                 const ImageFormat& fmt) {
    std::array<float,4> v={0.f,0.f,0.f,1.f};
    auto ptr=t.address+t.sub.offset+y*t.sub.rowPitch+x*fmt.stride();
    for(uint32_t c=0;c<fmt.channels;c++) {
        if(fmt.componentBytes==2u) {
            uint16_t bits=0;
            std::memcpy(&bits,ptr+c*2u,2u);
            v[c]=halfToFloat(bits);
        } else std::memcpy(&v[c],ptr+c*4u,4u);
    }
    return v;
}
static bool isWritten(const std::array<float,4>& p,const ImageFormat& fmt) {
    for(uint32_t i=0;i<fmt.channels;i++)if(p[i]!=sentinel)return true;
    return false;
}
int main(int argc,char** argv) {
 try {
    require(argc>=5 && argc<=8,"Usage: original.spv roundtrip.spv width height [seed [groupsY [rg16f|rg32f|rgba16f|rgba32f]] | --canary]");
    bool canary=(argc==6 && std::string(argv[5])=="--canary");
    if(!canary && argc>=6) {
        inputSeed=uint32_t(std::stoul(argv[5]));
        require(inputSeed<=1023 && std::to_string(inputSeed)==argv[5],"Invalid bounded input seed");
    }
    uint32_t dispatchGroupY=1;
    if(argc==7) {
        dispatchGroupY=uint32_t(std::stoul(argv[6]));
        require(dispatchGroupY>=1 && dispatchGroupY<=2 &&
                std::to_string(dispatchGroupY)==argv[6],"Invalid bounded Y dispatch");
    }
    const ImageFormat imageFormat=selectFormat(argc==8?argv[7]:"rgba32f");
    auto original=spirvFile(argv[1]),roundtrip=spirvFile(argv[2]);
    int widthInt=std::stoi(argv[3]),heightInt=std::stoi(argv[4]);
    require(widthInt>=1 && widthInt<=2048 && heightInt>=1 && heightInt<=2048,
            "Unsafe Vulkan image extent");
    uint32_t w=uint32_t(widthInt),h=uint32_t(heightInt);
    VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};
    app.pApplicationName="RaftA1CpuShaderNumerics";
    app.apiVersion=VK_API_VERSION_1_1;
    VkInstanceCreateInfo instanceInfo{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    instanceInfo.pApplicationInfo=&app;
    VkInstance instance=VK_NULL_HANDLE;
    check(vkCreateInstance(&instanceInfo,nullptr,&instance),"vkCreateInstance");
    uint32_t count=0;
    check(vkEnumeratePhysicalDevices(instance,&count,nullptr),"enumerate devices");
    require(count>0 && count<64,"No bounded Vulkan CPU devices");
    std::vector<VkPhysicalDevice> physicals(count);
    check(vkEnumeratePhysicalDevices(instance,&count,physicals.data()),"enumerate GPU handles");
    VkPhysicalDevice physical=VK_NULL_HANDLE;
    for(auto candidate:physicals) {
        VkPhysicalDeviceProperties props{};
        vkGetPhysicalDeviceProperties(candidate,&props);
        if(props.deviceType==VK_PHYSICAL_DEVICE_TYPE_CPU) {
            physical=candidate;break;
        }
    }
    require(physical!=VK_NULL_HANDLE,"No software Vulkan CPU driver: refuse GPU fallback");
    VkPhysicalDeviceProperties properties{};
    vkGetPhysicalDeviceProperties(physical,&properties);
    VkPhysicalDeviceFeatures features{};
    vkGetPhysicalDeviceFeatures(physical,&features);
    require(features.shaderStorageImageWriteWithoutFormat==VK_TRUE,
            "CPU Vulkan does not support storageImageWriteWithoutFormat");
    require(properties.limits.maxComputeWorkGroupInvocations>=1024 || canary,
            "CPU Vulkan max workgroup invocations below 1024");
    VkFormatProperties formatProps{};
    vkGetPhysicalDeviceFormatProperties(physical,imageFormat.vk,&formatProps);
    require((formatProps.linearTilingFeatures&
             (VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT|VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT))==
            (VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT|VK_FORMAT_FEATURE_STORAGE_IMAGE_BIT),
            "CPU driver lacks original FFT requested linear sampled/storage image format");
    uint32_t queues=0;
    vkGetPhysicalDeviceQueueFamilyProperties(physical,&queues,nullptr);
    require(queues>0 && queues<64,"Compute queue families missing");
    std::vector<VkQueueFamilyProperties> queueProps(queues);
    vkGetPhysicalDeviceQueueFamilyProperties(physical,&queues,queueProps.data());
    uint32_t family=queues;
    for(uint32_t i=0;i<queues;i++)if(queueProps[i].queueFlags&VK_QUEUE_COMPUTE_BIT) {
        family=i;break;
    }
    require(family<queues,"No CPU compute queue");
    VkDeviceQueueCreateInfo qInfo{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    float priority=1.f;
    qInfo.queueFamilyIndex=family;
    qInfo.queueCount=1;
    qInfo.pQueuePriorities=&priority;
    VkPhysicalDeviceFeatures enabled{};
    enabled.shaderStorageImageWriteWithoutFormat=VK_TRUE;
    VkDeviceCreateInfo deviceInfo{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
    deviceInfo.queueCreateInfoCount=1;
    deviceInfo.pQueueCreateInfos=&qInfo;
    deviceInfo.pEnabledFeatures=&enabled;
    VkDevice device=VK_NULL_HANDLE;
    check(vkCreateDevice(physical,&deviceInfo,nullptr,&device),"vkCreateDevice");
    VkQueue queue=VK_NULL_HANDLE;
    vkGetDeviceQueue(device,family,0,&queue);
    VkPhysicalDeviceMemoryProperties memProps{};
    vkGetPhysicalDeviceMemoryProperties(physical,&memProps);
    std::array<Texture,4> images{};
    VkImageSubresource sub{VK_IMAGE_ASPECT_COLOR_BIT,0,0};
    for(int t=0;t<4;t++) {
        auto& tex=images[t];
        VkImageCreateInfo ci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
        ci.imageType=VK_IMAGE_TYPE_2D;
        ci.format=imageFormat.vk;
        ci.extent={w,h,1};
        ci.mipLevels=1;ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;
        ci.tiling=VK_IMAGE_TILING_LINEAR;
        ci.usage=(t<2)?VK_IMAGE_USAGE_SAMPLED_BIT:VK_IMAGE_USAGE_STORAGE_BIT;
        ci.sharingMode=VK_SHARING_MODE_EXCLUSIVE;
        ci.initialLayout=VK_IMAGE_LAYOUT_PREINITIALIZED;
        check(vkCreateImage(device,&ci,nullptr,&tex.image),"vkCreateImage");
        VkMemoryRequirements required{};
        vkGetImageMemoryRequirements(device,tex.image,&required);
        uint32_t type=memProps.memoryTypeCount;
        for(uint32_t i=0;i<memProps.memoryTypeCount;i++){
            VkMemoryPropertyFlags want=VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|
                VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
            if((required.memoryTypeBits&(1u<<i))&&
                (memProps.memoryTypes[i].propertyFlags&want)==want){type=i;break;}
        }
        require(type<memProps.memoryTypeCount,"CPU driver lacks mapped host-coherent image memory");
        VkMemoryAllocateInfo ai{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
        ai.allocationSize=required.size;ai.memoryTypeIndex=type;
        check(vkAllocateMemory(device,&ai,nullptr,&tex.memory),"vkAllocateMemory");
        check(vkBindImageMemory(device,tex.image,tex.memory,0),"vkBindImageMemory");
        vkGetImageSubresourceLayout(device,tex.image,&sub,&tex.sub);
        void* mapped=nullptr;
        check(vkMapMemory(device,tex.memory,0,required.size,0,&mapped),"vkMapMemory");
        tex.address=reinterpret_cast<uint8_t*>(mapped);
        require(tex.sub.rowPitch>=w*imageFormat.stride()&&
                tex.sub.offset+(h-1)*tex.sub.rowPitch+w*imageFormat.stride()<=required.size,
                "Mapped image layout out of bounds");
        for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++) {
            std::array<float,4> p{};
            for(int c=0;c<4;c++)p[c]=(t<2)?inputValue(x,y,t,c):sentinel;
            putPixel(tex,x,y,imageFormat,p);
        }
        VkImageViewCreateInfo view{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
        view.image=tex.image;view.viewType=VK_IMAGE_VIEW_TYPE_2D;
        view.format=imageFormat.vk;
        view.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
        check(vkCreateImageView(device,&view,nullptr,&tex.view),"vkCreateImageView");
    }
    std::array<VkDescriptorSetLayoutBinding,3> bindings{};
    for(uint32_t i=0;i<3;i++){
        bindings[i].binding=i;bindings[i].descriptorCount=1;
        bindings[i].descriptorType=i<2?VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:
                                      VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
        bindings[i].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;
    }
    VkDescriptorSetLayoutCreateInfo layoutCi{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
    layoutCi.bindingCount=3;layoutCi.pBindings=bindings.data();
    VkDescriptorSetLayout setLayout=VK_NULL_HANDLE;
    check(vkCreateDescriptorSetLayout(device,&layoutCi,nullptr,&setLayout),
          "vkCreateDescriptorSetLayout");
    VkPipelineLayoutCreateInfo pipeLayoutCi{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    pipeLayoutCi.setLayoutCount=1;pipeLayoutCi.pSetLayouts=&setLayout;
    VkPipelineLayout pipeLayout=VK_NULL_HANDLE;
    check(vkCreatePipelineLayout(device,&pipeLayoutCi,nullptr,&pipeLayout),
          "vkCreatePipelineLayout");
    std::array<VkDescriptorPoolSize,2> poolSizes{};
    poolSizes[0]={VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,4};
    poolSizes[1]={VK_DESCRIPTOR_TYPE_STORAGE_IMAGE,2};
    VkDescriptorPoolCreateInfo poolCi{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
    poolCi.maxSets=2;poolCi.poolSizeCount=2;poolCi.pPoolSizes=poolSizes.data();
    VkDescriptorPool pool=VK_NULL_HANDLE;
    check(vkCreateDescriptorPool(device,&poolCi,nullptr,&pool),"vkCreateDescriptorPool");
    std::array<VkDescriptorSetLayout,2> layouts={setLayout,setLayout};
    VkDescriptorSetAllocateInfo allocate{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
    allocate.descriptorPool=pool;allocate.descriptorSetCount=2;allocate.pSetLayouts=layouts.data();
    std::array<VkDescriptorSet,2> sets{};
    check(vkAllocateDescriptorSets(device,&allocate,sets.data()),"vkAllocateDescriptorSets");
    std::array<VkDescriptorImageInfo,6> descriptors{};
    std::array<VkWriteDescriptorSet,6> writes{};
    for(int set=0;set<2;set++)for(int binding=0;binding<3;binding++){
        const int ix=set*3+binding;
        descriptors[ix].imageView=images[binding<2?binding:2+set].view;
        descriptors[ix].imageLayout=VK_IMAGE_LAYOUT_GENERAL;
        writes[ix].sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
        writes[ix].dstSet=sets[set];
        writes[ix].dstBinding=binding;
        writes[ix].descriptorCount=1;
        writes[ix].descriptorType=bindings[binding].descriptorType;
        writes[ix].pImageInfo=&descriptors[ix];
    }
    vkUpdateDescriptorSets(device,uint32_t(writes.size()),writes.data(),0,nullptr);
    std::array<VkShaderModule,2> shaderModules{};
    std::array<VkPipeline,2> pipelines{};
    std::array<std::vector<uint32_t>,2> bytes={original,roundtrip};
    for(int i=0;i<2;i++){
        VkShaderModuleCreateInfo sci{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
        sci.codeSize=bytes[i].size()*4;sci.pCode=bytes[i].data();
        check(vkCreateShaderModule(device,&sci,nullptr,&shaderModules[i]),"vkCreateShaderModule");
        VkPipelineShaderStageCreateInfo stage{VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};
        stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;stage.module=shaderModules[i];stage.pName="main";
        VkComputePipelineCreateInfo pc{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
        pc.stage=stage;pc.layout=pipeLayout;
        check(vkCreateComputePipelines(device,VK_NULL_HANDLE,1,&pc,nullptr,&pipelines[i]),
              "vkCreateComputePipelines");
    }
    VkCommandPoolCreateInfo poolCommand{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
    poolCommand.queueFamilyIndex=family;
    VkCommandPool commandPool=VK_NULL_HANDLE;
    check(vkCreateCommandPool(device,&poolCommand,nullptr,&commandPool),"vkCreateCommandPool");
    VkCommandBufferAllocateInfo cmdAllocate{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
    cmdAllocate.commandPool=commandPool;
    cmdAllocate.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;cmdAllocate.commandBufferCount=1;
    VkCommandBuffer cmd=VK_NULL_HANDLE;
    check(vkAllocateCommandBuffers(device,&cmdAllocate,&cmd),"vkAllocateCommandBuffers");
    VkCommandBufferBeginInfo cmdBegin{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
    check(vkBeginCommandBuffer(cmd,&cmdBegin),"vkBeginCommandBuffer");
    std::array<VkImageMemoryBarrier,4> preBarriers{};
    for(int i=0;i<4;i++){
        preBarriers[i].sType=VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
        preBarriers[i].srcAccessMask=VK_ACCESS_HOST_WRITE_BIT;
        preBarriers[i].dstAccessMask=i<2?VK_ACCESS_SHADER_READ_BIT:VK_ACCESS_SHADER_WRITE_BIT;
        preBarriers[i].oldLayout=VK_IMAGE_LAYOUT_PREINITIALIZED;
        preBarriers[i].newLayout=VK_IMAGE_LAYOUT_GENERAL;
        preBarriers[i].srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        preBarriers[i].dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        preBarriers[i].image=images[i].image;
        preBarriers[i].subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
    }
    vkCmdPipelineBarrier(cmd,VK_PIPELINE_STAGE_HOST_BIT,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,
                         0,0,nullptr,0,nullptr,4,preBarriers.data());
    for(int i=0;i<2;i++){
        vkCmdBindPipeline(cmd,VK_PIPELINE_BIND_POINT_COMPUTE,pipelines[i]);
        vkCmdBindDescriptorSets(cmd,VK_PIPELINE_BIND_POINT_COMPUTE,
                                pipeLayout,0,1,&sets[i],0,nullptr);
        vkCmdDispatch(cmd,1,dispatchGroupY,1);
    }
    std::array<VkImageMemoryBarrier,2> postBarriers{};
    for(int i=0;i<2;i++){
        postBarriers[i].sType=VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
        postBarriers[i].srcAccessMask=VK_ACCESS_SHADER_WRITE_BIT;
        postBarriers[i].dstAccessMask=VK_ACCESS_HOST_READ_BIT;
        postBarriers[i].oldLayout=VK_IMAGE_LAYOUT_GENERAL;
        postBarriers[i].newLayout=VK_IMAGE_LAYOUT_GENERAL;
        postBarriers[i].srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        postBarriers[i].dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
        postBarriers[i].image=images[2+i].image;
        postBarriers[i].subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
    }
    vkCmdPipelineBarrier(cmd,VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT,VK_PIPELINE_STAGE_HOST_BIT,
                         0,0,nullptr,0,nullptr,2,postBarriers.data());
    check(vkEndCommandBuffer(cmd),"vkEndCommandBuffer");
    VkSubmitInfo submission{VK_STRUCTURE_TYPE_SUBMIT_INFO};
    submission.commandBufferCount=1;submission.pCommandBuffers=&cmd;
    check(vkQueueSubmit(queue,1,&submission,VK_NULL_HANDLE),"vkQueueSubmit");
    check(vkQueueWaitIdle(queue),"vkQueueWaitIdle");
    uint64_t writesA=0,writesB=0,missing=0,nonFinite=0,canaryErrors=0;
    double sumSquares=0,referenceSquares=0,maxAbs=0;
    for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++) {
        const auto a=pixel(images[2],x,y,imageFormat),b=pixel(images[3],x,y,imageFormat);
        bool writeA=isWritten(a,imageFormat),writeB=isWritten(b,imageFormat);
        writesA+=writeA;writesB+=writeB;
        if(writeA!=writeB) {missing++;continue;}
        if(!writeA)continue;
        for(uint32_t c=0;c<imageFormat.channels;c++){
            const float va=a[c],vb=b[c];
            if(!std::isfinite(va)||!std::isfinite(vb)){nonFinite++;continue;}
            double delta=double(va)-double(vb);
            maxAbs=std::max(maxAbs,std::abs(delta));
            sumSquares+=delta*delta;
            referenceSquares+=double(va)*double(va);
            if(canary && (std::abs(va-(inputValue(x,y,0,c)+inputValue(x,y,1,c)))>1e-5f ||
                          std::abs(vb-(inputValue(x,y,0,c)+inputValue(x,y,1,c)))>1e-5f))
                canaryErrors++;
        }
    }
    require(writesA>0&&writesB>0,"No evidence of any shader image writes");
    const double relative=std::sqrt(sumSquares/std::max(referenceSquares,1e-30));
    bool match=missing==0&&nonFinite==0&&relative<=1e-5&&maxAbs<=1e-4;
    if(canary)require(canaryErrors==0,"Synthetic canary output disagrees with known CPU sum");
    std::cout<<std::setprecision(12)
             <<"RAFT_A1_VULKAN_DIFF {\"cpu_software_vulkan\":true,"
             <<"\"vulkan_image_format\":\""<<imageFormat.token<<"\""
             <<",\"image_channels\":"<<imageFormat.channels
             <<",\"image_component_bits\":"<<imageFormat.componentBytes*8u
             <<",\"extent_width\":"<<w
             <<",\"extent_height\":"<<h
             <<",\"input_seed\":"<<inputSeed
             <<",\"dispatch_group_y\":"<<dispatchGroupY
             <<",\"original_written_pixels\":"<<writesA
             <<",\"roundtrip_written_pixels\":"<<writesB
             <<",\"write_coverage_mismatch_pixels\":"<<missing
             <<",\"nonfinite_components\":"<<nonFinite
             <<",\"max_abs_difference\":"<<maxAbs
             <<",\"relative_l2_difference\":"<<relative
             <<",\"within_selected_tolerance\":"<<(match?"true":"false")
             <<",\"synthetic_canary_verified\":"<<(canary?"true":"false")
             <<",\"unity_gpu_or_android_device_verified\":false}\n";
    check(vkDeviceWaitIdle(device),"vkDeviceWaitIdle");
    for(int i=0;i<4;i++){
        vkUnmapMemory(device,images[i].memory);
        vkDestroyImageView(device,images[i].view,nullptr);
        vkDestroyImage(device,images[i].image,nullptr);
        vkFreeMemory(device,images[i].memory,nullptr);
    }
    vkDestroyCommandPool(device,commandPool,nullptr);
    for(int i=0;i<2;i++){
        vkDestroyPipeline(device,pipelines[i],nullptr);
        vkDestroyShaderModule(device,shaderModules[i],nullptr);
    }
    vkDestroyDescriptorPool(device,pool,nullptr);
    vkDestroyPipelineLayout(device,pipeLayout,nullptr);
    vkDestroyDescriptorSetLayout(device,setLayout,nullptr);
    vkDestroyDevice(device,nullptr);
    vkDestroyInstance(instance,nullptr);
    return 0;
 } catch(const std::exception& e) {
    std::cerr<<"RAFT_A1_VULKAN_ERROR "<<e.what()<<"\n";
    return 2;
 }
}
