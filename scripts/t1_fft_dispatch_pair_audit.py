"""Audit bounded T1 FFT passive trace pairs without claiming GPU success.

Input: UTF-8 JSONL operation/detail objects persisted by PersistentDiagnosticLog,
or legacy event/message synthetic fixtures, from a single logger session.
The logger rotates regular segments at 4 MiB. This is passive metadata only;
no original game data or shaders are required.
"""
import argparse
import json
from pathlib import Path

BEFORE = "t1_original_fft_dispatch.before"
# Identity keys must not change between the entry and return of one call.
# Optional provenance, when present, must agree on BOTH sides of a call.
# Legacy sequence-only traces remain parseable but never prove GPU execution.
IDENTITY_FIELDS = ("kernel", "kernel_name", "kernel_index", "find_kernel_result", "dispatch_kernel", "shader", "shader_name", "resource", "fft_length", "fft_size", "bank", "pass_index", "groups_x", "groups_y", "groups_z", "session_id", "build_sha", "shader_guid", "resource_guid", "__trace_schema")
AFTER = "t1_original_fft_dispatch.returned"
# PersistentDiagnosticLog defaults to one 4 MiB on-device JSONL segment.
MAX_LOG_BYTES = 4 * 1024 * 1024


def audit(records):
    pending = {}
    seen = set()
    paired = set()
    invalid_sequences = set()
    failed_returns = set()
    # One JSONL input represents one runtime session/build, not a merge of runs.
    provenance = {}
    provenance_presence = {}
    errors = []
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("trace row must be object")
        # Actual PersistentDiagnosticLog.jsonl rows have operation/detail,
        # NOT the earlier synthetic event/message fixture envelope.
        native = "operation" in row or "detail" in row
        legacy = "event" in row or "message" in row
        if native and legacy:
            raise ValueError("mixed trace envelopes")
        event = row.get("operation") if native else row.get("event")
        if event not in (BEFORE, AFTER):
            continue
        message = row.get("detail") if native else row.get("message")
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
            if not k or not v.strip():
                raise ValueError("empty trace field")
            if k in fields:
                raise ValueError("duplicate trace field")
            fields[k] = v.strip()
        # Internal marker prevents a synthetic return being paired with an
        # authentic AndroidRuntimeLog before event (or vice versa).
        if "__trace_schema" in fields:
            raise ValueError("reserved trace schema field")
        fields["__trace_schema"] = "native" if native else "legacy"
        if native:
            # The logger's top-level "sequence" is a GLOBAL log counter,
            # distinct from the bounded call sequence inside "detail".
            if row.get("area") != "water":
                raise ValueError("invalid original FFT logger area")
            session = row.get("session")
            if not isinstance(session, str) or not session.strip():
                raise ValueError("missing original logger session")
            if "session_id" in fields and fields["session_id"] != session:
                raise ValueError("conflicting original logger session")
            fields["session_id"] = session
            if event == BEFORE:
                # Verify only the source hook schema, not GPU execution.
                required = {
                    "source_sha_prefix": "8aa32937d423",
                    "original_findkernel_callsite_present": "false",
                    "original_runtime_mapping": "unverified",
                    "gpu_result": "unverified",
                }
                if any(fields.get(k) != v for k, v in required.items()):
                    raise ValueError("original FFT before source marker drift")
                for k in ("numeric_kernel_argument", "original_exponent",
                          "shader_instance_session_local", "pass_offset"):
                    try:
                        int(fields[k])
                    except (KeyError, ValueError, TypeError):
                        raise ValueError("invalid original FFT before numeric field: " + k)
                if fields["pass_offset"] not in ("0", "1"):
                    raise ValueError("invalid original FFT before pass offset")
                groups = fields.get("group_xyz", "").split(",")
                if len(groups) != 3:
                    raise ValueError("invalid original FFT before group_xyz")
                try:
                    if [int(x) for x in groups][::2] != [1, 1]:
                        raise ValueError("invalid original FFT before X/Z groups")
                except ValueError:
                    raise ValueError("invalid original FFT before group_xyz")
            elif (fields.get("managed_dispatch_call_returned") != "true"
                  or fields.get("gpu_result") != "unverified"):
                raise ValueError("invalid original FFT returned marker")
        seq = fields.get("sequence", "")
        if not seq.isascii() or not seq.isdecimal() or not 1 <= int(seq) <= 16 or str(int(seq)) != seq:
            raise ValueError("invalid bounded sequence")
        seq = int(seq)
        for name in ("session_id", "build_sha"):
            present = name in fields
            if name in provenance_presence and provenance_presence[name] != present:
                errors.append("cross_session_provenance_presence:" + name + ":" + str(seq))
                invalid_sequences.add(seq)
                paired.discard(seq)
            else:
                provenance_presence[name] = present
            if present:
                if name in provenance and provenance[name] != fields[name]:
                    errors.append("cross_session_provenance:" + name + ":" + str(seq))
                    invalid_sequences.add(seq)
                    paired.discard(seq)
                else:
                    provenance[name] = fields[name]
        key = (event, seq)
        duplicate = key in seen
        if duplicate:
            errors.append("duplicate_event:" + str(seq))
            # A duplicated trace event invalidates the entire sequence even if
            # an earlier return was already counted as a valid pair.
            invalid_sequences.add(seq)
            paired.discard(seq)
        seen.add(key)
        if event == BEFORE:
            if not duplicate:
                pending[seq] = fields
        elif seq not in pending:
            errors.append("return_without_before:" + str(seq))
        elif not duplicate:
            before = pending[seq]
            mismatched = [name for name in IDENTITY_FIELDS
                          if (name in before) != (name in fields)
                          or (name in before and before[name] != fields[name])]
            if mismatched:
                errors.append("identity_mismatch:" + str(seq) + ":" + ",".join(mismatched))
            if "result" in fields and fields["result"] != "returned":
                # Report explicit failure independently of an identity mismatch:
                # both observations matter when investigating a broken dispatch.
                errors.append("dispatch_result_failure:" + str(seq))
                failed_returns.add(seq)
            if not mismatched and seq not in failed_returns and seq not in invalid_sequences:
                paired.add(seq)
    # A foreign trace can arrive after an earlier pair was counted; no pair
    # from a mixed-provenance file may be used as a positive result.
    if any(error.startswith(("cross_session_provenance:", "cross_session_provenance_presence:")) for error in errors):
        paired.clear()
    missing = sorted(seq for seq in pending if seq not in paired)
    return {"before_count": len(pending),
            "returned_count": len([k for k in seen if k[0] == AFTER]),
            "missing_return_sequences": missing,
            "paired_count": len(paired),
            "failed_return_sequences": sorted(failed_returns),
            "errors": errors,
            "runtime_kernel_identity_proven": False,
            "gpu_execution_proven": False}


def reject_duplicate_json_keys(pairs):
    """Do not let JSON parser silently overwrite trace evidence fields."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON trace key: " + key)
        result[key] = value
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("jsonl", type=Path)
    a = p.parse_args()
    if not a.jsonl.is_file() or a.jsonl.stat().st_size > MAX_LOG_BYTES:
        raise ValueError("bounded trace JSONL required (<=4 MiB)")
    rows = [json.loads(line, object_pairs_hook=reject_duplicate_json_keys)
            for line in a.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(audit(rows), sort_keys=True))


if __name__ == "__main__":
    main()
