"""Stage the private, single-workgroup Vulkan side of T1 FFT parity."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def render_host(source: str) -> str:
    changes = {
        "std::array<VkImageMemoryBarrier,2> postBarriers{};\n    for(int i=0;i<2;i++){":
            "std::array<VkImageMemoryBarrier,3> postBarriers{};\n    for(int i=0;i<3;i++){",
        "postBarriers[i].image=images[i?5:3].image;":
            "postBarriers[i].image=images[i==0?2:(i==1?3:5)].image;",
        "0,0,nullptr,0,nullptr,2,postBarriers.data());":
            "0,0,nullptr,0,nullptr,3,postBarriers.data());",
        '    check(vkDeviceWaitIdle(device),"vkDeviceWaitIdle");': '''    // Write tightly packed mapped texels only inside private runner scratch.
    static_assert(sizeof(float)==4 && std::numeric_limits<float>::is_iec559);
    const std::array<const char*,4> names={
        "source.rgba32f","butterfly.rgba32f","pass0.rgba32f","pass1.rgba32f"};
    for(int i=0;i<4;i++){
        std::ofstream out(names[i],std::ios::binary | std::ios::trunc);
        require(bool(out),"Private readback open failed");
        for(uint32_t y=0;y<h;y++)for(uint32_t x=0;x<w;x++) {
            const auto p=pixel(images[i],x,y,imageFormat);
            out.write(reinterpret_cast<const char*>(p.data()),4*sizeof(float));
        }
        out.close();
        require(bool(out),"Private readback write failed");
    }
    check(vkDeviceWaitIdle(device),"vkDeviceWaitIdle");''',
    }
    for anchor, replacement in changes.items():
        if source.count(anchor) != 1:
            raise ValueError("A1 Vulkan host changed; inspect private capture anchors")
        source = source.replace(anchor, replacement)
    return source


def capture(host: Path, project: Path) -> None:
    project = project.resolve()
    modules = [project / "_private_vulkan" / f"slot{slot}.spv" for slot in (0, 1)]
    output = project / "T1VulkanCapture"
    output.mkdir(mode=0o700)
    with tempfile.TemporaryDirectory(prefix="t1-vulkan-host-") as tmp:
        source = Path(tmp) / "capture.cpp"
        runner = Path(tmp) / "capture"
        source.write_text(render_host(host.read_text()))
        subprocess.run(["g++", "-std=c++17", "-O2", str(source), "-lvulkan", "-o", str(runner)],
                       check=True, timeout=60, capture_output=True)
        subprocess.run([str(runner), str(modules[0]), str(modules[0]), str(modules[1]),
                        str(modules[1]), "1024", "32", "19", "1", "rgba32f"],
                       cwd=output, check=True, timeout=110, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    try:
        capture(Path("scripts/a1_fft_two_pass_vulkan.cpp"), args.project)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(1, "Private Vulkan capture failed\n")
    print("RAFT_T1_PRIVATE_VULKAN_CAPTURE completed=true")


if __name__ == "__main__":
    main()
