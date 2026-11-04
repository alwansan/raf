"""Validate a pinned Raft evidence snapshot, then embed its JSON in offline HTML.

Usage: python scripts/update_dashboard.py
Requires an existing dashboard/data.json, all immutable snapshots, and dashboard/index.html.
Never computes a global product-completion percentage.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
p = root / "dashboard/data.json"
data = json.loads(p.read_text(encoding="utf-8"))
assert data["schema_version"] == 2
assert data["state"] == "NOT_READY"
for key in ("overall_completion_percent", "source_recovery_percent", "phone_acceptance_percent"):
    assert data.get(key) is None, f"Global unknown must be null: {key}"
assert re.fullmatch(r"[0-9a-f]{40}", data["source_sha"])
assert re.fullmatch(r"[0-9a-f]{40}", data["zip2"]["source_sha"])
assert len(data["areas"]) == 7 and len({a["id"] for a in data["areas"]}) == 7
assert len({m["id"] for m in data["metrics"]}) == len(data["metrics"])

for m in data["metrics"]:
    assert type(m["done"]) is int and type(m["total"]) is int
    assert 0 <= m["done"] <= m["total"] and m["total"] > 0
    assert all(m.get(k) for k in ("id","title","unit","inventory_version","weighting","scope","verification","url"))
for a in data["areas"]:
    assert all(a.get(k) for k in ("id","title","state","summary","verified","unverified","blockers","ongoing","next","evidence"))
    assert a["evidence"] and a["state"] in ("partial","blocked","device_pending","unknown")
for key, attr in (("ZIP2-MANIFEST","manifest_file_count"),("RESOURCE-CENSUS",None),("COMPUTE-CENSUS",None)):
    assert any(m["id"] == key for m in data["metrics"])
def measure(i):
    return next(m for m in data["metrics"] if m["id"] == i)
assert measure("ZIP2-MANIFEST")["total"] == data["zip2"]["manifest_file_count"]
assert measure("RESOURCE-CENSUS")["total"] == data["inventory"]["owners"]
assert measure("COMPUTE-CENSUS")["total"] == data["kernel_inventory"]["kernel_rows"]
assert data["kernel_inventory"]["fft_rows"] + data["kernel_inventory"]["blur_rows"] + data["kernel_inventory"]["other_rows"] == data["kernel_inventory"]["kernel_rows"]
assert data["inventory"]["count"] >= max(x["count"] for x in data["inventory"]["top_classes"])
assert data["trial"]["status"] == "completed" and data["trial"]["conclusion"] == "success"
assert data["trial"]["package_signed"] is True and data["trial"]["package_delivered"] is True
assert data["trial"]["device_acceptance"] is None
assert data["trial"]["game_release"] == data["release_checks"]["game"]["url"]
assert any(r["id"] == data["trial"]["run_id"] and r["status"] == "completed" and r["conclusion"] == "success" for r in data["runs"])
assert len({r["id"] for r in data["runs"]}) == len(data["runs"])
assert data["release_checks"]["logger"]["game"] is False
assert data["release_checks"]["game"]["tag"] != data["release_checks"]["logger"]["tag"]
assert data["release_checks"]["game"]["asset_count"] == len(data["release_checks"]["game"]["assets"]) == 12
assert data["previous_game_release"]["tag"].startswith("android-early-test-")
assert data["phone_evidence"]["apk_version_code"] == 86
assert data["phone_evidence"]["source_sha"] is None and data["phone_evidence"]["installed_apk_sha256"] is None
assert data["phone_evidence"]["shader_pass"] == 40327 and data["phone_evidence"]["compute"] == 5555
assert data["team"]["eligible_count"] == 50
assert data["team"]["source_state_directories"] == 36
assert len(data["team"]["not_started_without_directory"]) == 14
assert data["team"]["legacy_retired_count"] == 74
assert len(data["clients"]) == 110
assert len(data["phone_sessions"]) == 6 and sum(p["session_summary_available"] for p in data["phone_sessions"]) == 5

clients = data["clients"]
verification = data["verification"]
assert len(clients) == verification["client_folder_count"]
assert len({c["username"] for c in clients}) == len(clients)
assert sum(c["read_status"] == "file_read" for c in clients) == verification["client_files_refreshed"]
assert sum(c["read_status"] == "previous_snapshot" for c in clients) == verification["client_files_from_prior_snapshot"]
for c in clients:
    assert c["url"] and c["username"] and c["reported_status"]
    assert isinstance(c["work"], list)
    assert c.get("activity_verified") is None
    updated = c.get("updated_at")
    if updated and "T" in updated and re.search(r"(Z|[+-]\d\d:\d\d)$",updated):
        newer = datetime.fromisoformat(updated.replace("Z","+00:00")) > datetime.fromisoformat(data["as_of"].replace("Z","+00:00"))
        assert bool(c.get("timestamp_anomaly")) == newer, c["username"]

external = [m["url"] for m in data["metrics"]]
external += [e["url"] for a in data["areas"] for e in a["evidence"]]
external += [r["url"] for r in data["runs"]]
external += [s["url"] for s in data["sources"]]
external += [c["url"] for c in clients]
external += [data["trial"]["url"], data["trial"]["request_url"], data["inventory"]["source"], data["kernel_inventory"]["source"], data["zip2"]["provider_note"]]
for link in external:
    u = urlparse(link)
    assert (u.scheme,u.hostname) == ("https","github.com") and u.path.startswith("/alwansan/"),link

history = data["snapshot_history"]
assert len({h["path"] for h in history}) == len(history)
current = []
for h in history:
    filepath = (root/"dashboard"/h["path"]).resolve()
    assert filepath.is_relative_to(root.resolve()) and filepath.is_file(),h["path"]
    if h["source_sha"] == data["source_sha"] and h["at"] == data["as_of"]:
        current.append(filepath)
assert len(current) == 1, "A unique immutable current snapshot must exist"
assert json.loads(current[0].read_text(encoding="utf-8")) == data, "Current snapshot differs from dashboard/data.json"

page = root/"dashboard/index.html"
html = page.read_text(encoding="utf-8")
pattern = r'(<script id="snapshot" type="application/json">)[\s\S]*?(</script>)'
assert len(re.findall(pattern,html)) == 1
payload = json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")
result = re.sub(pattern,lambda m:m.group(1)+payload+m.group(2),html)
embedded = re.search(pattern,result).group(0).split(">",1)[1].rsplit("</script>",1)[0]
assert json.loads(embedded) == data
for element in ("trial","bteam","inventory-tiles","inventory-bars","phone-bars","metrics","milestones","areas","clients","runs","delivery","history","next","sources","limits"):
    assert f'id="{element}"' in result
page.write_text(result,encoding="utf-8")
print("PASS: scoped denominators, null unknowns, fixed SHA, 7 tracks, current trial, client evidence, internal/external links, snapshot equality and offline JSON embed")
