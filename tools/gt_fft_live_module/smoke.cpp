// Authored, source-free loader-layer control. No game inputs or shaders.
#include <vulkan/vulkan.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
static void checkpoint(const char* phase){std::cerr<<"GT_FFT_AUTHORED_SMOKE "<<phase<<std::endl;}
static void need(bool value){if(!value)throw std::runtime_error("smoke check failed");}
static void check(VkResult result){if(result!=VK_SUCCESS)throw std::runtime_error("smoke Vulkan result "+std::to_string(result));}
int main(){
 try{
    VkApplicationInfo app{VK_STRUCTURE_TYPE_APPLICATION_INFO};app.apiVersion=VK_API_VERSION_1_1;
    VkInstanceCreateInfo ic{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};ic.pApplicationInfo=&app;
    checkpoint("before_create_instance");VkInstance instance{};check(vkCreateInstance(&ic,nullptr,&instance));checkpoint("after_create_instance");
    checkpoint("before_enumerate_physical");uint32_t count=0;check(vkEnumeratePhysicalDevices(instance,&count,nullptr));need(count>0);
    std::vector<VkPhysicalDevice> devices(count);check(vkEnumeratePhysicalDevices(instance,&count,devices.data()));
    VkPhysicalDevice physical{};for(auto d:devices){VkPhysicalDeviceProperties p{};vkGetPhysicalDeviceProperties(d,&p);if(p.deviceType==VK_PHYSICAL_DEVICE_TYPE_CPU){physical=d;break;}}need(physical!=VK_NULL_HANDLE);
    uint32_t qc=0;vkGetPhysicalDeviceQueueFamilyProperties(physical,&qc,nullptr);need(qc>0);
    std::vector<VkQueueFamilyProperties> queues(qc);vkGetPhysicalDeviceQueueFamilyProperties(physical,&qc,queues.data());
    uint32_t family=qc;for(uint32_t i=0;i<qc;i++)if(queues[i].queueFlags&VK_QUEUE_COMPUTE_BIT){family=i;break;}need(family<qc);
    float priority=1.0f;VkDeviceQueueCreateInfo qi{VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};qi.queueFamilyIndex=family;qi.queueCount=1;qi.pQueuePriorities=&priority;
    VkDeviceCreateInfo dc{VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};dc.queueCreateInfoCount=1;dc.pQueueCreateInfos=&qi;
    checkpoint("before_create_device");VkDevice device{};check(vkCreateDevice(physical,&dc,nullptr,&device));checkpoint("after_create_device");
    VkQueue queue{};vkGetDeviceQueue(device,family,0,&queue);
    std::ifstream file("/opt/gt-fft-layer/smoke.spv",std::ios::binary|std::ios::ate);
    auto size=file.tellg();need(file.good()&&size>=20&&size<=1048576&&size%4==0);
    std::vector<uint32_t> words(static_cast<size_t>(size)/4);file.seekg(0);file.read(reinterpret_cast<char*>(words.data()),size);need(file.good()&&words[0]==0x07230203);
    VkShaderModuleCreateInfo sc{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};sc.codeSize=words.size()*4;sc.pCode=words.data();
    checkpoint("before_create_shader");VkShaderModule module{};check(vkCreateShaderModule(device,&sc,nullptr,&module));checkpoint("after_create_shader");
    VkPipelineLayoutCreateInfo lc{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};VkPipelineLayout layout{};check(vkCreatePipelineLayout(device,&lc,nullptr,&layout));
    VkComputePipelineCreateInfo pc{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
    pc.stage.sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;pc.stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;pc.stage.module=module;pc.stage.pName="main";pc.layout=layout;
    checkpoint("before_create_pipeline");VkPipeline pipeline{};check(vkCreateComputePipelines(device,VK_NULL_HANDLE,1,&pc,nullptr,&pipeline));checkpoint("after_create_pipeline");
    vkDestroyShaderModule(device,module,nullptr);
    VkCommandPoolCreateInfo cc{VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};cc.queueFamilyIndex=family;
    VkCommandPool pool{};check(vkCreateCommandPool(device,&cc,nullptr,&pool));
    VkCommandBufferAllocateInfo ac{VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};ac.commandPool=pool;ac.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY;ac.commandBufferCount=1;
    VkCommandBuffer command{};check(vkAllocateCommandBuffers(device,&ac,&command));
    checkpoint("before_begin_command");VkCommandBufferBeginInfo begin{VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};check(vkBeginCommandBuffer(command,&begin));
    checkpoint("before_bind_pipeline");vkCmdBindPipeline(command,VK_PIPELINE_BIND_POINT_COMPUTE,pipeline);checkpoint("before_dispatch");vkCmdDispatch(command,64,64,1);checkpoint("after_dispatch");check(vkEndCommandBuffer(command));
    checkpoint("before_submit");VkSubmitInfo sub{VK_STRUCTURE_TYPE_SUBMIT_INFO};sub.commandBufferCount=1;sub.pCommandBuffers=&command;check(vkQueueSubmit(queue,1,&sub,VK_NULL_HANDLE));check(vkQueueWaitIdle(queue));
    checkpoint("after_queue_idle");vkFreeCommandBuffers(device,pool,1,&command);vkDestroyCommandPool(device,pool,nullptr);vkDestroyPipeline(device,pipeline,nullptr);vkDestroyPipelineLayout(device,layout,nullptr);vkDestroyDevice(device,nullptr);vkDestroyInstance(instance,nullptr);
    checkpoint("complete");return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
