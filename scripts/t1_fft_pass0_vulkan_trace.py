"""Execute the authenticated pass-zero trace in private Vulkan scratch."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from scripts.t1_fft_pass0_trace_variant import instrument
from scripts.t1_fft_readback_parity import compare_pass, read_image
from scripts.t1_fft_vulkan_roundtrip_isolation import HEIGHT, WIDTH, capture_host, run


def trace_host(source):
    source = capture_host(source)
    patches = {
        "std::array<VkDescriptorSetLayoutBinding,3> bindings{};": """constexpr VkDeviceSize traceBytes = 4097 * sizeof(uint32_t);
    VkBufferCreateInfo traceCi{VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    traceCi.size = traceBytes;
    traceCi.usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;
    VkBuffer traceBuffer;
    check(vkCreateBuffer(device, &traceCi, nullptr, &traceBuffer), "create trace buffer");
    VkMemoryRequirements traceReq;
    vkGetBufferMemoryRequirements(device, traceBuffer, &traceReq);
    uint32_t traceType = memProps.memoryTypeCount;
    for (uint32_t i = 0; i < memProps.memoryTypeCount; ++i) {
        const auto flags = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
        if ((traceReq.memoryTypeBits & (1u << i)) &&
            (memProps.memoryTypes[i].propertyFlags & flags) == flags) {
            traceType = i;
            break;
        }
    }
    require(traceType < memProps.memoryTypeCount, "trace memory unavailable");
    VkMemoryAllocateInfo traceAi{VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    traceAi.allocationSize = traceReq.size;
    traceAi.memoryTypeIndex = traceType;
    VkDeviceMemory traceMemory;
    check(vkAllocateMemory(device, &traceAi, nullptr, &traceMemory), "allocate trace");
    check(vkBindBufferMemory(device, traceBuffer, traceMemory, 0), "bind trace");
    void* traceData = nullptr;
    check(vkMapMemory(device, traceMemory, 0, traceBytes, 0, &traceData), "map trace");
    std::memset(traceData, 0, traceBytes);
    std::array<VkDescriptorSetLayoutBinding,4> bindings{};""",
        "    VkDescriptorSetLayoutCreateInfo layoutCi": """    bindings[3] = {3, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, VK_SHADER_STAGE_COMPUTE_BIT, nullptr};
    VkDescriptorSetLayoutCreateInfo layoutCi""",
        "layoutCi.bindingCount=3;": "layoutCi.bindingCount=4;",
        "std::array<VkDescriptorPoolSize,2> poolSizes{};": "std::array<VkDescriptorPoolSize,3> poolSizes{};",
        "    VkDescriptorPoolCreateInfo poolCi": """    poolSizes[2]={VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,4};
    VkDescriptorPoolCreateInfo poolCi""",
        "poolCi.poolSizeCount=2;": "poolCi.poolSizeCount=3;",
        "    std::array<VkShaderModule,4> shaderModules{};": """    VkDescriptorBufferInfo traceInfo{traceBuffer, 0, traceBytes};
    VkWriteDescriptorSet traceWrite{VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
    traceWrite.dstSet = sets[1];
    traceWrite.dstBinding = 3;
    traceWrite.descriptorCount = 1;
    traceWrite.descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER;
    traceWrite.pBufferInfo = &traceInfo;
    vkUpdateDescriptorSets(device, 1, &traceWrite, 0, nullptr);
    std::array<VkShaderModule,4> shaderModules{};""",
        "    std::array<VkImageMemoryBarrier,4> postBarriers{};": """    VkMemoryBarrier traceBarrier{VK_STRUCTURE_TYPE_MEMORY_BARRIER};
    traceBarrier.srcAccessMask = VK_ACCESS_SHADER_WRITE_BIT;
    traceBarrier.dstAccessMask = VK_ACCESS_HOST_READ_BIT;
    vkCmdPipelineBarrier(cmd, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_HOST_BIT,
                         0, 1, &traceBarrier, 0, nullptr, 0, nullptr);
    std::array<VkImageMemoryBarrier,4> postBarriers{};""",
        '    check(vkQueueWaitIdle(queue),"vkQueueWaitIdle");': """    check(vkQueueWaitIdle(queue),"vkQueueWaitIdle");
    std::ofstream trace("trace.bin", std::ios::binary);
    trace.write(static_cast<const char*>(traceData), traceBytes);
    trace.close();
    require(bool(trace), "private trace write failed");""",
        "    vkDestroyDevice(device,nullptr);": """    vkUnmapMemory(device, traceMemory);
    vkDestroyBuffer(device, traceBuffer, nullptr);
    vkFreeMemory(device, traceMemory, nullptr);
    vkDestroyDevice(device,nullptr);""",
    }
    for anchor, replacement in patches.items():
        if source.count(anchor) != 1:
            raise ValueError("Private trace host anchor changed")
        source = source.replace(anchor, replacement)
    return source


def analyze(project, export=None):
    with tempfile.TemporaryDirectory(prefix="t1-runtime-trace-") as temp:
        work = Path(temp)
        path = project / "Assets/T1OriginalDerived/FFT_Candidate_00.compute"
        pragma, hlsl = path.read_text(encoding="utf-8").split("\n", 1)
        if pragma != "#pragma kernel main":
            raise ValueError("Unexpected private entry point")
        (work / "trace.hlsl").write_text(instrument(hlsl))
        print("RAFT_T1_TRACE_STAGE shader_compile", flush=True)
        run(["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
             "-o", "trace.spv", "trace.hlsl"], work)
        run(["spirv-val", "--target-env", "vulkan1.1", "trace.spv"], work)
        print("RAFT_T1_TRACE_STAGE host_compile", flush=True)
        host = Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text()
        (work / "trace.cpp").write_text(trace_host(host))
        run(["g++", "-std=c++17", "-O2", "trace.cpp", "-lvulkan", "-o", "trace"], work)
        print("RAFT_T1_TRACE_STAGE dispatch", flush=True)
        modules = project / "_private_vulkan"
        run(["./trace", str(modules / "slot0.spv"), "trace.spv", str(modules / "slot1.spv"),
             str(modules / "slot1.spv"), str(WIDTH), str(HEIGHT), "19", "1", "rgba32f"], work)
        print("RAFT_T1_TRACE_STAGE readback", flush=True)
        trace = read_image(work / "trace.bin", 4097 * 4)
        (count,) = struct.unpack_from("<I", trace)
        print("RAFT_T1_TRACE_RECORD_COUNT " + str(count), flush=True)
        if not 0 < count <= 512:
            raise ValueError("Empty or overflowed private trace")
        sites = [0, 0, 0]
        out_of_bounds = [0, 0, 0]
        for site, x, y, mip, *_ in struct.iter_unpack("<Iiii4I", trace[4:4 + count * 32]):
            if site >= len(sites):
                print("RAFT_T1_TRACE_STATUS invalid_site", flush=True)
                raise ValueError("Unknown private trace site")
            sites[site] += 1
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT and mip == 0):
                out_of_bounds[site] += 1
        print("RAFT_T1_TRACE_STAGE output_compare", flush=True)
        passes = []
        for slot in (0, 1):
            images = [read_image(work / f"{name}{slot}.rgba32f", WIDTH * HEIGHT * 16)
                      for name in ("original", "roundtrip")]
            passes.append(compare_pass(*images))
        if export is not None and all(sites) and all(row["match"] for row in passes):
            with export.open("xb") as stream:
                stream.write(trace)
        return {"records_by_site": sites, "out_of_bounds_by_site": out_of_bounds,
                "output_parity": passes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--export-private-trace", type=Path)
    args = parser.parse_args()
    try:
        result = analyze(args.project.resolve(), args.export_private_trace)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private Vulkan trace execution or validation failed\n")
    print("RAFT_T1_VULKAN_TRACE " + json.dumps(result, sort_keys=True))
    if not all(result["records_by_site"]) or not all(row["match"] for row in result["output_parity"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
