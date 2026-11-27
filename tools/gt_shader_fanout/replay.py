"""Replay the permanent actual authored exporter archive, no original fetch."""
import hashlib,json,zipfile
from pathlib import Path,PurePosixPath
from tempfile import TemporaryDirectory
from tools.gt_shader_fanout.audit import scan
from scripts import t3_exported_renderer_shader_impact as old

ARCHIVE=Path("clients/GT/sessions/20261127-authored-external-pptr-route/actual-evidence-46018334469.zip")
SHA="7a09666cddddb6ede58ab32bbd616fa6a2df248bb52627d4310a6b2f86e2a7e4"
def main():
    raw=ARCHIVE.read_bytes()
    assert len(raw)==39284 and hashlib.sha256(raw).hexdigest()==SHA
    with TemporaryDirectory() as tmp,zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None and len(z.namelist())==50 and len(set(z.namelist()))==50
        prefix="case/actual-export/"
        root=Path(tmp)
        selected=[x for x in z.infolist() if x.filename.startswith(prefix)]
        assert len(selected)==20 and sum(x.file_size for x in selected)<1024*1024
        for item in selected:
            name=PurePosixPath(item.filename[len(prefix):])
            assert not name.is_absolute() and ".." not in name.parts and name.parts[0]=="Assets"
            p=root.joinpath(*name.parts);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(z.read(item))
        result,_=scan(root)
        assert result["material_documents"]==2 and result["renderer_documents"]==2
        assert result["counts"]["renderer_slots"]==4
        assert result["counts"]["renderer_slots_resolved_native_material"]==4
        assert result["counts"]["slot_native_shader_document_unverified"]==4
        assert result["dummy_shader_guid_targets"]==0
        try:old.audit(root)
        except ValueError as e:
            assert str(e)=="no_exported_ShaderLab_sources"
        else:raise AssertionError("old classification unexpectedly accepted")
        print(json.dumps({"status":"PASS_RETAINED_ACTUAL_AUTHORED_EXPORT_FANOUT","archive_sha256":SHA,
                          "exact_export_files_replayed":20,"report":result},sort_keys=True))
if __name__=="__main__":main()
