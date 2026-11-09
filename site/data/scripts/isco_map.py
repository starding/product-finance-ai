# SOC → ISCO-08 大类的近似对应（按 SOC 大类、工作区间与职业名称）
def soc_to_isco(code, title, jz):
    m = int(code[:2]); t = title.lower()
    if m == 11: return "OC1"
    if m in (13, 15, 17, 19, 21, 23, 25, 27, 29): return "OC2" if jz >= 4 else "OC3"
    if m in (31, 33, 39): return "OC5"
    if m == 35: return "OC9" if jz <= 1 else "OC5"
    if m == 37: return "OC9"
    if m == 41: return "OC3" if jz >= 3 else "OC5"
    if m == 43: return "OC4"
    if m == 45: return "OC9" if jz <= 1 else "OC6"
    if m == 47: return "OC9" if ("helper" in t or "laborer" in t) else ("OC8" if "operator" in t else "OC7")
    if m == 49: return "OC9" if "helper" in t else "OC7"
    if m == 51: return "OC8" if any(k in t for k in ("operator", "tender", "assembler")) else ("OC9" if "helper" in t else "OC7")
    if m == 53: return "OC9" if ("laborer" in t or "hand" in t or "cleaner" in t) else "OC8"
    if m == 55: return "OC0"
    return None

