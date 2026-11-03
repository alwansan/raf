"""Validate evidence-scoped reporting and embed the JSON in offline HTML.

Run: python scripts/update_dashboard.py
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
source = root / "dashboard/data.json"
data = json.loads(source.read_text(encoding="utf-8"))
assert data["schema_version"] == 2
for key in ("overall_completion_percent", "source_recovery_percent", "phone_acceptance_percent"):
    assert data[key] is None, f"Global progress must remain unknown: {key}"
assert data["state"] == "NOT_READY"
assert re.fullmatch(r"[a-f0-9]{40}", data["source_sha"])
assert len(data["areas"]) == 7 and len({a["id"] for a in data["areas"]}) == 7
assert len({m["id"] for m in data["metrics"]}) == len(data["metrics"])
assert len(data["clients"]) == data["verification"]["client_folder_count"]
assert len({c["username"] for c in data["clients"]}) == len(data["clients"])
assert data["milestones"] and data["snapshot_history"]

for m in data["metrics"]:
    assert type(m["done"]) is int and type(m["total"]) is int
    assert m["total"] > 0 and 0 <= m["done"] <= m["total"]
    assert all(m.get(k) for k in ("id", "unit", "scope", "inventory_version", "weighting", "verification", "url"))
for a in data["areas"]:
    assert all(a.get(k) for k in ("id", "title", "state", "summary", "verified", "unverified", "blockers", "ongoing", "next", "evidence"))
for c in data["clients"]:
    assert c["username"] and c["url"] and c["reported_status"]
for e in [*data["sources"], *[z for a in data["areas"] for z in a["evidence"]]]:
    u = urlparse(e["url"])
    assert (u.scheme, u.hostname) == ("https", "github.com") and u.path.startswith("/alwansan/"), e
for h in data["snapshot_history"]:
    file = (root / "dashboard" / h["path"]).resolve()
    assert file.is_relative_to(root.resolve()) and file.is_file(), h["path"]
    if h["source_sha"] == data["source_sha"] and h["at"] == data["as_of"]:
        assert json.loads(file.read_text(encoding="utf-8")) == data, "Current archived snapshot differs"

page = root / "dashboard/index.html"
html = page.read_text(encoding="utf-8")
pattern = r'(<script id="snapshot" type="application/json">)[\s\S]*?(</script>)'
assert len(re.findall(pattern, html)) == 1, "Expected one offline JSON slot"
encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
result = re.sub(pattern, lambda m: m.group(1) + encoded + m.group(2), html)
assert json.loads(re.search(pattern, result).group(0).split(">", 1)[1].rsplit("</script>", 1)[0]) == data
for element in ("metrics", "milestones", "areas", "clients", "runs", "delivery", "history", "next", "sources", "limits"):
    assert f'id="{element}"' in result
page.write_text(result, encoding="utf-8")
print("PASS: scoped metrics, explicit unknowns, evidence URLs, 7 tracks, client inventory, archive, embedded JSON")
