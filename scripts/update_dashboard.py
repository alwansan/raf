"""Validate snapshot and embed it into the standalone dashboard."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/"dashboard/data.json").read_text())
assert data["overall_completion_percent"] is None, "No global completion metric defined"
assert re.fullmatch("[0-9a-f]{40}",data["source_sha"])
for row in data["metrics"]:
    assert type(row["done"]) is int and type(row["total"]) is int
    assert row["total"]>0 and 0<=row["done"]<=row["total"]
    assert row["scope"] and row["url"].startswith("https://github.com/alwansan/raf/")
for row in data["areas"]:
    assert row["id"] and row["summary"] and row["url"].startswith("https://")
p=root/"dashboard/index.html"
text=p.read_text()
payload=json.dumps(data,ensure_ascii=False).replace("<","\\u003c")
pattern=r'(<script id="snapshot" type="application/json">)[\s\S]*?(</script>)'
assert len(re.findall(pattern,text))==1
p.write_text(re.sub(pattern,lambda m:m[1]+payload+m[2],text))
print("Validated scoped metrics, source SHA and standalone embedded snapshot")
