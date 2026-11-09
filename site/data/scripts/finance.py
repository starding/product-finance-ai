# 金融保险行业：职业与任务两层的门构成与 Agent 可达份额
# 用法：python3 finance.py <下载目录> <编码目录> → finance.json
# 与 model2.py 同一口径；O*NET 中无任务评分的职业（金融与投资分析师、金融风险专员），核心任务权重记 1、补充任务记 0.5，并标注。
import csv, json, sys, collections, glob
DL, CD = sys.argv[1], sys.argv[2]
T = ["r_jia", "r_yi", "r_bing"]
A = {x["id"]: x for f in glob.glob(f"{CD}/code_A_part*.json") for x in json.load(open(f))}
B = {x["id"]: x for f in glob.glob(f"{CD}/code_B_part*.json") for x in json.load(open(f))}
IWA = {}
for i in A:
    g = collections.Counter(); g[A[i]["gate"]] += 0.5; g[B[i]["gate"]] += 0.5
    IWA[i] = {"gates": g, "r": {t: (A[i][t] + B[i][t]) / 2 for t in T}}
dwa2iwa = {r["DWA Element ID"]: r["IWA Element ID"] for r in csv.DictReader(open(f"{DL}/gwas_to_iwas_to_dwas.csv"))}
GROUPS = [
 ("银行与信贷", [("13-2072.00", "贷款专员"), ("13-2041.00", "信用分析师"), ("13-2071.00", "信贷咨询师"), ("43-4131.00", "贷款面谈与经办员"), ("43-4041.00", "授信审核员"), ("43-3071.00", "银行柜员"), ("43-3011.00", "账款催收员")]),
 ("证券与资产管理", [("11-3031.03", "投资基金经理"), ("13-2051.00", "金融与投资分析师"), ("13-2099.01", "金融量化分析师"), ("13-2054.00", "金融风险专员"), ("13-2052.00", "个人理财顾问"), ("41-3031.00", "证券与金融服务销售（经纪人）"), ("43-4011.00", "证券经纪业务文员")]),
 ("保险", [("15-2011.00", "精算师"), ("13-2053.00", "核保员"), ("41-3021.00", "保险销售代理"), ("13-1031.00", "理赔调查员"), ("13-1032.00", "车险定损员"), ("43-9041.00", "理赔与保单处理文员")]),
 ("各子行业共有的职能", [("11-3031.00", "财务经理"), ("13-1041.00", "合规专员"), ("13-2099.04", "反欺诈调查与分析师"), ("13-2011.00", "会计与审计"), ("43-4051.00", "客户服务代表"), ("15-1252.00", "软件开发人员")]),
]
codes = {c for _, l in GROUPS for c, _ in l}
tasks = {}
for r in csv.DictReader(open(f"{DL}/task_statements.csv")):
    if r["O*NET-SOC Code"] in codes: tasks[(r["O*NET-SOC Code"], r["Task ID"])] = {"text": r["Task"], "type": r["Task Type"]}
im, ft = {}, collections.defaultdict(float)
for r in csv.DictReader(open(f"{DL}/task_ratings.csv")):
    k = (r["O*NET-SOC Code"], r["Task ID"])
    if k not in tasks: continue
    if r["Scale ID"] == "IM": im[k] = float(r["Data Value"])
    elif r["Scale ID"] == "FT" and r["Category"]: ft[k] += int(r["Category"]) * float(r["Data Value"]) / 100
tdw = collections.defaultdict(list)
for r in csv.DictReader(open(f"{DL}/tasks_to_dwas.csv")):
    k = (r["O*NET-SOC Code"], r["Task ID"])
    if k in tasks and r["DWA Element ID"] in dwa2iwa: tdw[k].append((dwa2iwa[r["DWA Element ID"]], r["DWA Element Name"]))
out = []
for gname, lst in GROUPS:
    for c, cn in lst:
        rated = any(k in im for k in tasks if k[0] == c)
        rows = []
        for k, tv in tasks.items():
            if k[0] != c or not tdw.get(k): continue
            w = max(im[k] - 1, 0) * ft[k] if rated and k in im and k in ft else (1.0 if tv["type"] == "Core" else 0.5)
            iws = [i for i, _ in tdw[k] if i in IWA]
            if not iws or w <= 0: continue
            g = collections.Counter(); r_ = {t: 0.0 for t in T}
            for i in iws:
                for gg, s in IWA[i]["gates"].items(): g[gg] += s / len(iws)
                for t in T: r_[t] += IWA[i]["r"][t] / len(iws)
            rows.append({"id": k[1], "text": tv["text"], "w": w, "gates": dict(g), "r": r_, "dwas": [d for _, d in tdw[k]]})
        tot = sum(x["w"] for x in rows)
        for x in rows: x["share"] = x["w"] / tot
        G = collections.Counter(); P = {t: 0.0 for t in T}
        for x in rows:
            for gg, s in x["gates"].items(): G[gg] += x["share"] * s
            for t in T: P[t] += x["share"] * x["r"][t]
        rows.sort(key=lambda x: -x["share"])
        out.append({"group": gname, "code": c, "name": cn, "rated": rated, "n_tasks": len(rows), "gates": dict(G), "p": P, "tasks": rows})
json.dump(out, open("finance.json", "w"), ensure_ascii=False, indent=1)
for o in out:
    g = o["gates"]; p = o["p"]
    print(f'{o["group"][:4]} {o["name"]:14s} 任务{o["n_tasks"]:3d} {"" if o["rated"] else "（等权）"} 4d {g.get("4d",0):.2f} 4s {g.get("4s",0):.2f} 2 {g.get("2",0):.2f} 5 {g.get("5",0):.2f} 1 {g.get("1",0):.2f} 3 {g.get("3",0):.2f} | 甲 {p["r_jia"]:.2f} 乙 {p["r_yi"]:.2f} 丙 {p["r_bing"]:.2f} 上限乙 {1/(1-p["r_yi"]):.2f}')
