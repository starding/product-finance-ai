# 行业与职业的 Agent 可达份额（任务加权版）
# 用法：python3 model2.py <下载目录> <编码目录>
# 数据：O*NET 31.0 task_ratings（任务重要度 IM 与频次 FT）、tasks_to_dwas、gwas_to_iwas_to_dwas、job_zones；
#       Eurostat lfsa_eisn2（EU27，2024，NACE 门类 × ISCO 大类就业人数）；IWA 双人编码 code_[AB]_part*.json。
# 方法：任务权重 =（重要度 − 1）× 频次类别均值 → 平均分到该任务的细项活动（DWA）→ 归入中间活动（IWA）
#       → 每个 IWA 有门与三档能力下的可承担比例 r（两位编码员取平均，门不一致时各计一半）
#       → 职业的门构成与可达份额 p → 按 ISCO 大类平均 → 按 NACE 门类的职业构成加权。
import csv, json, sys, collections, glob, math
DL, CD = sys.argv[1], sys.argv[2]
T = ["r_jia", "r_yi", "r_bing"]
A = {x["id"]: x for f in sorted(glob.glob(f"{CD}/code_A_part*.json")) for x in json.load(open(f))}
B = {x["id"]: x for f in sorted(glob.glob(f"{CD}/code_B_part*.json")) for x in json.load(open(f))}
ids = sorted(set(A) & set(B))
# 一致性
agree = sum(A[i]["gate"] == B[i]["gate"] for i in ids) / len(ids)
ca, cb = collections.Counter(A[i]["gate"] for i in ids), collections.Counter(B[i]["gate"] for i in ids)
pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / len(ids) ** 2
kappa = (agree - pe) / (1 - pe)
mad = {t: sum(abs(A[i][t] - B[i][t]) for i in ids) / len(ids) for t in T}
def corr(t):
    x = [A[i][t] for i in ids]; y = [B[i][t] for i in ids]; mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)
rel = {"n_iwa": len(ids), "gate_agree": agree, "gate_kappa": kappa, "r_mad": mad, "r_corr": {t: corr(t) for t in T}}
IWA = {}
for i in ids:
    g = collections.Counter(); g[A[i]["gate"]] += 0.5; g[B[i]["gate"]] += 0.5
    IWA[i] = {"gates": g, "r": {t: (A[i][t] + B[i][t]) / 2 for t in T}}
dwa2iwa = {r["DWA Element ID"]: r["IWA Element ID"] for r in csv.DictReader(open(f"{DL}/gwas_to_iwas_to_dwas.csv"))}
task_dwas = collections.defaultdict(list)
for r in csv.DictReader(open(f"{DL}/tasks_to_dwas.csv")):
    task_dwas[(r["O*NET-SOC Code"], r["Task ID"])].append(r["DWA Element ID"])
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
    iw = [dwa2iwa[d] for d in dw if d in dwa2iwa and dwa2iwa[d] in IWA]
    for x in iw: occw[k[0]][x] += w / len(iw)
exec(open(__file__.replace("model2.py", "isco_map.py")).read())
occ = {}
for c, d in occw.items():
    tot = sum(d.values())
    if tot <= 0 or c not in jz: continue
    g = collections.Counter(); p = collections.Counter()
    for x, w in d.items():
        for gg, s in IWA[x]["gates"].items(): g[gg] += w / tot * s
        for t in T: p[t] += w / tot * IWA[x]["r"][t]
    occ[c] = {"title": titles.get(c, c), "isco": soc_to_isco(c, titles.get(c, ""), jz[c]), "gates": dict(g), "p": dict(p)}
def agg(items):
    n = len(items); g = collections.Counter(); p = collections.Counter()
    for o in items:
        for k, v in o["gates"].items(): g[k] += v / n
        for k, v in o["p"].items(): p[k] += v / n
    return {"n": n, "gates": dict(g), "p": dict(p)}
byI = collections.defaultdict(list)
for o in occ.values():
    if o["isco"]: byI[o["isco"]].append(o)
ISCO = {k: agg(v) for k, v in byI.items()}
eu = json.load(open(f"{DL}/eu.json")); dims, size = eu["id"], eu["size"]
idx = {d: eu["dimension"][d]["category"]["index"] for d in dims}
def val(nace, oc):
    pos = 0
    for d, s in zip(dims, size):
        i = idx[d][nace] if d == "nace_r2" else (idx[d][oc] if d == "isco08" else 0)
        pos = pos * s + i
    return eu["value"].get(str(pos), 0.0) or 0.0
NACE = {}
for nace, lab in eu["dimension"]["nace_r2"]["category"]["label"].items():
    if nace in ("NRP", "U"): continue
    ws = {oc: val(nace, oc) for oc in ISCO if oc != "OC0"}
    tot = sum(ws.values())
    if tot <= 0: continue
    g = collections.Counter(); p = collections.Counter()
    for oc, wv in ws.items():
        for k, v in ISCO[oc]["gates"].items(): g[k] += wv / tot * v
        for k, v in ISCO[oc]["p"].items(): p[k] += wv / tot * v
    NACE[nace] = {"label": lab, "emp_k": tot, "mix": {oc: ws[oc] / tot for oc in ws}, "gates": dict(g), "p": dict(p)}
json.dump({"reliability": rel, "ISCO": ISCO, "NACE": NACE, "occ": occ}, open("aggregates2.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(rel, ensure_ascii=False))
G = ["1", "2", "3", "4d", "4s", "5"]
def line(name, g, p): return f"{name:24s} " + " ".join(f"{k}:{g.get(k,0):.2f}" for k in G) + " | " + " ".join(f"{t[2:]}:{p[t]:.2f}" for t in T) + f" | 上限乙 {1/(1-p['r_yi']):.2f} 丙 {1/(1-p['r_bing']):.2f}"
for c in ["15-1252.00", "53-3032.00", "29-1141.00", "47-2061.00", "13-2011.00", "35-2014.00", "43-4051.00", "13-2051.00", "47-2111.00", "11-1021.00", "25-2021.00", "41-2031.00", "23-1011.00", "37-2012.00"]:
    if c in occ: print(line(occ[c]["title"][:24], occ[c]["gates"], occ[c]["p"]))
print()
for k in sorted(ISCO): print(line(k, ISCO[k]["gates"], ISCO[k]["p"]))
print()
for k, v in sorted(NACE.items(), key=lambda x: -x[1]["p"]["r_yi"]): print(line(f'{k} {v["label"][:20]}', v["gates"], v["p"]))
