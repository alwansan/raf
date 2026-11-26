import subprocess,json,time,os
from pathlib import Path
repo=Path('/home/a/Documents/Codex/2026-11-13/new-chat/work/raf')
root=repo/'clients/GT/sessions/20261126-complete-handoff/tests'
python='/home/a/Documents/Codex/2026-11-13/new-chat/work/unity-reader/bin/python'
patterns=['test_gt_next23b_unity_gate','test_gt_next23b_private_stage_translation','test_gt_original_next23b_source_pass_modes','test_gt_next23b_source_property_flags','test_gt_fft_utilities_restore','test_gt_fft_utilities_unity_contract','test_gt_fft_utilities_bundle','test_gt_install_fft_utilities_original','test_gt_original_921_bundle','test_gt_native_post23_integration','test_gt_native_foam_workflow_contract','test_gt_particle108_export_alpha_diagnostic','test_verify_water_render_contract','test_t5_live_water_ack','test_gt_synthetic_material_alpha','test_gt_restoration_plan_check']
env=dict(os.environ,PYTHONPATH='tests',PYTHONDONTWRITEBYTECODE='1')
command=[python,'-B','-m','unittest',*patterns,'-v']
start=time.monotonic();r=subprocess.run(command,cwd=repo,env=env,capture_output=True,text=True,timeout=180)
(root/'current-focused-tests.txt').write_text(r.stdout+r.stderr)
(root/'current-focused-test-command.json').write_text(json.dumps({'date':'2026-11-26','repository_base':'f3c8a2cdacf04fdbfbced5f87a1407da223e3a15','tested_worktree_includes_preserved_local_drafts':True,'command':command,'environment':{'PYTHONPATH':'tests','PYTHONDONTWRITEBYTECODE':'1'},'exit_code':r.returncode,'seconds':round(time.monotonic()-start,2),'scope':'Source-free synthetic contracts only; no Unity/native/device/game-source execution'},indent=2)+'\n')
print((r.stdout+r.stderr)[-5000:]);raise SystemExit(r.returncode)
