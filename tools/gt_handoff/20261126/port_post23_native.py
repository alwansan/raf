from pathlib import Path
p=Path('.github/workflows/raft-unity-editor-android-import.yml')
s=p.read_text()
a=s.index('      - name: Recover original Particle108 ShaderLab')
b=s.index('      - name: Recover and stage original BlockPaint',a)
particles=s[a:b]
s=s[:a]+s[b:]
anchor='      - name: Inventory actual exported Material Shader references without modifying assets\n'
i=s.index(anchor)

baseline='''      - name: GT record strict native post9 shader census and protected YAML baseline
        shell: bash
        run: |
          set -euo pipefail
          python3 -m scripts.t3_audit_exported_material_programs \\
            --project "$RUNNER_TEMP/project/ExportedProject" --rank-dummy-targets \\
            --out "$RUNNER_TEMP/gt-nine-shader-postrestore-quality.json"
          python3 - <<'PY_GT_NATIVE_POST9'
          import hashlib,json,os
          from pathlib import Path
          root=Path(os.environ["RUNNER_TEMP"])
          q=json.loads((root/"gt-nine-shader-postrestore-quality.json").read_text())
          c=q["counts"]
          assert q["status"]=="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
          assert c["material_documents"]==1536
          assert c["material_docs_using_Unity_builtin_Shader"]==750
          assert c["material_docs_using_local_custom_Shader"]==786
          assert c["material_docs_with_unknown_or_broken_Shader"]==0
          assert c["material_docs_using_dummy_Shader"]==333
          assert c["material_docs_using_non_dummy_Shader"]==453
          assets=root/"project/ExportedProject/Assets"
          before={}
          for p in assets.rglob("*"):
              if p.is_file() and not p.is_symlink() and p.suffix.lower() in {".meta",".mat",".asset",".prefab",".unity"}:
                  h=hashlib.sha256()
                  with p.open("rb") as f:
                      for chunk in iter(lambda:f.read(1048576),b""):
                          h.update(chunk)
                  before[str(p.relative_to(assets))]=h.hexdigest()
          assert len(before)>1000
          (root/"gt-full-smoke-private-unchanged-material-meta.json").write_text(json.dumps(before,sort_keys=True))
          print("GT_NATIVE_POST9_STRICT_ACCEPTED customNonDummy=453 customDummy=333 protectedFiles="+str(len(before)))
          PY_GT_NATIVE_POST9
'''
post13='''      - name: GT record strict native post13 shader census
        shell: bash
        run: |
          set -euo pipefail
          python3 -m scripts.t3_audit_exported_material_programs \\
            --project "$RUNNER_TEMP/project/ExportedProject" --rank-dummy-targets \\
            --out "$RUNNER_TEMP/gt-thirteen-shader-postrestore-quality.json"
          python3 - <<'PY_GT_NATIVE_POST13'
          import json,os
          from pathlib import Path
          root=Path(os.environ["RUNNER_TEMP"])
          q=json.loads((root/"gt-thirteen-shader-postrestore-quality.json").read_text())
          c=q["counts"]
          assert q["status"]=="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
          assert c["material_documents"]==1536
          assert c["material_docs_using_Unity_builtin_Shader"]==750
          assert c["material_docs_using_local_custom_Shader"]==786
          assert c["material_docs_with_unknown_or_broken_Shader"]==0
          assert c["material_docs_using_dummy_Shader"]==246
          assert c["material_docs_using_non_dummy_Shader"]==540
          assert c["distinct_dummy_Shader_targets_referenced"]==47
          print("GT_NATIVE_POST13_STRICT_ACCEPTED customNonDummy=540 customDummy=246")
          PY_GT_NATIVE_POST13
'''
ref=Path('.github/workflows/raft-gt-next7p33-original-full-export.yml').read_text()
start=ref.index('      - name: Authenticate still-unrestored 30-material Shader48')
end=ref.index('      - name: Publish aggregate evidence only, never original scenes/meshes/export/trace',start)
block=ref[start:end]
for old,new in [ ('gt-input','w1-original'),('gt-project/ExportedProject','project/ExportedProject'),('gt-private-export-lineage.json','private-export-lineage.json'),('.gt-zip2','zip2-original') ]:
    block=block.replace(old,new)
# Aggregate-only receipts use their established per-stage schema. They describe
# restoration before the game build; no package or device result is claimed.
s=s[:i]+baseline+particles+post13+block+s[i:]
p.write_text(s)
