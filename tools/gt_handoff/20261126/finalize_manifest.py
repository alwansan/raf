"""Record exact preserved bytes; run only after handoff edits are final."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'clients/GT/sessions/20261126-complete-handoff'
MANIFEST=BASE/'MANIFEST.json'

def main():
    modified=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    paths=sorted({p for p in modified+untracked if '__pycache__/' not in p and not p.endswith('.pyc') and p!=MANIFEST.relative_to(ROOT).as_posix()})
    inventory=BASE/'inventory/preserved-code-and-document-paths.json'
    if inventory.relative_to(ROOT).as_posix() not in paths:paths.append(inventory.relative_to(ROOT).as_posix());paths.sort()
    inventory.write_text(json.dumps({'compared_base':'f3c8a2cdacf04fdbfbced5f87a1407da223e3a15','paths':paths+[MANIFEST.relative_to(ROOT).as_posix()],'excluded_cache_only':True},indent=2)+'\n')
    for p in paths:
        f=ROOT/p
        if f.is_symlink() or not f.is_file():raise ValueError('unsafe preserved file: '+p)
    files=[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
    # Record public pre-existing code dependencies too, without copying them.
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    deps=[p for p in tracked if p not in paths and (p.startswith('scripts/gt_') or p.startswith('scripts/w1_') or p in ('scripts/t3_particle108_source_propstate.py','scripts/b44_verify_material_colors.py','scripts/verify_water_render_contract.py','clients/GT/OWNER_DIRECTIVE_RESTORE_FIRST_AR.md','clients/GT/METHOD_AR.md','docs/ZIP2_SOURCE_PROVIDER.md') or p.startswith('tools/synthetic_material_alpha/'))]
    references=[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in deps]
    MANIFEST.write_text(json.dumps({'schema_version':1,'date':'2026-11-26','reviewed_branch':'feature/android-native-port','reviewed_base':'f3c8a2cdacf04fdbfbced5f87a1407da223e3a15','purpose':'preserve all available authoring tools, tests, aggregate receipts and explanations; not restoration completion','CI_commit_skip_required':True,'files':files,'existing_repository_references':references,'manifest_self_hash_omitted':True,'known_missing_batches':3,'private_assets_or_credentials_included':False},indent=2)+'\n')
    print(json.dumps({'preserved_files':len(files),'existing_references':len(references),'preserved_bytes':sum(x['bytes'] for x in files),'manifest_sha256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}))

if __name__=='__main__':main()
