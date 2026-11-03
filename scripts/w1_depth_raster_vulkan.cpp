// Private FFT differential execution on a CPU Vulkan ICD (Mesa lavapipe).
// Only aggregate numeric metrics are printed; no image pixels or shader payloads.
// A successful comparison covers ONE deterministic workload, not all input data,
// Unity shaders, device Vulkan drivers or original mathematical equivalence.
#include <vulkan/vulkan.h>
#include <algorithm>
#include <array>
#include <atomic>
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

static std::atomic_uint32_t validationErrors{0},validationWarnings{0};
static VKAPI_ATTR VkBool32 VKAPI_CALL validationCallback(
    VkDebugUtilsMessageSeverityFlagBitsEXT severity,VkDebugUtilsMessageTypeFlagsEXT,
    const VkDebugUtilsMessengerCallbackDataEXT*,void*) {
    // Never print validation contents or original resource/shader identifiers.
    if(severity&VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT)validationErrors++;
    if(severity&VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT)validationWarnings++;
    return VK_FALSE;
}
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
    return 0.5f + std::sin(t)*0.3f+std::cos(t*0.27f)*0.15f;
}
static constexpr float sentinel=123456.f;
struct Texture {
    VkImage image=VK_NULL_HANDLE;
    VkImageView view=VK_NULL_HANDLE;
    VkDeviceMemory memory=VK_NULL_HANDLE;
    VkSubresourceLayout sub{};
    uint8_t* address=nullptr;
};
static std::array<float,4> pixel(const Texture& t,uint32_t x,uint32_t y) {
    std::array<float,4> v{};
    std::memcpy(v.data(),t.address+t.sub.offset+y*t.sub.rowPitch+x*16,16);
    return v;
}
static bool isWritten(const std::array<float,4>& p) {
    return std::any_of(p.begin(),p.end(),[](float f){return f!=sentinel;});
}
int main(int argc,char** argv) {
 try {
    require(argc==12 || argc==13,"Usage: originalVS originalFS rebuiltVS rebuiltFS mask zwrite ztest seed mutation textures zclip [--canary]");
    bool canary=argc==13 && std::string(argv[12])=="--canary";
    const int mask=std::stoi(argv[5]),zwrite=std::stoi(argv[6]),ztest=std::stoi(argv[7]);
    inputSeed=uint32_t(std::stoul(argv[8]));
    const int mutation=std::stoi(argv[9]),textureCount=std::stoi(argv[10]),zclip=std::stoi(argv[11]);
    require((mask==0||mask==15)&&(zwrite==0||zwrite==1)&&ztest>=0&&ztest<=8&&inputSeed<=1023&&mutation>=0&&mutation<=4&&textureCount>=0&&textureCount<=2&&(zclip==0||zclip==1),"Invalid bounded raster configuration");
    uint32_t w=31,h=19;
    const float clearDepth=canary?0.61f:(inputSeed==0?0.21f:(inputSeed==19?0.61f:0.91f));
    std::array<std::vector<uint32_t>,4> binaries={spirvFile(argv[1]),spirvFile(argv[2]),spirvFile(argv[3]),spirvFile(argv[4])};
    VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};
    app.pApplicationName="RaftW1RasterDepthNumerics";
    app.apiVersion=VK_API_VERSION_1_1;
    VkInstanceCreateInfo instanceInfo{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    instanceInfo.pApplicationInfo=&app;
    const char* layer="VK_LAYER_KHRONOS_validation";
    const std::array<const char*,2> extensions={VK_EXT_DEBUG_UTILS_EXTENSION_NAME,VK_EXT_VALIDATION_FEATURES_EXTENSION_NAME};
    VkDebugUtilsMessengerCreateInfoEXT debugInfo{VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};
    debugInfo.messageSeverity=VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT|VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT;
    debugInfo.messageType=VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT|VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT|VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
    debugInfo.pfnUserCallback=validationCallback;
    const VkValidationFeatureEnableEXT syncFeature=VK_VALIDATION_FEATURE_ENABLE_SYNCHRONIZATION_VALIDATION_EXT;
    VkValidationFeaturesEXT validation{VK_STRUCTURE_TYPE_VALIDATION_FEATURES_EXT};
    validation.enabledValidationFeatureCount=1;validation.pEnabledValidationFeatures=&syncFeature;validation.pNext=&debugInfo;
    instanceInfo.pNext=&validation;instanceInfo.enabledLayerCount=1;instanceInfo.ppEnabledLayerNames=&layer;
    instanceInfo.enabledExtensionCount=extensions.size();instanceInfo.ppEnabledExtensionNames=extensions.data();
    VkInstance instance=VK_NULL_HANDLE;
    check(vkCreateInstance(&instanceInfo,nullptr,&instance),"vkCreateInstance");
    auto createDebug=reinterpret_cast<PFN_vkCreateDebugUtilsMessengerEXT>(vkGetInstanceProcAddr(instance,"vkCreateDebugUtilsMessengerEXT"));
    auto destroyDebug=reinterpret_cast<PFN_vkDestroyDebugUtilsMessengerEXT>(vkGetInstanceProcAddr(instance,"vkDestroyDebugUtilsMessengerEXT"));
    require(createDebug&&destroyDebug,"Vulkan validation messenger unavailable");
    VkDebugUtilsMessengerEXT messenger;
    check(createDebug(instance,&debugInfo,nullptr,&messenger),"create private validation messenger");
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
    require(zclip || features.depthClamp,"Required original ZClip Off unsupported by CPU Vulkan");
    VkFormatProperties formatProps{};
    vkGetPhysicalDeviceFormatProperties(physical,VK_FORMAT_R32G32B32A32_SFLOAT,&formatProps);
    require((formatProps.linearTilingFeatures&
             (VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT|VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT))==
            (VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT|VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT),
            "CPU driver lacks linear-tiled RGBA32F sampled/storage support");
    uint32_t queues=0;
    vkGetPhysicalDeviceQueueFamilyProperties(physical,&queues,nullptr);
    require(queues>0 && queues<64,"Compute queue families missing");
    std::vector<VkQueueFamilyProperties> queueProps(queues);
    vkGetPhysicalDeviceQueueFamilyProperties(physical,&queues,queueProps.data());
    uint32_t family=queues;
    for(uint32_t i=0;i<queues;i++)if(queueProps[i].queueFlags&VK_QUEUE_GRAPHICS_BIT) {
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
    enabled.depthClamp=features.depthClamp;
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
        ci.format=VK_FORMAT_R32G32B32A32_SFLOAT;
        ci.extent={w,h,1};
        ci.mipLevels=1;ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;
        ci.tiling=VK_IMAGE_TILING_LINEAR;
        ci.usage=(t<2)?VK_IMAGE_USAGE_SAMPLED_BIT:VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT;
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
        require(tex.sub.rowPitch>=w*16&&
                tex.sub.offset+(h-1)*tex.sub.rowPitch+w*16<=required.size,
                "Mapped image layout out of bounds");
        for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++) {
            std::array<float,4> p{};
            for(int c=0;c<4;c++)p[c]=(t<2)?inputValue(x,y,t,c):sentinel;
            std::memcpy(tex.address+tex.sub.offset+y*tex.sub.rowPitch+x*16,p.data(),16);
        }
        VkImageViewCreateInfo view{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
        view.image=tex.image;view.viewType=VK_IMAGE_VIEW_TYPE_2D;
        view.format=VK_FORMAT_R32G32B32A32_SFLOAT;
        view.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
        check(vkCreateImageView(device,&view,nullptr,&tex.view),"vkCreateImageView");
    }
    VkSamplerCreateInfo samplerInfo{VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
    samplerInfo.magFilter=VK_FILTER_NEAREST;samplerInfo.minFilter=VK_FILTER_NEAREST;
    samplerInfo.mipmapMode=VK_SAMPLER_MIPMAP_MODE_NEAREST;
    samplerInfo.addressModeU=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    samplerInfo.addressModeV=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    samplerInfo.addressModeW=VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
    samplerInfo.maxLod=0;
    VkSampler sampler=VK_NULL_HANDLE;
    check(vkCreateSampler(device,&samplerInfo,nullptr,&sampler),"vkCreateSampler");

    auto memoryType=[&](uint32_t bits,VkMemoryPropertyFlags want){
        for(uint32_t i=0;i<memProps.memoryTypeCount;i++)
            if((bits&(1u<<i))&&(memProps.memoryTypes[i].propertyFlags&want)==want)return i;
        throw std::runtime_error("Required Vulkan memory type unavailable");
    };
    struct Depth {VkImage image;VkImageView view;VkDeviceMemory memory;VkBuffer readback;VkDeviceMemory host;float* mapped;};
    std::array<Depth,2> depths{};
    VkFormatProperties depthProps{};
    vkGetPhysicalDeviceFormatProperties(physical,VK_FORMAT_D32_SFLOAT,&depthProps);
    require(depthProps.optimalTilingFeatures&VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT,"D32 depth attachment unavailable");
    for(auto& d:depths){
        VkImageCreateInfo ci{VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
        ci.imageType=VK_IMAGE_TYPE_2D;ci.format=VK_FORMAT_D32_SFLOAT;ci.extent={w,h,1};
        ci.mipLevels=1;ci.arrayLayers=1;ci.samples=VK_SAMPLE_COUNT_1_BIT;
        ci.tiling=VK_IMAGE_TILING_OPTIMAL;ci.usage=VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT|VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
        check(vkCreateImage(device,&ci,nullptr,&d.image),"create depth image");
        VkMemoryRequirements mr{};vkGetImageMemoryRequirements(device,d.image,&mr);
        VkMemoryAllocateInfo ma{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ma.allocationSize=mr.size;
        ma.memoryTypeIndex=memoryType(mr.memoryTypeBits,0);
        check(vkAllocateMemory(device,&ma,nullptr,&d.memory),"allocate depth");
        check(vkBindImageMemory(device,d.image,d.memory,0),"bind depth");
        VkImageViewCreateInfo vi{VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};vi.image=d.image;vi.viewType=VK_IMAGE_VIEW_TYPE_2D;
        vi.format=VK_FORMAT_D32_SFLOAT;vi.subresourceRange={VK_IMAGE_ASPECT_DEPTH_BIT,0,1,0,1};
        check(vkCreateImageView(device,&vi,nullptr,&d.view),"create depth view");
        VkBufferCreateInfo bi{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};bi.size=w*h*sizeof(float);bi.usage=VK_BUFFER_USAGE_TRANSFER_DST_BIT;
        check(vkCreateBuffer(device,&bi,nullptr,&d.readback),"create depth readback");
        vkGetBufferMemoryRequirements(device,d.readback,&mr);ma.allocationSize=mr.size;
        ma.memoryTypeIndex=memoryType(mr.memoryTypeBits,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
        check(vkAllocateMemory(device,&ma,nullptr,&d.host),"allocate depth readback");
        check(vkBindBufferMemory(device,d.readback,d.host,0),"bind depth readback");
        void* ptr=nullptr;check(vkMapMemory(device,d.host,0,mr.size,0,&ptr),"map depth readback");d.mapped=static_cast<float*>(ptr);
    }
    const std::array<float,18> vertices={-.83f,-.71f,.24f,1.f,.07f,.13f, .91f,-.31f,.79f,.91f,.94f,.21f, .13f,.94f,.43f,1.13f,.29f,.91f};
    std::array<float,36> geometry{};
    std::copy(vertices.begin(),vertices.end(),geometry.begin());
    std::copy(vertices.begin(),vertices.end(),geometry.begin()+18);
    if(mutation==1)for(int v=0;v<3;v++)std::swap(geometry[18+v*6+4],geometry[18+v*6+5]);
    if(mutation==2)for(int v=0;v<3;v++)geometry[18+v*6]=-geometry[18+v*6];
    VkBuffer vertexBuffer;VkDeviceMemory vertexMemory;
    VkBufferCreateInfo vbi{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};vbi.size=sizeof(geometry);vbi.usage=VK_BUFFER_USAGE_VERTEX_BUFFER_BIT;
    check(vkCreateBuffer(device,&vbi,nullptr,&vertexBuffer),"create vertices");
    VkMemoryRequirements vr{};vkGetBufferMemoryRequirements(device,vertexBuffer,&vr);
    VkMemoryAllocateInfo vma{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};vma.allocationSize=vr.size;
    vma.memoryTypeIndex=memoryType(vr.memoryTypeBits,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    check(vkAllocateMemory(device,&vma,nullptr,&vertexMemory),"allocate vertices");
    check(vkBindBufferMemory(device,vertexBuffer,vertexMemory,0),"bind vertices");
    void* vp=nullptr;check(vkMapMemory(device,vertexMemory,0,vr.size,0,&vp),"map vertices");
    std::memcpy(vp,geometry.data(),sizeof(geometry));vkUnmapMemory(device,vertexMemory);

    std::array<VkDescriptorSetLayoutBinding,4> bindings{};
    for(uint32_t i=0;i<4;i++){
        bindings[i].binding=i;bindings[i].descriptorCount=1;
        bindings[i].descriptorType=i<2?VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:VK_DESCRIPTOR_TYPE_SAMPLER;
        bindings[i].stageFlags=VK_SHADER_STAGE_FRAGMENT_BIT;
    }
    VkDescriptorSetLayoutCreateInfo sl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};sl.bindingCount=4;sl.pBindings=bindings.data();
    VkDescriptorSetLayout setLayout;check(vkCreateDescriptorSetLayout(device,&sl,nullptr,&setLayout),"create descriptor layout");
    VkPipelineLayoutCreateInfo pl{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};pl.setLayoutCount=1;pl.pSetLayouts=&setLayout;
    VkPipelineLayout pipelineLayout;check(vkCreatePipelineLayout(device,&pl,nullptr,&pipelineLayout),"create graphics layout");
    std::array<VkDescriptorPoolSize,2> sizes={VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,4},VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_SAMPLER,4}};
    VkDescriptorPoolCreateInfo dp{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};dp.maxSets=2;dp.poolSizeCount=2;dp.pPoolSizes=sizes.data();
    VkDescriptorPool descriptorPool;check(vkCreateDescriptorPool(device,&dp,nullptr,&descriptorPool),"create descriptor pool");
    std::array<VkDescriptorSetLayout,2> setLayouts={setLayout,setLayout};std::array<VkDescriptorSet,2> sets{};
    VkDescriptorSetAllocateInfo da{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};da.descriptorPool=descriptorPool;da.descriptorSetCount=2;da.pSetLayouts=setLayouts.data();
    check(vkAllocateDescriptorSets(device,&da,sets.data()),"allocate descriptor sets");
    std::array<VkDescriptorImageInfo,8> infos{};std::array<VkWriteDescriptorSet,8> writes{};
    for(int s=0;s<2;s++)for(int b=0;b<4;b++){
        int ix=s*4+b;infos[ix].imageLayout=VK_IMAGE_LAYOUT_GENERAL;
        if(b<2){int image=b;if(s==1&&mutation==4)image=textureCount==1?1:0;infos[ix].imageView=images[image].view;}
        else infos[ix].sampler=sampler;
        writes[ix].sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;writes[ix].dstSet=sets[s];writes[ix].dstBinding=b;
        writes[ix].descriptorCount=1;writes[ix].descriptorType=bindings[b].descriptorType;writes[ix].pImageInfo=&infos[ix];
    }
    vkUpdateDescriptorSets(device,writes.size(),writes.data(),0,nullptr);
    std::array<VkAttachmentDescription,2> attachments{};
    attachments[0].format=VK_FORMAT_R32G32B32A32_SFLOAT;attachments[1].format=VK_FORMAT_D32_SFLOAT;
    for(auto& a:attachments){a.samples=VK_SAMPLE_COUNT_1_BIT;a.loadOp=VK_ATTACHMENT_LOAD_OP_CLEAR;a.storeOp=VK_ATTACHMENT_STORE_OP_STORE;
        a.stencilLoadOp=VK_ATTACHMENT_LOAD_OP_DONT_CARE;a.stencilStoreOp=VK_ATTACHMENT_STORE_OP_DONT_CARE;a.initialLayout=VK_IMAGE_LAYOUT_UNDEFINED;}
    attachments[0].finalLayout=VK_IMAGE_LAYOUT_GENERAL;attachments[1].finalLayout=VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL;
    VkAttachmentReference colorRef{0,VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL},depthRef{1,VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL};
    VkSubpassDescription subpass{};subpass.pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS;
    subpass.colorAttachmentCount=1;subpass.pColorAttachments=&colorRef;subpass.pDepthStencilAttachment=&depthRef;
    std::array<VkSubpassDependency,2> deps{};
    deps[0].srcSubpass=VK_SUBPASS_EXTERNAL;deps[0].dstSubpass=0;
    deps[0].srcStageMask=VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT;
    deps[0].dstStageMask=VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT|VK_PIPELINE_STAGE_EARLY_FRAGMENT_TESTS_BIT;
    deps[0].dstAccessMask=VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT|VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;
    deps[1].srcSubpass=0;deps[1].dstSubpass=VK_SUBPASS_EXTERNAL;
    deps[1].srcStageMask=VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT|VK_PIPELINE_STAGE_EARLY_FRAGMENT_TESTS_BIT|VK_PIPELINE_STAGE_LATE_FRAGMENT_TESTS_BIT;
    deps[1].dstStageMask=VK_PIPELINE_STAGE_TRANSFER_BIT|VK_PIPELINE_STAGE_HOST_BIT;
    deps[1].srcAccessMask=VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT|VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;
    deps[1].dstAccessMask=VK_ACCESS_TRANSFER_READ_BIT|VK_ACCESS_HOST_READ_BIT;
    VkRenderPassCreateInfo rp{VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO};rp.attachmentCount=2;rp.pAttachments=attachments.data();
    rp.subpassCount=1;rp.pSubpasses=&subpass;rp.dependencyCount=2;rp.pDependencies=deps.data();
    VkRenderPass renderPass;check(vkCreateRenderPass(device,&rp,nullptr,&renderPass),"create render pass");
    std::array<VkFramebuffer,2> framebuffers{};
    for(int i=0;i<2;i++){
        std::array<VkImageView,2> views={images[2+i].view,depths[i].view};
        VkFramebufferCreateInfo fi{VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO};fi.renderPass=renderPass;fi.attachmentCount=2;fi.pAttachments=views.data();fi.width=w;fi.height=h;fi.layers=1;
        check(vkCreateFramebuffer(device,&fi,nullptr,&framebuffers[i]),"create framebuffer");
    }
    std::array<VkShaderModule,4> modules{};std::array<VkPipeline,2> pipelines{};
    for(int i=0;i<4;i++){VkShaderModuleCreateInfo sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};sm.codeSize=binaries[i].size()*4;sm.pCode=binaries[i].data();
        check(vkCreateShaderModule(device,&sm,nullptr,&modules[i]),"create graphics shader");}
    for(int i=0;i<2;i++){
        std::array<VkPipelineShaderStageCreateInfo,2> stages{};
        for(int j=0;j<2;j++){stages[j].sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;stages[j].stage=j?VK_SHADER_STAGE_FRAGMENT_BIT:VK_SHADER_STAGE_VERTEX_BIT;
            stages[j].module=modules[i*2+j];stages[j].pName="main";}
        VkVertexInputBindingDescription vb{0,6*sizeof(float),VK_VERTEX_INPUT_RATE_VERTEX};
        std::array<VkVertexInputAttributeDescription,2> va={VkVertexInputAttributeDescription{0,0,VK_FORMAT_R32G32B32A32_SFLOAT,0},VkVertexInputAttributeDescription{1,0,VK_FORMAT_R32G32_SFLOAT,4*sizeof(float)}};
        VkPipelineVertexInputStateCreateInfo vi{VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};vi.vertexBindingDescriptionCount=1;vi.pVertexBindingDescriptions=&vb;vi.vertexAttributeDescriptionCount=2;vi.pVertexAttributeDescriptions=va.data();
        VkPipelineInputAssemblyStateCreateInfo ia{VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};ia.topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
        VkViewport viewport{0,0,float(w),float(h),0,1};VkRect2D scissor{{0,0},{w,h}};
        VkPipelineViewportStateCreateInfo vs{VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};vs.viewportCount=1;vs.pViewports=&viewport;vs.scissorCount=1;vs.pScissors=&scissor;
        VkPipelineRasterizationStateCreateInfo rs{VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};rs.polygonMode=VK_POLYGON_MODE_FILL;rs.cullMode=VK_CULL_MODE_NONE;rs.frontFace=VK_FRONT_FACE_COUNTER_CLOCKWISE;rs.lineWidth=1;rs.depthClampEnable=!zclip;
        VkPipelineMultisampleStateCreateInfo ms{VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};ms.rasterizationSamples=VK_SAMPLE_COUNT_1_BIT;
        const std::array<VkCompareOp,9> comparisons={VK_COMPARE_OP_LESS_OR_EQUAL,VK_COMPARE_OP_NEVER,VK_COMPARE_OP_LESS,VK_COMPARE_OP_EQUAL,VK_COMPARE_OP_LESS_OR_EQUAL,VK_COMPARE_OP_GREATER,VK_COMPARE_OP_NOT_EQUAL,VK_COMPARE_OP_GREATER_OR_EQUAL,VK_COMPARE_OP_ALWAYS};
        VkPipelineDepthStencilStateCreateInfo ds{VK_STRUCTURE_TYPE_PIPELINE_DEPTH_STENCIL_STATE_CREATE_INFO};ds.depthTestEnable=VK_TRUE;ds.depthWriteEnable=zwrite;ds.depthCompareOp=(i==1&&mutation==3)?VK_COMPARE_OP_NEVER:comparisons[ztest];
        VkPipelineColorBlendAttachmentState cb{};cb.colorWriteMask=mask;cb.blendEnable=VK_FALSE;
        VkPipelineColorBlendStateCreateInfo bs{VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};bs.attachmentCount=1;bs.pAttachments=&cb;
        VkGraphicsPipelineCreateInfo gp{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};gp.stageCount=2;gp.pStages=stages.data();gp.pVertexInputState=&vi;gp.pInputAssemblyState=&ia;gp.pViewportState=&vs;gp.pRasterizationState=&rs;gp.pMultisampleState=&ms;gp.pDepthStencilState=&ds;gp.pColorBlendState=&bs;gp.layout=pipelineLayout;gp.renderPass=renderPass;
        check(vkCreateGraphicsPipelines(device,VK_NULL_HANDLE,1,&gp,nullptr,&pipelines[i]),"create graphics pipeline");
    }
    VkCommandPoolCreateInfo cp{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};cp.queueFamilyIndex=family;VkCommandPool commandPool;
    check(vkCreateCommandPool(device,&cp,nullptr,&commandPool),"create graphics commands");
    VkCommandBufferAllocateInfo ca{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};ca.commandPool=commandPool;ca.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;ca.commandBufferCount=1;
    VkCommandBuffer cmd;check(vkAllocateCommandBuffers(device,&ca,&cmd),"allocate graphics commands");
    VkCommandBufferBeginInfo begin{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};check(vkBeginCommandBuffer(cmd,&begin),"begin graphics commands");
    std::array<VkImageMemoryBarrier,2> inputBarriers{};
    for(int i=0;i<2;i++){auto& b=inputBarriers[i];b.sType=VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;b.srcAccessMask=VK_ACCESS_HOST_WRITE_BIT;b.dstAccessMask=VK_ACCESS_SHADER_READ_BIT;b.oldLayout=VK_IMAGE_LAYOUT_PREINITIALIZED;b.newLayout=VK_IMAGE_LAYOUT_GENERAL;b.srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.image=images[i].image;b.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};}
    vkCmdPipelineBarrier(cmd,VK_PIPELINE_STAGE_HOST_BIT,VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT,0,0,nullptr,0,nullptr,2,inputBarriers.data());
    for(int i=0;i<2;i++){
        std::array<VkClearValue,2> clear{};clear[0].color={{-2.f,-3.f,-4.f,-5.f}};clear[1].depthStencil={clearDepth,0};
        VkRenderPassBeginInfo rb{VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO};rb.renderPass=renderPass;rb.framebuffer=framebuffers[i];rb.renderArea={{0,0},{w,h}};rb.clearValueCount=2;rb.pClearValues=clear.data();
        vkCmdBeginRenderPass(cmd,&rb,VK_SUBPASS_CONTENTS_INLINE);vkCmdBindPipeline(cmd,VK_PIPELINE_BIND_POINT_GRAPHICS,pipelines[i]);
        vkCmdBindDescriptorSets(cmd,VK_PIPELINE_BIND_POINT_GRAPHICS,pipelineLayout,0,1,&sets[i],0,nullptr);
        VkDeviceSize offset=i*18*sizeof(float);vkCmdBindVertexBuffers(cmd,0,1,&vertexBuffer,&offset);vkCmdDraw(cmd,3,1,0,0);vkCmdEndRenderPass(cmd);
        VkBufferImageCopy copy{};copy.imageSubresource={VK_IMAGE_ASPECT_DEPTH_BIT,0,0,1};copy.imageExtent={w,h,1};
        vkCmdCopyImageToBuffer(cmd,depths[i].image,VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,depths[i].readback,1,&copy);
    }
    std::array<VkBufferMemoryBarrier,2> hostBarriers{};
    for(int i=0;i<2;i++){auto& b=hostBarriers[i];b.sType=VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER;b.srcAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT;b.dstAccessMask=VK_ACCESS_HOST_READ_BIT;b.srcQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;b.buffer=depths[i].readback;b.size=VK_WHOLE_SIZE;}
    vkCmdPipelineBarrier(cmd,VK_PIPELINE_STAGE_TRANSFER_BIT,VK_PIPELINE_STAGE_HOST_BIT,0,0,nullptr,2,hostBarriers.data(),0,nullptr);
    check(vkEndCommandBuffer(cmd),"end graphics commands");
    VkSubmitInfo submit{VK_STRUCTURE_TYPE_SUBMIT_INFO};submit.commandBufferCount=1;submit.pCommandBuffers=&cmd;
    check(vkQueueSubmit(queue,1,&submit,VK_NULL_HANDLE),"submit graphics");check(vkQueueWaitIdle(queue),"wait graphics");
    uint64_t changedA=0,changedB=0,coverageMismatch=0,nonfinite=0,canaryErrors=0;
    double maxColor=0,maxDepth=0;
    for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++){
        auto a=pixel(images[2],x,y),b=pixel(images[3],x,y);
        float da=depths[0].mapped[y*w+x],db=depths[1].mapped[y*w+x];
        auto changed=[&](const std::array<float,4>& p,float depth){return p!=std::array<float,4>{-2,-3,-4,-5}||depth!=clearDepth;};
        bool wa=changed(a,da),wb=changed(b,db);changedA+=wa;changedB+=wb;coverageMismatch+=(wa!=wb);
        for(int c=0;c<4;c++){if(!std::isfinite(a[c])||!std::isfinite(b[c]))nonfinite++;
            else maxColor=std::max(maxColor,std::abs(double(a[c])-double(b[c])));}
        if(!std::isfinite(da)||!std::isfinite(db))nonfinite++;else maxDepth=std::max(maxDepth,std::abs(double(da)-double(db)));
        if(canary&&wa){const std::array<float,4> want={.2f,.4f,.6f,.8f};for(int c=0;c<4;c++)if(std::abs(a[c]-want[c])>1e-6f)canaryErrors++;if(std::abs(da-.25f)>1e-6f)canaryErrors++;}
        if(canary&&wb){const std::array<float,4> want={.2f,.4f,.6f,.8f};for(int c=0;c<4;c++)if(std::abs(b[c]-want[c])>1e-6f)canaryErrors++;if(std::abs(db-.25f)>1e-6f)canaryErrors++;}
    }
    require(changedA>0,"Original graphics produced no observable writes");
    if(mutation==0)require(changedB>0,"Rebuilt graphics produced no observable writes");
    if(canary)require(canaryErrors==0&&changedB>0,"Known raster color/depth canary disagrees");
    require(validationErrors.load()==0,"Vulkan API or synchronization validation errors detected");
    bool match=coverageMismatch==0&&nonfinite==0&&maxColor<=1e-4&&maxDepth<=1e-6;
    std::cout<<std::setprecision(12)<<"RAFT_W1_RASTER_DIFF {\"cpu_vulkan\":true,\"width\":"<<w<<",\"height\":"<<h
        <<",\"changed_original_pixels\":"<<changedA<<",\"changed_rebuilt_pixels\":"<<changedB<<",\"coverage_mismatch_pixels\":"<<coverageMismatch
        <<",\"nonfinite_components\":"<<nonfinite<<",\"max_color_abs\":"<<maxColor<<",\"max_depth_abs\":"<<maxDepth
        <<",\"within_tolerance\":"<<(match?"true":"false")<<",\"known_color_depth_canary\":"<<(canary?"true":"false")
        <<",\"vulkan_validation_errors\":"<<validationErrors.load()<<",\"vulkan_validation_warnings\":"<<validationWarnings.load()<<",\"synchronization_validation_enabled\":true"
        <<",\"mutation\":"<<mutation<<",\"android_or_unity_render\":false}\n";
    check(vkDeviceWaitIdle(device),"device wait idle");
    vkDestroyCommandPool(device,commandPool,nullptr);
    for(int i=0;i<2;i++){vkDestroyPipeline(device,pipelines[i],nullptr);vkDestroyFramebuffer(device,framebuffers[i],nullptr);
        vkUnmapMemory(device,depths[i].host);vkDestroyBuffer(device,depths[i].readback,nullptr);vkFreeMemory(device,depths[i].host,nullptr);
        vkDestroyImageView(device,depths[i].view,nullptr);vkDestroyImage(device,depths[i].image,nullptr);vkFreeMemory(device,depths[i].memory,nullptr);}
    for(auto m:modules)vkDestroyShaderModule(device,m,nullptr);
    vkDestroyRenderPass(device,renderPass,nullptr);vkDestroyDescriptorPool(device,descriptorPool,nullptr);vkDestroyPipelineLayout(device,pipelineLayout,nullptr);vkDestroyDescriptorSetLayout(device,setLayout,nullptr);
    vkDestroyBuffer(device,vertexBuffer,nullptr);vkFreeMemory(device,vertexMemory,nullptr);
    vkDestroySampler(device,sampler,nullptr);
    for(auto& t:images){vkUnmapMemory(device,t.memory);vkDestroyImageView(device,t.view,nullptr);vkDestroyImage(device,t.image,nullptr);vkFreeMemory(device,t.memory,nullptr);}
    vkDestroyDevice(device,nullptr);destroyDebug(instance,messenger,nullptr);vkDestroyInstance(instance,nullptr);
    require(validationErrors.load()==0,"Vulkan cleanup validation errors detected");return 0;
 }catch(const std::exception& e){std::cerr<<"RAFT_W1_RASTER_ERROR "<<e.what()<<"\n";return 2;}
}

