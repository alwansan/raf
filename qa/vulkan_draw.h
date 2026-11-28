/* Included only by the independent shader-draw variant. */
#include "probe_spirv.h"
typedef struct {
    VkImageView view;
    VkRenderPass pass;
    VkFramebuffer framebuffer;
    VkShaderModule vertex, fragment;
    VkPipelineLayout layout;
    VkPipeline pipeline;
} ProbeDraw;

static int create_draw(VkDevice device, VkImage image, uint32_t w, uint32_t h, ProbeDraw *d) {
    VkImageViewCreateInfo vi = {
        .sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
        .image = image, .viewType = VK_IMAGE_VIEW_TYPE_2D,
        .format = VK_FORMAT_R8G8B8A8_UNORM,
        .subresourceRange = { .aspectMask = VK_IMAGE_ASPECT_COLOR_BIT,
                              .levelCount = 1, .layerCount = 1 }
    };
    VK(vkCreateImageView(device, &vi, NULL, &d->view));
    VkAttachmentDescription attachment = {
        .format = VK_FORMAT_R8G8B8A8_UNORM, .samples = VK_SAMPLE_COUNT_1_BIT,
        .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR, .storeOp = VK_ATTACHMENT_STORE_OP_STORE,
        .stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
        .stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
        .initialLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
        .finalLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
    };
    VkAttachmentReference ref = { .attachment = 0, .layout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL };
    VkSubpassDescription subpass = {
        .pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS,
        .colorAttachmentCount = 1, .pColorAttachments = &ref
    };
    VkRenderPassCreateInfo ri = {
        .sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO, .attachmentCount = 1,
        .pAttachments = &attachment, .subpassCount = 1, .pSubpasses = &subpass
    };
    VK(vkCreateRenderPass(device, &ri, NULL, &d->pass));
    VkFramebufferCreateInfo fi = {
        .sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO, .renderPass = d->pass,
        .attachmentCount = 1, .pAttachments = &d->view, .width = w, .height = h, .layers = 1
    };
    VK(vkCreateFramebuffer(device, &fi, NULL, &d->framebuffer));
    VkShaderModuleCreateInfo sm = { .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        .codeSize = sizeof(probe_vertex_spv), .pCode = probe_vertex_spv };
    VK(vkCreateShaderModule(device, &sm, NULL, &d->vertex));
    sm.codeSize = sizeof(probe_fragment_spv);
    sm.pCode = probe_fragment_spv;
    VK(vkCreateShaderModule(device, &sm, NULL, &d->fragment));
    VkPushConstantRange push = { .stageFlags = VK_SHADER_STAGE_FRAGMENT_BIT, .size = 16 };
    VkPipelineLayoutCreateInfo li = { .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .pushConstantRangeCount = 1, .pPushConstantRanges = &push };
    VK(vkCreatePipelineLayout(device, &li, NULL, &d->layout));
    VkPipelineShaderStageCreateInfo stages[2] = {
        { .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
          .stage = VK_SHADER_STAGE_VERTEX_BIT, .module = d->vertex, .pName = "main" },
        { .sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
          .stage = VK_SHADER_STAGE_FRAGMENT_BIT, .module = d->fragment, .pName = "main" }
    };
    VkPipelineVertexInputStateCreateInfo vertex = { .sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO };
    VkPipelineInputAssemblyStateCreateInfo ia = {
        .sType = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
        .topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST
    };
    VkViewport viewport = { .width = (float)w, .height = (float)h, .maxDepth = 1.0f };
    VkRect2D scissor = { .extent = { w, h } };
    VkPipelineViewportStateCreateInfo vs = { .sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
        .viewportCount = 1, .pViewports = &viewport, .scissorCount = 1, .pScissors = &scissor };
    VkPipelineRasterizationStateCreateInfo rs = { .sType = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
        .polygonMode = VK_POLYGON_MODE_FILL, .cullMode = VK_CULL_MODE_NONE,
        .frontFace = VK_FRONT_FACE_COUNTER_CLOCKWISE, .lineWidth = 1.0f };
    VkPipelineMultisampleStateCreateInfo ms = { .sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
        .rasterizationSamples = VK_SAMPLE_COUNT_1_BIT };
    VkPipelineColorBlendAttachmentState blend = {
        .colorWriteMask = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT |
                          VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT
    };
    VkPipelineColorBlendStateCreateInfo bs = { .sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
        .attachmentCount = 1, .pAttachments = &blend };
    VkGraphicsPipelineCreateInfo gp = { .sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
        .stageCount = 2, .pStages = stages, .pVertexInputState = &vertex, .pInputAssemblyState = &ia,
        .pViewportState = &vs, .pRasterizationState = &rs, .pMultisampleState = &ms,
        .pColorBlendState = &bs, .layout = d->layout, .renderPass = d->pass, .basePipelineIndex = -1 };
    VK(vkCreateGraphicsPipelines(device, VK_NULL_HANDLE, 1, &gp, NULL, &d->pipeline));
    return 0;
}
static void record_draw(VkCommandBuffer cb, const ProbeDraw *d, uint32_t w, uint32_t h,
                        const float *color) {
    /* A null-color frame omits vkCmdDraw and must remain blue. */
    VkClearValue clear = { .color = { .float32 = { 0, 0, 1, 1 } } };
    VkRenderPassBeginInfo begin = { .sType = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
        .renderPass = d->pass, .framebuffer = d->framebuffer,
        .renderArea = { .extent = { w, h } }, .clearValueCount = 1, .pClearValues = &clear };
    vkCmdBeginRenderPass(cb, &begin, VK_SUBPASS_CONTENTS_INLINE);
    if (color) {
        vkCmdBindPipeline(cb, VK_PIPELINE_BIND_POINT_GRAPHICS, d->pipeline);
        vkCmdPushConstants(cb, d->layout, VK_SHADER_STAGE_FRAGMENT_BIT, 0, 16, color);
        vkCmdDraw(cb, 3, 1, 0, 0);
    }
    vkCmdEndRenderPass(cb);
}
static void destroy_draw(VkDevice device, const ProbeDraw *d) {
    vkDestroyPipeline(device, d->pipeline, NULL);
    vkDestroyPipelineLayout(device, d->layout, NULL);
    vkDestroyShaderModule(device, d->fragment, NULL);
    vkDestroyShaderModule(device, d->vertex, NULL);
    vkDestroyFramebuffer(device, d->framebuffer, NULL);
    vkDestroyRenderPass(device, d->pass, NULL);
    vkDestroyImageView(device, d->view, NULL);
}
