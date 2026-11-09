"""Audit bounded T1 FFT passive trace pairs without claiming GPU success.

Input: UTF-8 JSONL objects with event and message keys, exported from a single
AndroidRuntimeLog session. Only this narrow diagnostic contract is accepted.
No original game data or shaders are required.
"""
import argparse
import json
from pathlib import Path

BEFORE = "t1_original_fft_dispatch.before"
AFTER = "t1_original_fft_dispatch.returned"


def audit(records):
    pending = {}
    seen = set()
    paired = set()
    errors = []
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("trace row must be object")
        event = row.get("event")
        if event not in (BEFORE, AFTER):
            continue
        message = row.get("message")
        if not isinstance(message, str):
            raise ValueError("missing trace message")
        fields = {}
        for part in message.split(";"):
            part = part.strip()
            if not part:
                continue
            if "=" not in part:
                raise ValueError("malformed trace field")
            k, v = part.split("=", 1)
            k = k.strip()
            if k in fields:
                raise ValueError("duplicate trace field")
            fields[k] = v.strip()
        seq = fields.get("sequence", "")
        if not seq.isdecimal() or not 1 <= int(seq) <= 16:
            raise ValueError("invalid bounded sequence")
        seq = int(seq)
        key = (event, seq)
        duplicate = key in seen
        if duplicate:
            errors.append("duplicate_event:" + str(seq))
        seen.add(key)
        if event == BEFORE:
            if not duplicate:
                pending[seq] = fields
        elif seq not in pending:
            errors.append("return_without_before:" + str(seq))
        elif not duplicate:
            paired.add(seq)
    missing = sorted(seq for seq in pending if seq not in paired)
    return {"before_count": len(pending),
            "returned_count": len([k for k in seen if k[0] == AFTER]),
            "missing_return_sequences": missing,
            "errors": errors,
            "runtime_kernel_identity_proven": False,
            "gpu_execution_proven": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("jsonl", type=Path)
    a = p.parse_args()
    if not a.jsonl.is_file() or a.jsonl.stat().st_size > 1048576:
        raise ValueError("bounded trace JSONL required (<=1 MiB)")
    rows = [json.loads(line) for line in a.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(audit(rows), sort_keys=True))


if __name__ == "__main__":
    main()
