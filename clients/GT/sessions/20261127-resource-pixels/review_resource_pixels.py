"""Replay the authored resource pixel evidence from an exact Actions ZIP."""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools/synthetic_material_alpha'))
from resource_pixels import verify_results


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return sha256(data).hexdigest()


def strict_json(data):
    def pairs(rows):
        result={}
        for k,v in rows:
            require(k not in result,'duplicate_json_key')
            result[k]=v
        return result
    def invalid(_):
        raise ValueError('nonfinite_json')
    return json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid)


def review(path, expected_sha, run_id):
    require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<4*1024*1024,'archive_bounds')
    data=path.read_bytes(); require(digest(data)==expected_sha,'archive_digest')
    with ZipFile(io.BytesIO(data)) as z:
        entries=z.infolist();names=[PurePosixPath(i.filename) for i in entries]
        require(len(entries)==6 and {n.name for n in names}=={'compiler.json','combined.hlsl','generated.shader','stage.json','raw.unity.json','verified.json'},'archive_population')
        require(all(not n.is_absolute() and '..' not in n.parts and len(n.parts)<=2 for n in names) and len({n.parent for n in names})==1,'archive_paths')
        require(all(not i.is_dir() and not stat.S_ISLNK(i.external_attr>>16) and 0<i.file_size<1024*1024 for i in entries),'member_bounds')
        require(z.testzip() is None,'archive_crc')
        raw={n.name:z.read(i) for n,i in zip(names,entries)}
    parsed={k:strict_json(v) for k,v in raw.items() if k.endswith('.json')}
    with tempfile.TemporaryDirectory(prefix='gt-resource-pixel-review-') as d:
        root=Path(d)
        for k,v in raw.items(): (root/k).write_bytes(v)
        result=verify_results(root,run_id,0,root/'local-review.json')
    require(result==parsed['verified.json'],'runner_numeric_report_mismatch')
    return {'archive_sha256':expected_sha,'archive_bytes':len(data),'run_id':run_id,
            'members':{k:{'bytes':len(v),'sha256':digest(v)} for k,v in sorted(raw.items())},
            'local_numeric_replay':result,'first_row_pixels':{r['name']:[s['rgba'] for s in r['samples'][:4]] for r in parsed['raw.unity.json']['cases']},
            'compiler_invocations':parsed['compiler.json']['tool_invocations'],
            'Unity_or_compiler_reexecuted_locally':False,'execution_attestation_requires_matching_GitHub_run_and_job':True,
            'original_game_pixels_verified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--sha256',required=True);p.add_argument('--run-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    require(not a.out.exists() and not a.out.is_symlink(),'fresh_output_required')
    result=review(a.archive,a.sha256,a.run_id);a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
