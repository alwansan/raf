"""Privacy-safe declaration-shape triage for authenticated private FileManager exports.

Diagnostic only: never treat a lexical candidate as a resolved implementation.
The caller must verify the original DLL and source fingerprint separately.
"""
import json
import re
import sys
from pathlib import Path
from scripts.b07_probe_original_world_callbacks import _executable_positions

ACCESS = re.compile(r"(?m)^[ \\t]*(?:public|private|protected|internal)\\b")
NAME = re.compile(r"\\b([A-Za-z_]\\w*)\\s*(?:<[^(){};]*>)?\\s*\\(")

def classify(source, target):
    if not re.fullmatch(r"[A-Za-z_]\\w*", target):
        raise ValueError("Invalid target identifier")
    masked = _executable_positions(source)
    counts = {"block_candidate": 0, "expression_candidate": 0,
              "declaration_unresolved": 0, "call_like_token": 0}
    for match in re.finditer(r"\\b" + re.escape(target) + r"\\s*\\(", masked):
        # A declaration is expected to begin on an access-modifier line.
        line_start = masked.rfind("\\n", 0, match.start()) + 1
        # Permit a multiline return type, bounded to 8 lines / 600 chars.
        prefix_start = max(0, match.start() - 600)
        prefix = masked[prefix_start:match.start()]
        accesses = list(ACCESS.finditer(prefix))
        start = prefix_start + accesses[-1].start() if accesses else None
        if start is None or masked[start:match.start()].count("\\n") > 8:
            counts["call_like_token"] += 1
            continue
        between = masked[start:match.start()]
        # Reject a prior statement/body or a method call in another declaration.
        if any(c in between for c in ";{}=") or not re.search(r"\\s", between):
            counts["call_like_token"] += 1
            continue
        depth, end = 1, None
        for i in range(match.end(), min(len(masked), match.end() + 600)):
            if masked[i] == "(": depth += 1
            elif masked[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end is None:
            counts["declaration_unresolved"] += 1
            continue
        tail = masked[end:end + 300]
        boundary = re.search(r"=>|[;{]", tail)
        if not boundary:
            counts["declaration_unresolved"] += 1
        elif boundary.group() == "=>":
            counts["expression_candidate"] += 1
        elif boundary.group() == "{":
            counts["block_candidate"] += 1
        else:
            counts["declaration_unresolved"] += 1
    counts["target_absence_proven"] = False
    counts["runtime_callability_proven"] = False
    counts["device_tested"] = False
    return counts

if __name__ == "__main__":
    # No raw source or target names in stdout, including failures.
    try:
        source = Path(sys.argv[1]).read_text(encoding="utf-8")
        report = classify(source, sys.argv[2])
        print(json.dumps(report, sort_keys=True))
    except Exception:
        print(json.dumps({"status": "unresolved", "raw_source_disclosed": False}))
        sys.exit(2)
