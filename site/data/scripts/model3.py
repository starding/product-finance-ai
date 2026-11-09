# 活动级：每项中间工作活动（IWA）占全部工作时间的比重（欧盟 27 国 2024 年就业结构加权）
# 用法：python3 model3.py onet31 codes → gang/iwa_level.json
# 方法同 model2.py：任务权重 =（重要度 − 1）× 频次 → 平均分到细项活动 → 归入 IWA → 职业内份额 → ISCO 大类平均 → 按全部行业的职业构成加权
import csv, json, sys, collections, glob
DL, CD = sys.argv[1], sys.argv[2]
IDS = {x['id'] for x in json.load(open(f'{CD}/iwas.json'))}
dwa2iwa = {r["DWA ID"] if "DWA ID" in r else r["DWA Element ID"]: (r["IWA ID"] if "IWA ID" in r else r["IWA Element ID"]) for r in csv.DictReader(open(f"{DL}/gwas_to_iwas_to_dwas.csv"))}
task_dwas = collections.defaultdict(list)
for r in csv.DictReader(open(f"{DL}/tasks_to_dwas.csv")):
    task_dwas[(r["O*NET-SOC Code"], r["Task ID"])].append(r.get("DWA ID") or r["DWA Element ID"])
im, ft = {}, collections.defaultdict(float)
for r in csv.DictReader(open(f"{DL}/task_ratings.csv")):
    k = (r["O*NET-SOC Code"], r["Task ID"])
    if r["Scale ID"] == "IM": im[k] = float(r["Data Value"])
    elif r["Scale ID"] == "FT" and r["Category"]: ft[k] += int(r["Category"]) * float(r["Data Value"]) / 100
titles = {r["O*NET-SOC Code"]: r["Title"] for r in csv.DictReader(open(f"{DL}/occupation_data.csv"))}
jz = {r["O*NET-SOC Code"]: int(r["Job Zone"]) for r in csv.DictReader(open(f"{DL}/job_zones.csv"))}
occw = collections.defaultdict(lambda: collections.defaultdict(float))
for k, dw in task_dwas.items():
    if k not in im or k not in ft: continue
    w = max(im[k] - 1, 0) * ft[k]
    iw = [dwa2iwa[d] for d in dw if d in dwa2iwa and dwa2iwa[d] in IDS]
    for x in iw: occw[k[0]][x] += w / len(iw)
exec(open(__file__.replace("model3.py", "isco_map.py")).read())
byI = collections.defaultdict(list)
for c, d in occw.items():
    tot = sum(d.values())
    if tot <= 0 or c not in jz: continue
    i = soc_to_isco(c, titles.get(c, ""), jz[c])
    if i: byI[i].append({x: v / tot for x, v in d.items()})
ISCO = {i: {x: sum(o.get(x, 0) for o in L) / len(L) for x in IDS} for i, L in byI.items()}
eu = json.load(open(f"{DL}/eu.json")); dims, size = eu["id"], eu["size"]
idx = {d: eu["dimension"][d]["category"]["index"] for d in dims}
def val(nace, oc):
    pos = 0
    for d, s in zip(dims, size):
        i = idx[d][nace] if d == "nace_r2" else (idx[d][oc] if d == "isco08" else 0)
        pos = pos * s + i
    return eu["value"].get(str(pos), 0.0) or 0.0
ws = {oc: val("TOTAL", oc) for oc in ISCO if oc != "OC0"}; T = sum(ws.values())
share = {x: sum(ws[oc] / T * ISCO[oc][x] for oc in ws) for x in IDS}
json.dump(share, open(f"{CD}/../gang/iwa_share.json", "w"), ensure_ascii=False, indent=0)
print(len(share), sum(share.values()), sorted(share.items(), key=lambda z: -z[1])[:5])
