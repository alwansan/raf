"""B47: negative-control contract for FFT/Water ComputeShader source candidates."""
from pathlib import Path
import tempfile
import unittest

from scripts.b47_compute_kernel_contract import kernel_entrypoint_profile
from scripts.verify_water_render_contract import inspect, native_ready


def make_compute(root, source):
    assets = root / "Assets"
    assets.mkdir(exist_ok=True)
    path = assets / "FFT.compute"
    path.write_text(source, encoding="utf-8")
    Path(str(path) + ".meta").write_text("guid: " + "1" * 32, encoding="utf-8")
    return path


class B47KernelContractTests(unittest.TestCase):
    def test_literal_numthreads_and_closed_entrypoint(self):
        source = (
            "#pragma kernel Horizontal\n[numthreads(8,8,1)]\n"
            "void Horizontal(uint3 id : SV_DispatchThreadID) { if(id.x){ return; } }"
        )
        self.assertEqual(kernel_entrypoint_profile(source), {
            "kernel_count": 1, "kernels_with_structural_entrypoints": 1,
            "unique_kernel_names": True, "all_kernel_entrypoints_structural": True,
        })
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_compute(root, source)
            report = inspect(root)
            self.assertTrue(report["water_compute_source_candidate_present"])
            self.assertEqual(report["compute_files_with_structural_entrypoints"], 1)
            self.assertFalse(report["authentic_water_kernel_identity_verified"])
            self.assertFalse(native_ready(report))

    def test_bare_pragma_is_not_a_kernel_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_compute(root, "#pragma kernel FFT\n")
            report = inspect(root)
            self.assertEqual(report["compute_files_with_kernels"], 1)
            self.assertEqual(report["compute_files_with_structural_entrypoints"], 0)
            self.assertFalse(report["water_compute_source_candidate_present"])

    def test_unbound_missing_or_unfinished_entrypoints_rejected(self):
        sources = (
            "#pragma kernel K\nvoid K() {}",
            "#pragma kernel K\n[numthreads(8,8,1)] void Other() {}",
            "#pragma kernel K\n[numthreads(8,8,1)] void K();",
            "#pragma kernel K\n[numthreads(8,8,1)] void K(){",
            "#pragma kernel K\n[numthreads(8,8,1)] void K() { }\n[numthreads(8,8,1)] void K() { }",
        )
        for source in sources:
            with self.subTest(source=source[:24]):
                self.assertFalse(kernel_entrypoint_profile(source)["all_kernel_entrypoints_structural"])

    def test_comments_and_quoted_pragma_cannot_be_candidates(self):
        source = (
            '// #pragma kernel Bad\n/* #pragma kernel AlsoBad */\n'
            '"#pragma kernel Quoted"\n'
        )
        self.assertEqual(kernel_entrypoint_profile(source)["kernel_count"], 0)

    def test_duplicate_kernel_names_rejected(self):
        source = (
            "#pragma kernel A\n#pragma kernel A\n"
            "[numthreads(1,1,1)] void A(){}"
        )
        report = kernel_entrypoint_profile(source)
        self.assertEqual(report["kernel_count"], 2)
        self.assertFalse(report["unique_kernel_names"])
        self.assertFalse(report["all_kernel_entrypoints_structural"])

    def test_thread_group_bounds(self):
        for x, y, z in ((0,8,8), (33,33,1), (2048,1,1)):
            with self.subTest(dimensions=(x,y,z)):
                source = (
                    f"#pragma kernel K\n[numthreads({x},{y},{z})] void K(){{}}"
                )
                self.assertFalse(kernel_entrypoint_profile(source)["all_kernel_entrypoints_structural"])

    def test_two_independent_valid_entrypoints(self):
        source = (
            "#pragma kernel A\n#pragma kernel B\n"
            "[numthreads(8,8,1)] void A(){}\n"
            "[numthreads(1,1,1)] void B(){ int a=2; }"
        )
        self.assertEqual(kernel_entrypoint_profile(source)["kernels_with_structural_entrypoints"], 2)

    def test_meta_symlink_never_counts_as_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = "#pragma kernel A\n[numthreads(1,1,1)]void A(){}"
            path = make_compute(root, source)
            meta = Path(str(path) + ".meta")
            meta.unlink()
            meta.symlink_to(path)
            report = inspect(root)
            self.assertFalse(report["water_compute_source_candidate_present"])


if __name__ == "__main__":
    unittest.main()
