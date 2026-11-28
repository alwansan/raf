/* Original synthetic Android Vulkan transfer/readback probe; no game inputs. */
#include <vulkan/vulkan.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef RAFT_ANDROID_JNI_LOG
#include <android/log.h>
/* Preserve the exact readback messages inside an Android app process. */
#define printf(...) __android_log_print(ANDROID_LOG_INFO, "RaftQaArmVk", __VA_ARGS__)
#define fprintf(stream, ...) __android_log_print(ANDROID_LOG_ERROR, "RaftQaArmVk", __VA_ARGS__)
#define puts(message) __android_log_print(ANDROID_LOG_INFO, "RaftQaArmVk", "%s", message)
#endif

#define VK(call) do { VkResult r = (call); if (r != VK_SUCCESS) { \
    fprintf(stderr, "%s failed: %d\n", #call, (int)r); return 1; } } while (0)
#define REQUIRE(test) do { if (!(test)) { fprintf(stderr, "Failed: %s\n", #test); return 1; } } while (0)

static uint32_t memory_type(const VkPhysicalDeviceMemoryProperties *p,
                            uint32_t mask, VkMemoryPropertyFlags required) {
    for (uint32_t i = 0; i < p->memoryTypeCount; ++i)
        if ((mask & (1u << i)) && (p->memoryTypes[i].propertyFlags & required) == required)
            return i;
    return UINT32_MAX;
}

static void image_barrier(VkCommandBuffer cb, VkImage image,
                          VkImageLayout old_layout, VkImageLayout new_layout,
                          VkAccessFlags src, VkAccessFlags dst,
                          VkPipelineStageFlags from, VkPipelineStageFlags to) {
    VkImageMemoryBarrier b = {
        .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER,
        .srcAccessMask = src, .dstAccessMask = dst,
        .oldLayout = old_layout, .newLayout = new_layout,
        .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .image = image,
        .subresourceRange = { .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                               .levelCount = 1, .layerCount = 1 }
    };
    vkCmdPipelineBarrier(cb, from, to, 0, 0, NULL, 0, NULL, 1, &b);
}

#ifdef RAFT_SHADER_DRAW
#include "vulkan_draw.h"
#endif

#ifdef RAFT_ANDROID_JNI_LOG
int raft_vulkan_probe_main(void) {
#else
int main(void) {
    setvbuf(stdout, NULL, _IOLBF, 0);
#endif
    VkApplicationInfo app = { .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
        .pApplicationName = "RAFT synthetic Vulkan probe", .apiVersion = VK_API_VERSION_1_0 };
    VkInstanceCreateInfo ic = { .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
        .pApplicationInfo = &app };
    VkInstance instance;
    VK(vkCreateInstance(&ic, NULL, &instance));

    uint32_t count = 0;
    VK(vkEnumeratePhysicalDevices(instance, &count, NULL));
    REQUIRE(count > 0);
    VkPhysicalDevice *devices = calloc(count, sizeof(*devices));
    REQUIRE(devices != NULL);
    VK(vkEnumeratePhysicalDevices(instance, &count, devices));
    VkPhysicalDevice physical = VK_NULL_HANDLE;
    uint32_t family = UINT32_MAX;
    for (uint32_t d = 0; d < count && family == UINT32_MAX; ++d) {
        uint32_t n = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(devices[d], &n, NULL);
        if (!n) continue;
        VkQueueFamilyProperties *q = calloc(n, sizeof(*q));
        REQUIRE(q != NULL);
        vkGetPhysicalDeviceQueueFamilyProperties(devices[d], &n, q);
        for (uint32_t j = 0; j < n; ++j) {
            if (q[j].queueCount && (q[j].queueFlags & VK_QUEUE_GRAPHICS_BIT)) {
                physical = devices[d]; family = j; break;
            }
        }
        free(q);
    }
    free(devices);
    REQUIRE(physical != VK_NULL_HANDLE && family != UINT32_MAX);
    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(physical, &props);
    printf("VK_DEVICE=%s type=%u vendor=%04x device=%04x api=%u.%u.%u driver=%u queue=%u\n",
           props.deviceName, (unsigned)props.deviceType, props.vendorID, props.deviceID,
           VK_VERSION_MAJOR(props.apiVersion), VK_VERSION_MINOR(props.apiVersion),
           VK_VERSION_PATCH(props.apiVersion), props.driverVersion, family);
    float priority = 1.0f;
    VkDeviceQueueCreateInfo qc = { .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
        .queueFamilyIndex = family, .queueCount = 1, .pQueuePriorities = &priority };
    VkDeviceCreateInfo dc = { .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
        .queueCreateInfoCount = 1, .pQueueCreateInfos = &qc };
    VkDevice device;
    VK(vkCreateDevice(physical, &dc, NULL, &device));
    VkQueue queue;
    vkGetDeviceQueue(device, family, 0, &queue);
    VkPhysicalDeviceMemoryProperties mp;
    vkGetPhysicalDeviceMemoryProperties(physical, &mp);

#ifdef RAFT_SHADER_DRAW
    enum { FRAMES = 3 };
#else
    enum { FRAMES = 2 };
#endif
    enum { W = 4, H = 4, FRAME = W * H * 4, SIZE = FRAMES * FRAME };
    VkImageCreateInfo ii = { .sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,
        .imageType = VK_IMAGE_TYPE_2D, .format = VK_FORMAT_R8G8B8A8_UNORM,
        .extent = {W, H, 1}, .mipLevels = 1, .arrayLayers = 1,
        .samples = VK_SAMPLE_COUNT_1_BIT, .tiling = VK_IMAGE_TILING_OPTIMAL,
        .usage = VK_IMAGE_USAGE_TRANSFER_SRC_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT
#ifdef RAFT_SHADER_DRAW
            | VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT
#endif
        ,
        .sharingMode = VK_SHARING_MODE_EXCLUSIVE, .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED };
    VkImage image;
    VK(vkCreateImage(device, &ii, NULL, &image));
    VkMemoryRequirements ir;
    vkGetImageMemoryRequirements(device, image, &ir);
    uint32_t it = memory_type(&mp, ir.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
    if (it == UINT32_MAX) it = memory_type(&mp, ir.memoryTypeBits, 0);
    REQUIRE(it != UINT32_MAX);
    VkMemoryAllocateInfo ia = { .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
        .allocationSize = ir.size, .memoryTypeIndex = it };
    VkDeviceMemory im;
    VK(vkAllocateMemory(device, &ia, NULL, &im));
    VK(vkBindImageMemory(device, image, im, 0));
#ifdef RAFT_SHADER_DRAW
    ProbeDraw draw = {0};
    REQUIRE(create_draw(device, image, W, H, &draw) == 0);
#endif

    VkBufferCreateInfo bi = { .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
        .size = SIZE, .usage = VK_BUFFER_USAGE_TRANSFER_DST_BIT,
        .sharingMode = VK_SHARING_MODE_EXCLUSIVE };
    VkBuffer buffer;
    VK(vkCreateBuffer(device, &bi, NULL, &buffer));
    VkMemoryRequirements br;
    vkGetBufferMemoryRequirements(device, buffer, &br);
    uint32_t bt = memory_type(&mp, br.memoryTypeBits,
        VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
    if (bt == UINT32_MAX) bt = memory_type(&mp, br.memoryTypeBits, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT);
    REQUIRE(bt != UINT32_MAX);
    VkMemoryAllocateInfo ba = { .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
        .allocationSize = br.size, .memoryTypeIndex = bt };
    VkDeviceMemory bm;
    VK(vkAllocateMemory(device, &ba, NULL, &bm));
    VK(vkBindBufferMemory(device, buffer, bm, 0));

    VkCommandPoolCreateInfo pi = { .sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
        .queueFamilyIndex = family };
    VkCommandPool pool;
    VK(vkCreateCommandPool(device, &pi, NULL, &pool));
    VkCommandBufferAllocateInfo ca = { .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
        .commandPool = pool, .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY, .commandBufferCount = 1 };
    VkCommandBuffer cb;
    VK(vkAllocateCommandBuffers(device, &ca, &cb));
    VkCommandBufferBeginInfo begin = { .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
        .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT };
    VK(vkBeginCommandBuffer(cb, &begin));

    const VkClearColorValue colors[2] = { { .float32 = {1,0,0,1} }, { .float32 = {0,1,0,1} } };
#ifndef RAFT_SHADER_DRAW
    VkImageSubresourceRange range = { .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
        .levelCount = 1, .layerCount = 1 };
#endif
    for (uint32_t i = 0; i < FRAMES; ++i) {
#ifdef RAFT_SHADER_DRAW
        image_barrier(cb, image,
            i ? VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL : VK_IMAGE_LAYOUT_UNDEFINED,
            VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
            i ? VK_ACCESS_TRANSFER_READ_BIT : 0, VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
            i ? VK_PIPELINE_STAGE_TRANSFER_BIT : VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
            VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT);
        record_draw(cb, &draw, W, H, i < 2 ? colors[i].float32 : NULL);
        image_barrier(cb, image, VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
            VK_ACCESS_TRANSFER_READ_BIT, VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            VK_PIPELINE_STAGE_TRANSFER_BIT);
#else
        image_barrier(cb, image,
            i ? VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL : VK_IMAGE_LAYOUT_UNDEFINED,
            VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
            i ? VK_ACCESS_TRANSFER_READ_BIT : 0, VK_ACCESS_TRANSFER_WRITE_BIT,
            i ? VK_PIPELINE_STAGE_TRANSFER_BIT : VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,
            VK_PIPELINE_STAGE_TRANSFER_BIT);
        vkCmdClearColorImage(cb, image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, &colors[i], 1, &range);
        image_barrier(cb, image, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,
            VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_ACCESS_TRANSFER_WRITE_BIT,
            VK_ACCESS_TRANSFER_READ_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT);
#endif
        VkBufferImageCopy copy = { .bufferOffset = i * FRAME,
            .imageSubresource = { .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT, .layerCount = 1 },
            .imageExtent = { W, H, 1 } };
        vkCmdCopyImageToBuffer(cb, image, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, buffer, 1, &copy);
    }
    VkBufferMemoryBarrier barrier = { .sType = VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER,
        .srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT, .dstAccessMask = VK_ACCESS_HOST_READ_BIT,
        .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED, .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .buffer = buffer, .size = VK_WHOLE_SIZE };
    vkCmdPipelineBarrier(cb, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_HOST_BIT,
        0, 0, NULL, 1, &barrier, 0, NULL);
    VK(vkEndCommandBuffer(cb));

    VkFenceCreateInfo fi = { .sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO };
    VkFence fence;
    VK(vkCreateFence(device, &fi, NULL, &fence));
    VkSubmitInfo submit = { .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO,
        .commandBufferCount = 1, .pCommandBuffers = &cb };
    VK(vkQueueSubmit(queue, 1, &submit, fence));
    VK(vkWaitForFences(device, 1, &fence, VK_TRUE, UINT64_C(20000000000)));
    void *mapped = NULL;
    VK(vkMapMemory(device, bm, 0, VK_WHOLE_SIZE, 0, &mapped));
    if (!(mp.memoryTypes[bt].propertyFlags & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) {
        VkMappedMemoryRange mr = { .sType = VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE,
            .memory = bm, .offset = 0, .size = VK_WHOLE_SIZE };
        VK(vkInvalidateMappedMemoryRanges(device, 1, &mr));
    }
    const uint8_t expect[3][4] = {{255,0,0,255}, {0,255,0,255}, {0,0,255,255}};
    const uint8_t *bytes = mapped;
    for (uint32_t i = 0; i < FRAMES; ++i) {
        const uint8_t *p = bytes + i * FRAME;
        printf("VK_FRAME_%u_FIRST_RGBA=%u,%u,%u,%u\n", i, p[0], p[1], p[2], p[3]);
        for (uint32_t j = 0; j < W*H; ++j) {
            if (memcmp(p + j*4, expect[i], 4) != 0) {
                fprintf(stderr, "Unexpected frame %u pixel %u: %u,%u,%u,%u\n",
                    i, j, p[j*4], p[j*4+1], p[j*4+2], p[j*4+3]);
                return 1;
            }
        }
    }
    vkUnmapMemory(device, bm);
    vkDestroyFence(device, fence, NULL);
    vkDestroyCommandPool(device, pool, NULL);
    vkDestroyBuffer(device, buffer, NULL);
    vkFreeMemory(device, bm, NULL);
#ifdef RAFT_SHADER_DRAW
    destroy_draw(device, &draw);
#endif
    vkDestroyImage(device, image, NULL);
    vkFreeMemory(device, im, NULL);
    vkDestroyDevice(device, NULL);
    vkDestroyInstance(instance, NULL);
#ifdef RAFT_SHADER_DRAW
    puts("VK_SHADER_DRAW_PASS pixels=32 negative_control=16");
#endif
    puts("VULKAN_TRANSFER_READBACK_PASS pixels=32");
    return 0;
}
