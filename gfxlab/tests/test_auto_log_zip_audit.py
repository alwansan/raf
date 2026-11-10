import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from gfxlab.tools.auto_log_zip_audit import analyze,parse_snapshot

def state(model="M03",role="METALLIC",channel="G",sampling="FORCE_LINEAR_IMPORT",surface=1):
    return {
      "experiment":"GFX-MULTI-031","modelId":model,
      "diagnosticRole":role,"diagnosticChannel":channel,
      "diagnosticSampling":sampling,
      "diagnosticMaterialSurface":surface,
      "materialMode":"SOURCE_PBR_STANDARD_APPROX",
      "originalShaderRestored":False}

class TestAutoLogZipAudit(unittest.TestCase):
    def test_single_report_parses_double_nested_json_string(self):
        row={"kind":"state_snapshot","stateJson":json.dumps(state())}
        self.assertEqual(parse_snapshot(row)["diagnosticChannel"],"G")
        self.assertFalse(parse_snapshot(row)["originalShaderRestored"])

    def test_reject_unrelated_apk_or_missing_state(self):
        row={"kind":"state_snapshot","stateJson":json.dumps({"experiment":"WRONG"})}
        with self.assertRaises(ValueError):parse_snapshot(row)
        with self.assertRaises(ValueError):parse_snapshot({"kind":"state_snapshot"})
        x=state();x["diagnosticChannel"]="invalid"
        with self.assertRaises(ValueError):parse_snapshot({"kind":"state_snapshot","stateJson":json.dumps(x)})

    def test_zip_aggregates_all_sessions_without_raw_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"export.zip"
            reports=[state("M00","BASECOLOR","RGB","SOURCE_TEXTURE_COLORSPACE_IMPORT",0),
                     state("M03","METALLIC","G","FORCE_LINEAR_IMPORT",1)]
            with ZipFile(path,"w") as z:
                z.writestr("README.txt","test")
                for i,item in enumerate(reports):
                    prefix=f"sessions/session{i}/"
                    z.writestr(prefix+"summary.json",json.dumps(
                        {"schema":"gfxlab-session-v1","messagesDropped":0,"writeFailure":""}))
                    z.writestr(prefix+"snapshots.jsonl",json.dumps(
                        {"kind":"state_snapshot","message":"material_surface_changed",
                         "stateJson":json.dumps(item)})+"\n")
                    z.writestr(prefix+"events.jsonl",json.dumps(
                        {"kind":"unity_Exception","message":"PRIVATE_STACK",
                         "stackTrace":"PRIVATE_BINARY_DETAILS"})+"\n")
            d=analyze(path)
            self.assertEqual(d["session_count"],2)
            self.assertEqual(d["snapshot_count"],2)
            self.assertEqual(d["event_count"],2)
            self.assertTrue(d["both_sampling_settings_tested"])
            self.assertTrue(d["m03_second_material_tested"])
            self.assertFalse(d["all_six_models_four_modes_covered"])
            self.assertEqual(d["model_mode_coverage"]["M03"],["SOURCE_PBR_STANDARD_APPROX"])
            self.assertEqual(d["model_channel_coverage"]["M03"],["G"])
            self.assertEqual(d["unity_message_type_counts"]["unity_Exception"],2)
            self.assertEqual(d["unity_error_warning_messages_with_stack_text"],2)
            self.assertNotIn("PRIVATE_STACK",str(d))
            self.assertNotIn("PRIVATE_BINARY_DETAILS",str(d))
            self.assertFalse(d["original_shader48_restored"])
            self.assertFalse(d["source_vs_pc_gpu_pixel_parity_verified"])

    def test_missing_session_parts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"incomplete.zip"
            with ZipFile(path,"w") as z:
                z.writestr("sessions/a/snapshots.jsonl","{}")
            with self.assertRaises(ValueError):analyze(path)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"unsafe.zip"
            with ZipFile(path,"w") as z:z.writestr("../outside.txt","secret")
            with self.assertRaises(ValueError):analyze(path)

    def test_surface_on_another_model_does_not_count_for_m03(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"false-positive.zip"
            with ZipFile(path,"w") as z:
                z.writestr("sessions/s0/summary.json",json.dumps(
                    {"schema":"gfxlab-session-v1","messagesDropped":0,"writeFailure":""}))
                data=[
                    state("M00","BASECOLOR","RGB","SOURCE_TEXTURE_COLORSPACE_IMPORT",1),
                    state("M03","NORMAL","R","FORCE_LINEAR_IMPORT",0)]
                z.writestr("sessions/s0/snapshots.jsonl","".join(
                    json.dumps({"kind":"state_snapshot","stateJson":json.dumps(x)})+"\n"
                    for x in data))
                z.writestr("sessions/s0/events.jsonl",json.dumps(
                    {"kind":"user_action","message":"PRIVATE"})+"\n")
            d=analyze(path)
            self.assertFalse(d["m03_second_material_tested"])
            self.assertEqual(d["surface_counts"],{"1":1,"0":1})
            self.assertFalse(d["all_six_models_four_modes_covered"])

    def test_session_parts_must_match_same_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"mismatched.zip"
            with ZipFile(path,"w") as z:
                z.writestr("sessions/a/summary.json",json.dumps(
                    {"schema":"gfxlab-session-v1"}))
                z.writestr("sessions/b/snapshots.jsonl",json.dumps(
                    {"kind":"state_snapshot","stateJson":json.dumps(state())})+"\n")
                z.writestr("sessions/c/events.jsonl",json.dumps(
                    {"kind":"unity_Log","message":"PRIVATE"})+"\n")
            with self.assertRaisesRegex(ValueError,"SESSION_FILE_SET_MISMATCH"):
                analyze(path)
