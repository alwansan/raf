"""Extract SHA-original Foam Shader.m_Name to PRIVATE scratch, never log a literal."""
import argparse
import os
from pathlib import Path

def safe_private_name(value, expected):
    if (type(value) is not str or type(expected) is not str
            or not (1 <= len(value) <= 256) or value != expected
            or any(ch in value for ch in ('\x00', '\r', '\n'))):
        raise ValueError("original_Foam_Shader_identity_mismatch")
    return value

def prepare_name(source: Path, destination: Path):
    from scripts.t2_foam_member_abi import original_source_tree
    from scripts.b24_original_foam_stage_translation import TARGET
    from scripts.w1_stage_zip2_owners import safe
    source, destination = source.absolute(), destination.absolute()
    safe(source)
    safe(destination)
    if (not source.is_dir() or destination.exists() or
            not destination.parent.is_dir() or
            destination.is_relative_to(source)):
        raise ValueError("unsafe_private_source_or_destination")
    parsed = original_source_tree(source)
    name = safe_private_name(parsed.get("m_Name"), TARGET)
    fd = os.open(str(destination), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(name)
    return True

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--private-out", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        prepare_name(args.source, args.private_out)
    except BaseException:
        print("T2_FOAM_ORIGINAL_SHADERFIND_NAME_PREP_BLOCKED no_private_content_printed=true")
        return 2
    print("T2_FOAM_ORIGINAL_SHADERFIND_NAME_PREP_PASS name_published=false")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
