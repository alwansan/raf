"""Render the current T-team view without copying or resetting the inherited ledger."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.refresh_b_team import build, render


def build_t(ledger):
    data = build(ledger)
    data["source_input_sha256"] = data.pop("input_sha256")
    data["generation"] = "T-2026-11-05"
    for category in ("issues", "resources", "events"):
        for row in data[category]:
            row["_record_path"] = "../B_TEAM/" + row["_record_path"]
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    data["input_sha256"] = hashlib.sha256(encoded).hexdigest()
    return data


def render_t(data):
    return render(data).replace("# ملخص فريق B", "# ملخص فريق T1–T5", 1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, default=Path("prompt/coordination/B_TEAM"))
    p.add_argument("--output", type=Path, default=Path("prompt/coordination/T_TEAM"))
    a = p.parse_args()
    data = build_t(a.ledger)
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / "SUMMARY.md").write_text(render_t(data), encoding="utf-8")
    (a.output / "snapshot.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
