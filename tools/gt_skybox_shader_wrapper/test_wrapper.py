"""Authored negative controls for the source-bound single-pass wrapper."""
import tempfile
import unittest
from pathlib import Path
from tools.gt_skybox_shader_wrapper import wrapper as w
from tools.gt_light_same_export.audit import Rejected


class WrapperTests(unittest.TestCase):
    def route(self):
        return {"subshader":0,"pass":0,"routes":[{"enabled":[]}],
                "keyword_universe":[],"unmatched_vertex_keywords":[]}

    def test_exact_route(self):
        self.assertEqual(w.single_route([self.route()]),self.route())

    def test_keyword_rejected(self):
        r=self.route()
        r["routes"][0]["enabled"]=["AUTHORED"]
        with self.assertRaises(Rejected): w.single_route([r])

    def test_extra_route_rejected(self):
        r=self.route()
        r["routes"].append({"enabled":[]})
        with self.assertRaises(Rejected): w.single_route([r])

    def test_orphan_rejected(self):
        r=self.route()
        r["unmatched_vertex_keywords"]=[[]]
        with self.assertRaises(Rejected): w.single_route([r])

    def test_attach_one(self):
        s=w.attach("before\n"+w.MARKER+"\nafter","authored")
        self.assertEqual(s.count("HLSLPROGRAM"),1)
        self.assertIn("#pragma vertex gt_vs_main",s)
        self.assertIn("#pragma fragment gt_fs_main",s)
        self.assertNotIn(w.MARKER,s)

    def test_extra_marker_rejected(self):
        with self.assertRaises(Rejected): w.attach(w.MARKER*2,"authored")

    def test_duplicate_varying_rejected(self):
        with self.assertRaises(Rejected):
            w.interface({"inputs":[{"location":0,"type":"vec4"}]*2},"inputs")

    def test_interface_matches_and_drift_rejected(self):
        a={"inputs":[{"location":0,"type":"vec3"}],
           "outputs":[{"location":1,"type":"vec4"}]}
        b={"inputs":[{"location":1,"type":"vec4"}],
           "outputs":[{"location":0,"type":"vec4"}]}
        self.assertEqual(w.compare_interfaces(a,b,a,b,a)["varyings"],1)
        bad=dict(b,inputs=[{"location":0,"type":"vec4"}])
        with self.assertRaises(Rejected): w.compare_interfaces(a,bad,a,b,a)
        with self.assertRaises(Rejected): w.compare_interfaces(a,bad,a,bad,a)

    def test_missing_final_buffer_rejected(self):
        with self.assertRaises(Rejected):
            w.verify_final_offsets({"ubos":[]},[{"name":"authored"}],"vs")

    def test_install_only_shader(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve()
            s=p/"a.shader";m=p/"a.shader.meta";f=p/"scene.unity";t=p/"material.mat"
            s.write_text("//DummyShaderTextExporter\nold")
            for q in (m,f,t): q.write_text(q.name)
            r=w.install(s,[m,f,t],p,"authored candidate")
            self.assertEqual(r["protected_files_unchanged"],3)
            self.assertEqual(s.read_text(),"authored candidate")
            for q in (m,f,t): self.assertEqual(q.read_text(),q.name)

    def test_install_without_dummy_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve();s=p/"a.shader";s.write_text("original")
            with self.assertRaises(Rejected): w.install(s,[],p,"candidate")
            self.assertEqual(s.read_text(),"original")

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve();s=p/"a.shader";s.write_text("//DummyShaderTextExporter")
            q=p/"symlink";q.symlink_to(s)
            with self.assertRaises(Rejected): w.install(q,[],p,"candidate")

    def test_safe_category_does_not_emit_private_text(self):
        self.assertEqual(w.error_category(ValueError("Private shader name!")),"ValueError")
        self.assertEqual(w.error_category(ValueError("skybox_final_entry_identity")),"skybox_final_entry_identity")


if __name__ == "__main__":
    unittest.main()
