"""Recheck the exact authored keyword artifact; does not attest execution itself."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import stat
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools/synthetic_material_alpha'))
from keyword_pixels import verify, hashes, KEYS


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def parse(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('nonfinite_json')
    return json.loads(data.decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid)


def review(archive, digest, run_id):
    require(archive.is_file() and not archive.is_symlink() and 0 < archive.stat().st_size < 8*1024*1024,
            'archive_size_or_path')
    archive_bytes = archive.read_bytes()
    require(sha256(archive_bytes).hexdigest() == digest, 'archive_sha256_mismatch')
    import io
    with ZipFile(io.BytesIO(archive_bytes)) as z:
        items = z.infolist()
        require(len(items) == 3, 'unexpected_archive_population')
        names = [PurePosixPath(i.filename) for i in items]
        require(all(not n.is_absolute() and '..' not in n.parts and len(n.parts) <= 2 for n in names)
                and len(set(n.parent for n in names)) == 1
                and {n.name for n in names} == {'stage.json','raw.unity.json','verified.json'}, 'unexpected_archive_members')
        require(all(not i.is_dir() and not stat.S_ISLNK(i.external_attr >> 16)
                    and 0 < i.file_size <= 4*1024*1024 for i in items), 'unexpected_member_type_or_size')
        require(z.testzip() is None, 'archive_crc_failed')
        data = {n.name: z.read(i) for n,i in zip(names,items)}
    staged, raw, supplied = (parse(data[k]) for k in ('stage.json','raw.unity.json','verified.json'))
    require(staged == {'status':'PREPARED','Unity_render_executed':False,'synthetic_only':True,
                       'files':hashes(),'route_keys':[list(k) for k in KEYS]}, 'staged_fixture_mismatch')
    result = verify(raw, run_id, 0)
    require(supplied == result, 'runner_report_differs_from_independent_recomputation')
    return {'archive_sha256':digest,'archive_bytes':len(archive_bytes),'run_id':run_id,
            'members':{k:{'bytes':len(v),'sha256':sha256(v).hexdigest()} for k,v in sorted(data.items())},
            'local_numeric_replay':result,'first_observed_pixel_per_case':{r['name']:r['samples'][0]['rgba'] for r in raw['cases']},
            'execution_attestation_requires_matching_github_run_and_job':True,
            'original_game_pixels_verified':False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--run-id',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    require(not a.out.exists() and not a.out.is_symlink(), 'fresh_output_required')
    result=review(a.archive,a.sha256,a.run_id)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
