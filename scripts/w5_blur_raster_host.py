"""Generate W5's bounded UBO extension of the unchanged W1 CPU raster host.

The public, authored host template is SHA-pinned. Generated C++ contains no game
source. Keep W1's validation/canary/readback machinery, adding independent real
vertex and fragment UBO allocations, non-symmetric matrices and fault controls.
"""
import argparse
import hashlib
from pathlib import Path

HOST_SHA256 = "a66534982059019331b99ae34cad3d8f8e355897b5fcade24b44f615f69a16a6"

UNIFORMS = r'''
    struct Uniform { VkBuffer buffer; VkDeviceMemory memory; };
    std::array<Uniform,6> uniforms{};
    std::array<VkDescriptorBufferInfo,6> uniformInfos{};
    std::array<VkWriteDescriptorSet,6> uniformWrites{};
    const std::array<uint32_t,3> uniformBytes={176,368,80};
    for(int s=0;s<2;s++)for(int b=0;b<3;b++) {
        const int index=s*3+b;
        auto& u=uniforms[index];
        std::vector<float> values(uniformBytes[b]/4);
        for(size_t k=0;k<values.size();k++)values[k]=0.013f*float(1+(k*7+inputSeed)%23);
        if(b<2) {
            const int start=b==0?0:68;
            // Non-symmetric, column-indexed source data; never identity-only.
            const float jitter=0.001f*float(inputSeed%13);
            const std::array<float,16> matrix={
                .93f,jitter+.04f,-.01f,.01f, -.07f,.87f,.03f,0.f,
                .02f,-.04f,.91f,0.f, .025f,-.035f,.015f,1.f};
            std::copy(matrix.begin(),matrix.end(),values.begin()+start);
            if(s==1&&mutation==5&&b==1)values[start+12]+=.31f;
            if(s==1&&mutation==7)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++)
                std::swap(values[start+x*4+y],values[start+y*4+x]);
        } else {
            values[8]=.025f; values[12]=-1.1f;values[13]=-2.3f;values[14]=-.7f;
            values[16]=1.f/float(w);values[17]=1.f/float(h);
            if(s==1&&mutation==6)for(int k:{8,12,13,14,16,17})values[k]*=3.f;
        }
        VkBufferCreateInfo bi{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
        bi.size=uniformBytes[b];bi.usage=VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT;
        check(vkCreateBuffer(device,&bi,nullptr,&u.buffer),"create source uniform buffer");
        VkMemoryRequirements mr{};vkGetBufferMemoryRequirements(device,u.buffer,&mr);
        VkMemoryAllocateInfo ma{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};ma.allocationSize=mr.size;
        ma.memoryTypeIndex=memoryType(mr.memoryTypeBits,VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT|VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
        check(vkAllocateMemory(device,&ma,nullptr,&u.memory),"allocate source uniforms");
        check(vkBindBufferMemory(device,u.buffer,u.memory,0),"bind source uniforms");
        void* ptr=nullptr;check(vkMapMemory(device,u.memory,0,mr.size,0,&ptr),"map source uniforms");
        std::memcpy(ptr,values.data(),uniformBytes[b]);vkUnmapMemory(device,u.memory);
        uniformInfos[index]={u.buffer,0,uniformBytes[b]};
        auto& write=uniformWrites[index];write.sType=VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
        write.dstSet=sets[s];write.dstBinding=4+b;write.descriptorCount=1;
        write.descriptorType=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;write.pBufferInfo=&uniformInfos[index];
    }
    vkUpdateDescriptorSets(device,uniformWrites.size(),uniformWrites.data(),0,nullptr);
'''


def generate(template):
    if hashlib.sha256(template.encode()).hexdigest() != HOST_SHA256:
        raise ValueError("W1 raster host changed; review rather than silently patch")
    edits = [
        ('mutation<=4', 'mutation<=7'),
        ('std::array<VkDescriptorSetLayoutBinding,4> bindings{};',
         'std::array<VkDescriptorSetLayoutBinding,7> bindings{};'),
        ('    VkDescriptorSetLayoutCreateInfo sl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};sl.bindingCount=4;',
         '''    for(uint32_t b=4;b<7;b++) {
        bindings[b].binding=b;bindings[b].descriptorCount=1;
        bindings[b].descriptorType=VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER;
        bindings[b].stageFlags=b<6?VK_SHADER_STAGE_VERTEX_BIT:VK_SHADER_STAGE_FRAGMENT_BIT;
    }
    VkDescriptorSetLayoutCreateInfo sl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};sl.bindingCount=7;'''),
        ('std::array<VkDescriptorPoolSize,2> sizes={VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,4},VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_SAMPLER,4}};',
         'std::array<VkDescriptorPoolSize,3> sizes={VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,4},VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_SAMPLER,4},VkDescriptorPoolSize{VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,6}};'),
        ('dp.poolSizeCount=2;', 'dp.poolSizeCount=3;'),
        ('    vkUpdateDescriptorSets(device,writes.size(),writes.data(),0,nullptr);',
         '    vkUpdateDescriptorSets(device,writes.size(),writes.data(),0,nullptr);\n' + UNIFORMS),
        ('    vkDestroyBuffer(device,vertexBuffer,nullptr);',
         '    for(auto& u:uniforms){vkDestroyBuffer(device,u.buffer,nullptr);vkFreeMemory(device,u.memory,nullptr);}\n    vkDestroyBuffer(device,vertexBuffer,nullptr);'),
    ]
    for before, after in edits:
        if template.count(before) != 1:
            raise ValueError("W5 host insertion boundary changed")
        template = template.replace(before, after)
    return template


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with args.output.open('x') as output:
        output.write(generate(args.template.read_text()))
