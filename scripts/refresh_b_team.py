"""Deterministic B-team summary from committed issues/resources/events; never infers readiness."""
import argparse
import hashlib
import json
from pathlib import Path

STATUSES = {"OPEN", "IN_PROGRESS", "SOURCE_FIXED", "INTEGRATED", "DEVICE_CONFIRMED",
            "OWNER_CONFIRMED", "DEFERRED", "BLOCKED"}
STAGES = ("acquisition", "extraction", "reconstruction", "binding", "integration", "device")


def read_records(root, folder):
    result = []
    for path in sorted((root / folder).glob("**/*.json")):
        if path.is_symlink():
            raise ValueError("Symlink record refused: " + str(path))
        row = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError("Missing record identity: " + str(path))
        row = dict(row)
        row["_record_path"] = path.relative_to(root).as_posix()
        result.append(row)
    ids = [r["id"] for r in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate " + folder + " record identity")
    return result


def build(root):
    issues = read_records(root, "issues")
    resources = read_records(root, "resources")
    events = read_records(root, "events")
    for row in issues:
        if row.get("status") not in STATUSES:
            raise ValueError("Unknown issue status: " + row["id"])
        if row["status"] in {"SOURCE_FIXED", "INTEGRATED", "DEVICE_CONFIRMED", "OWNER_CONFIRMED"} and not row.get("evidence"):
            raise ValueError("Status without evidence: " + row["id"])
    for row in resources:
        if not isinstance(row.get("stages"), dict) or any(k not in row["stages"] for k in STAGES):
            raise ValueError("Missing resource stages: " + row["id"])
    # Events are history, not authority to silently close an issue.
    data = {"schema_version": 1, "issues": issues, "resources": resources, "events": events,
            "overall_percent": None, "readiness": "NOT_ASSESSED_BY_THIS_SUMMARY"}
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    data["input_sha256"] = hashlib.sha256(encoded).hexdigest()
    return data


def render(data):
    out = ["# ملخص فريق B — مولد من السجلات", "",
           "هذا فهرس أدلة، وليس إعلان جاهزية أو نسبة اكتمال اللعبة. النسبة الكلية غير معلومة.",
           "يُجدد في كل checkpoint؛ ليس خدمة تعمل بين الجلسات.", "",
           "| المشكلة | الأولوية | الحالة | المسار |", "|---|---|---|---|"]
    def cell(value):
        return str(value).replace("|", "/").replace("\n", " ")
    for r in sorted(data["issues"], key=lambda r: ({"P0": 0, "P1": 1, "P2": 2, "DEFERRED": 3}.get(r.get("priority"), 4), r["id"])):
        out.append("| [" + cell(r["id"] + " — " + r.get("title", "")) + "](" +
                   r["_record_path"] + ") | " + cell(r.get("priority", "")) + " | " +
                   cell(r["status"]) + " | " + cell(r.get("track", "")) + " |")
    out += ["", "## الموارد ذات السجل المفصل", "",
            "لكل مورد مراحل منفصلة؛ UNKNOWN لا يعني نجاحاً ولا فشلاً.", ""]
    for r in data["resources"]:
        out.append("- [" + cell(r.get("title", r["id"])) + "](" + r["_record_path"] +
                   "): " + "; ".join(k + "=" + cell(r["stages"][k]) for k in STAGES))
    out += ["", "## الأحداث", ""]
    for r in sorted(data["events"], key=lambda r: (r.get("at", ""), r["id"]))[-30:]:
        out.append("- [" + cell(r.get("at", "") + " / " + r.get("owner", "")) +
                   "](" + r["_record_path"] + "): " + cell(r.get("summary", "")))
    out += ["", "بصمة المدخلات: " + data["input_sha256"], ""]
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("prompt/coordination/B_TEAM"))
    a = p.parse_args()
    data = build(a.root)
    (a.root / "snapshot.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (a.root / "SUMMARY.md").write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
