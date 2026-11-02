"""Execute the real workflow FMOD/data gate against synthetic standalone/split packages."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]


class OriginalDataGateTests(unittest.TestCase):
    def run_gate(self, split=False, mutation=None):
        workflow = yaml.safe_load((ROOT/".github/workflows/raft-unity-editor-android-import.yml").read_text())
        step = next(s for s in workflow["jobs"]["reconstruct"]["steps"]
                    if s.get("name") == "Verify actual APK FMOD libraries, Java bridge and original bank/data bytes")
        script = step["run"].split("<<'PY'\n",1)[1].rsplit("\nPY",1)[0]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root/"builds/Android").mkdir(parents=True)
            data = b"synthetic original sound data"
            (root/"original-streaming-assets.json").write_text(json.dumps({"files":{"Master.bank":{
                "bytes":len(data), "sha256":hashlib.sha256(data).hexdigest()}}}))
            original = data if mutation != "changed" else b"x"*len(data)
            apk = root/"builds/Android/RaftAndroidExperimental.apk"
            with zipfile.ZipFile(apk,"w") as archive:
                for name in ("libfmod.so","libfmodstudio.so","libresonanceaudio.so"):
                    archive.writestr("lib/arm64-v8a/"+name,b"synthetic ELF")
                archive.writestr("classes.dex",b"Lorg/fmod/FMOD;")
                if (not split or mutation == "duplicated") and mutation != "missing":
                    archive.writestr("assets/Master.bank",original)
            if split:
                with zipfile.ZipFile(apk.with_suffix(".main.obb"),"w") as archive:
                    if mutation != "missing": archive.writestr("assets/Master.bank",original)
            elf={"abi":"arm64-v8a","exports":{"FMOD_System_Create","FMOD_System_GetVersion","FMOD_Studio_System_Create"}}
            previous = Path.cwd()
            try:
                os.chdir(root)
                with patch.dict(os.environ,{"RUNNER_TEMP":str(root)}), patch("scripts.audit_fmod_unity_package.elf_identity",return_value=elf), contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(script,"actual-workflow-original-data-gate","exec"),{})
            finally:
                os.chdir(previous)

    def test_standalone_and_split_preserve_exact_original_data_gate(self):
        self.run_gate()
        self.run_gate(split=True)

    def test_both_layouts_reject_missing_or_changed_original_data(self):
        for split in (False,True):
            for mutation in ("missing","changed"):
                with self.subTest(split=split,mutation=mutation):
                    with self.assertRaises(AssertionError): self.run_gate(split,mutation)

    def test_split_rejects_duplicated_original_data(self):
        with self.assertRaises(AssertionError): self.run_gate(True,"duplicated")
