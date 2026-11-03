"""Validate evidence snapshot and embed JSON into standalone HTML. Run: python scripts/update_dashboard.py"""
import json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/"dashboard/data.json").read_text(encoding="utf-8"))
assert data["schema_version"]==2
assert data["overall_completion_percent"] is None and data["source_recovery_percent"] is None and data["phone_acceptance_percent"] is None
assert re.fullmatch(r"[0-9a-f]{40}",data["source_sha"])
assert len(data["areas"])==7 and len({a["id"] for a in data["areas"]})==7
assert len(data["clients"])==data["verification"]["client_folder_count"]
for m in data["metrics"]:
    assert type(m["done"]) is int and type(m["total"]) is int
    assert m["total"]>0 and 0<=m["done"]<=m["total"]
    assert m["inventory_version"] and m["weighting"] and m["scope"] and m["url"].startswith("https://")
for a in data["areas"]:
    assert all(a.get(k) for k in ("id","title","summary","verified","unverified","blockers","ongoing","next","evidence"))
for h in data["snapshot_history"]:
    assert (root/"dashboard"/h["path"]).resolve().is_relative_to(root.resolve())
    assert (root/"dashboard"/h["path"]).resolve().is_file(),h["path"]
p=root/"dashboard/index.html"
html=p.read_text(encoding="utf-8")
pattern=r'(<script id="snapshot" type="application/json">)[\s\S]*?(</script>)'
assert len(re.findall(pattern,html))==1
payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")
out=re.sub(pattern,lambda m:m.group(1)+payload+m.group(2),html)
actual=re.search(pattern,out).group(0).split(">",1)[1].rsplit("</script>",1)[0]
assert json.loads(actual)==data
for name in ("metrics","areas","clients","runs","delivery","history","next","sources","limits"):
    assert ('id="'+name+'"') in out
p.write_text(out,encoding="utf-8")
print("PASS: JSON, bounds, local snapshot links, client count, embedded data, section ids")
