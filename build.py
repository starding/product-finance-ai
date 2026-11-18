# 用法：python3 build.py → 由 chapters/*.md 与 figs/*.html 生成 site/*.html 和封面 site/index.html；site/book.css 内嵌进每一页。
# 每页左侧为全书目录侧边栏（窄屏收为抽屉），上一篇、下一篇按 TOC 中已写的篇目自动生成。
# 文稿格式：开头 --- 包住的元数据；<!-- body --> 之前是版本记录，不进网页；正文中单独一行 {{fig:名称}} 插入 figs/名称.html，
# {{formula:分子|分母}} 插入分式；{{principles:部分序号}} 插入该部分的“原理的位置”总图（由各章原理卡自动汇总）。
# 双语：中文源在 chapters/、gen/、figs/、cover.md，英文源在 en/ 下同名文件；中文输出 site/，英文输出 site/en/。界面文字见 UI。
# 原理卡：以 :::原理 名称（第二部分重新审视已有原理时用 :::重跑 名称）开头、::: 结尾；首行是一句话表述，其后每行“字段：内容”（学科、类型、地位、约束、前提、提出、问题、重跑）。
import html, pathlib, re

ROOT = pathlib.Path(__file__).parent
BOOK = "产品×金融×AI：AI 时代的金融产品"
CSS = (ROOT / "site" / "book.css").read_text()
LANG = "zh"          # 当前语言：zh 或 en
SRC = ROOT           # 源文件根目录：中文为 ROOT，英文为 ROOT/en
OUT = ROOT / "site"  # 输出目录：中文为 site/，英文为 site/en/

# 界面文字：键为中文原文，英文版按此替换
UI_EN = {
    "关于本书": "About this book", "分解式": "Decomposition", "生成式": "Derivation",
    "全书目录": "Contents", "阅读方式": "Way of reading", "展开目录": "Open contents", "收起目录": "Close contents", "目录": "Contents",
    "附录": "Appendix", "结语": "Epilogue", "序": "Preface", "封面": "Cover",
    "资料截至": "Data as of", "从序开始阅读 →": "Start with the preface →", "本章在回报等式中的位置": "Where this chapter sits in the return equation",
    "实际回报 ＝": "Realized return =", "前提：承诺得到兑现": "Premise: promises kept",
    "推演至此，得到一条原理": "Derived so far: a principle", "重跑至此，重新检验一条原理": "Rerun: a principle re-examined",
    "在学科中的位置": "Standing in the field", "回应的约束": "Constraint it answers", "成立的前提": "Premises", "提出者": "Proposed by",
    "留下的问题": "Open question", "重跑之后": "After the rerun", "学科": "Discipline", "类型": "Type",
    "时间补偿": "Time compensation", "风险补偿": "Risk compensation", "信息优势": "Information advantage", "交易成本": "Trading costs", "运气": "Luck",
    "交互式网页书": "An interactive web book", "次阅读": "views", "English": "中文",
}
def ui(t):
    return UI_EN.get(t, t) if LANG == "en" else t


# 目录：(文件名, 编号, 标题, 所属部分)；文件名为空表示尚未写
TOC = [
    ("preface", "序", "为什么金融产品在 AI 时代需要重新学", None),
    ("part1", "第一部分", "市场：收益与风险从何而来", "part"),
    ("ch01", "第 1 章", "金融产品卖的是什么", 1),
    ("", "第一篇", "时间补偿", "sec"),
    ("ch02", "第 2 章", "利率与期限", 1),
    ("", "第二篇", "风险补偿", "sec"),
    ("ch03", "第 3 章", "风险长什么样", 1),
    ("ch04", "第 4 章", "分散：哪些风险有补偿", 1),
    ("ch05", "第 5 章", "复利与波动拖累", 1),
    ("ch06", "第 6 章", "因子：风险补偿可以分解", 1),
    ("", "第三篇", "信息优势", "sec"),
    ("ch07", "第 7 章", "价格为什么难以预测", 1),
    ("ch08", "第 8 章", "信息如何进入价格", 1),
    ("ch09", "第 9 章", "市场里的交易者", 1),
    ("", "第四篇", "交易成本", "sec"),
    ("ch10", "第 10 章", "流动性与买卖价差", 1),
    ("ch11", "第 11 章", "订单、规则与市场结构", 1),
    ("", "第五篇", "运气与技能", "sec"),
    ("ch12", "第 12 章", "主动管理的算术", 1),
    ("", "第六篇", "兑现的前提", "sec"),
    ("ch13", "第 13 章", "承诺如何被兑现", 1),
    ("ch14", "第 14 章", "监管为何存在", 1),
    ("part2", "第二部分", "用户：人要什么、能承受什么", "part"),
    ("ch15", "第 15 章", "用户要完成的任务", 2),
    ("ch16", "第 16 章", "用户如何做决定", 2),
    ("ch17", "第 17 章", "用户能承受什么", 2),
    ("ch18", "第 18 章", "用户如何判断与信任", 2),
    ("part3", "第三部分", "AI：代理能替人做多少", "part"),
    ("ch19", "第 19 章", "放大倍数：理论与实测", 3),
    ("ch20", "第 20 章", "哪些事务能交给 AI", 3),
    ("ch21", "第 21 章", "能力从哪里来、在哪里失效", 3),
    ("ch22", "第 22 章", "可验证性：核对的成本", 3),
    ("ch23", "第 23 章", "金融场景的特殊约束", 3),
    ("part4", "第四部分", "设计：在三组约束下设计金融产品", "part"),
    ("", "价值层", "承诺什么", "sec"),
    ("ch24", "第 24 章", "承诺什么", 4),
    ("", "契约层", "按什么条件", "sec"),
    ("ch25", "第 25 章", "委托参数：交代的目标与约束", 4),
    ("ch26", "第 26 章", "授权与不可逆敞口", 4),
    ("ch27", "第 27 章", "责任与利益冲突", 4),
    ("", "实现层", "如何兑现", "sec"),
    ("ch28", "第 28 章", "能力装配与过程可见", 4),
    ("ch29", "第 29 章", "保障强度", 4),
    ("", "信任", "长期关系", "sec"),
    ("ch30", "第 30 章", "信任如何建立", 4),
    ("", "总结", "回到三组约束", "sec"),
    ("ch31", "第 31 章", "设计原则", 4),
    ("estimates", "附录", "作者估算的方法与数据", "app"),
    ("method", "附录", "本书的写法", "app"),
]

TOC_EN = [
    ("preface", "Preface", "Why financial products must be relearned in the age of AI", None),
    ("part1", "Part One", "Markets: where returns and risks come from", "part"),
    ("ch01", "Chapter 1", "What financial products sell", 1),
    ("", "Section One", "Time compensation", "sec"),
    ("ch02", "Chapter 2", "Interest rates and maturity", 1),
    ("", "Section Two", "Risk compensation", "sec"),
    ("ch03", "Chapter 3", "What risk looks like", 1),
    ("ch04", "Chapter 4", "Diversification: which risks are rewarded", 1),
    ("ch05", "Chapter 5", "Compounding and volatility drag", 1),
    ("ch06", "Chapter 6", "Factors: risk compensation can be decomposed", 1),
    ("", "Section Three", "Information advantage", "sec"),
    ("ch07", "Chapter 7", "Why prices are hard to predict", 1),
    ("ch08", "Chapter 8", "How information gets into prices", 1),
    ("ch09", "Chapter 9", "Traders in the market", 1),
    ("", "Section Four", "Trading costs", "sec"),
    ("ch10", "Chapter 10", "Liquidity and the bid-ask spread", 1),
    ("ch11", "Chapter 11", "Orders, rules and market structure", 1),
    ("", "Section Five", "Luck and skill", "sec"),
    ("ch12", "Chapter 12", "The arithmetic of active management", 1),
    ("", "Section Six", "The premise of delivery", "sec"),
    ("ch13", "Chapter 13", "How promises are kept", 1),
    ("ch14", "Chapter 14", "Why regulation exists", 1),
    ("part2", "Part Two", "Users: what people want and what they can bear", "part"),
    ("ch15", "Chapter 15", "The jobs users need done", 2),
    ("ch16", "Chapter 16", "How users decide", 2),
    ("ch17", "Chapter 17", "What users can bear", 2),
    ("ch18", "Chapter 18", "How users judge and trust", 2),
    ("part3", "Part Three", "AI: how much an agent can do on people's behalf", "part"),
    ("ch19", "Chapter 19", "The amplification factor: theory and measurement", 3),
    ("ch20", "Chapter 20", "Which tasks can be handed to AI", 3),
    ("ch21", "Chapter 21", "Where capability comes from and where it fails", 3),
    ("ch22", "Chapter 22", "Verifiability: the cost of checking", 3),
    ("ch23", "Chapter 23", "Constraints peculiar to finance", 3),
    ("part4", "Part Four", "Design: financial products under three sets of constraints", "part"),
    ("", "Value layer", "What to promise", "sec"),
    ("ch24", "Chapter 24", "What to promise", 4),
    ("", "Contract layer", "On what terms", "sec"),
    ("ch25", "Chapter 25", "Mandate parameters: the goals and limits handed over", 4),
    ("ch26", "Chapter 26", "Authority and irreversible exposure", 4),
    ("ch27", "Chapter 27", "Liability and conflicts of interest", 4),
    ("", "Implementation layer", "How to deliver", "sec"),
    ("ch28", "Chapter 28", "Capability assembly and process visibility", 4),
    ("ch29", "Chapter 29", "Assurance level", 4),
    ("", "Trust", "The long-term relationship", "sec"),
    ("ch30", "Chapter 30", "How trust is built", 4),
    ("", "Summary", "Back to the three constraints", "sec"),
    ("ch31", "Chapter 31", "Design principles", 4),
    ("estimates", "Appendix", "The author's estimates: methods and data", "app"),
    ("method", "Appendix", "How this book was written", "app"),
]
TOC_ZH = TOC
DONE = {t[0] for t in TOC if t[0]}
WRITTEN = [t for t in TOC if t[0] in DONE]
# 侧栏顶部与底部：书名链接、关于本书、另一种读法；生成式版本（build_gen.py）会改写这些设置
HOME, HOME_TITLE, HOME_SUB = "index.html", "产品×金融×AI", "AI 时代的金融产品"
ABOUT = ("index.html#about", "关于本书")
OTHER = None
VIEW = "d"  # 当前视图：d 分解式，g 生成式；目录顶部可切换
VIEWS = [("d", "分解式", "preface.html"), ("g", "生成式", "g-preface.html")]

# 回报等式的各项：(键, 名称, 符号, 该篇第一章)
TERMS = [("time", "时间补偿", "＋", "ch02"), ("risk", "风险补偿", "＋", "ch03"), ("info", "信息优势", "＋", "ch07"),
         ("cost", "交易成本", "－", "ch10"), ("luck", "运气", "＋", "")]

def term_strip(term):
    """章首的等式位置条：高亮本章对应的一项"""
    items = []
    for i, (k, name, sign, f) in enumerate(TERMS):
        cls = "cur" if k == term else ""
        lab = (sign if i else "") + ui(name)
        items.append(f'<a class="{cls}" href="{f}.html">{lab}</a>' if f and k != term else f'<span class="{cls}">{lab}</span>')
    pk = ui("前提：承诺得到兑现")
    keep = f'<span class="cur">{pk}</span>' if term == "keep" else f'<a href="ch13.html">{pk}</a>'
    return f'<div class="eqstrip" aria-label="{ui("本章在回报等式中的位置")}"><span class="lbl">{ui("实际回报 ＝")}</span>' + "".join(items) + f'<span class="keep">{keep}</span></div>'


# 访问统计：与博客 xinghua.space 同一个自建统计服务（不用 cookie、不存 IP）。正式域名上每打开一页计一次并取回这一页的累计数，
# 本地预览只读不计；页头显示「N 次阅读」，取不到就不显示。
STATS = """<script>(()=>{if(navigator.webdriver)return;const S='https://xinghua-stats.xinghua-space.workers.dev',P=location.pathname;const got=location.hostname==='xinghua.space'?fetch(S+'/c',{method:'POST',keepalive:true,body:JSON.stringify({p:P,r:document.referrer,w:innerWidth,l:navigator.language})}):fetch(S+'/v?p='+encodeURIComponent(P));const ready=new Promise(r=>document.readyState==='loading'?addEventListener('DOMContentLoaded',r):r());Promise.all([got.then(r=>r.ok?r.json():null),ready]).then(([d])=>{const n=d&&d.page.views;if(!n)return;for(const e of document.querySelectorAll('[data-stat="page-views"]')){e.textContent=n.toLocaleString('en');e.closest('[hidden]')?.removeAttribute('hidden')}}).catch(()=>{})})()</script>"""

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
{css}</style>
{stats}
</head>
<body data-page="{page}">
<script>try{{if(document.body.dataset.page==='index'||localStorage.getItem('book-side')==='c')document.body.classList.add('side-collapsed');}}catch(e){{}}</script>
{side}
<button class="sidetoggle" type="button" aria-controls="sidenav" aria-expanded="false" aria-label="{l_open}" title="{l_toc}"><svg viewBox="0 0 20 20" aria-hidden="true"><rect x="2.5" y="3.5" width="15" height="13" rx="2.5"/><line x1="7.5" y1="3.5" x2="7.5" y2="16.5"/><path class="chev" d="M11 7.5 L13.5 10 L11 12.5"/></svg></button>
<div class="scrim" data-close></div>
{pre}<div class="wrap">
<header class="book"><a class="booklink" href="{home}">{book}</a><span>{part}<span class="views" hidden> · <span data-stat="page-views"></span> {l_views}</span></span><a class="langlink" href="{other}" hreflang="{olang}">{olabel}</a></header>
"""

TAIL = """</div>
<script>
(function(){
  // 目录：宽度 ≥760px 时与正文同层并排，展开时把正文推向右侧，可收起与重新固定，状态记在本机；手机宽度时为抽屉
  const b=document.body, tg=document.querySelector('.sidetoggle'), wide=matchMedia('(min-width:760px)');
  const save=v=>{try{localStorage.setItem('book-side',v)}catch(e){}};
  const isOpen=()=>wide.matches?!b.classList.contains('side-collapsed'):b.classList.contains('nav-open');
  const sync=()=>{const o=isOpen();tg.setAttribute('aria-expanded',String(o));tg.setAttribute('aria-label',o?(document.documentElement.lang==='en'?'Close contents':'收起目录'):(document.documentElement.lang==='en'?'Open contents':'展开目录'));tg.classList.toggle('is-open',o);};
  const setOpen=o=>{b.classList.toggle('nav-open',o);sync();};
  const setCollapsed=c=>{b.classList.toggle('side-collapsed',c);save(c?'c':'o');sync();};
  tg.addEventListener('click',()=>{if(wide.matches)setCollapsed(isOpen());else setOpen(!isOpen());});
  document.querySelectorAll('[data-close], .side a').forEach(el=>el.addEventListener('click',()=>{if(!wide.matches)setOpen(false);}));
  wide.addEventListener('change',sync);sync();
  addEventListener('keydown',e=>{if(e.key==='Escape'&&!wide.matches)setOpen(false);});
  // 动画：带 data-anim 的元素进入视野时加上 in 并派发 anim-in；data-replay 按钮重播
  const fire=t=>{t.classList.remove('in');void t.offsetWidth;t.classList.add('in');t.dispatchEvent(new Event('anim-in'));};
  if('IntersectionObserver' in window){
    const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){fire(e.target);io.unobserve(e.target);}}),{threshold:.3});
    document.querySelectorAll('[data-anim]').forEach(el=>io.observe(el));
  } else document.querySelectorAll('[data-anim]').forEach(fire);
  document.querySelectorAll('[data-replay]').forEach(x=>x.addEventListener('click',()=>fire(document.getElementById(x.dataset.replay))));
  const side=document.querySelector('.side'), cur=side.querySelector('a.cur:not(.sidetitle)'); if(cur) side.scrollTop=cur.offsetTop-side.clientHeight/3;
})();
</script>
</body>
</html>
"""

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<i>\1</i>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
    return t

def md(body):
    """返回 (正文 HTML, 小节列表 [(锚点, 标题)])"""
    JOIN = " " if LANG == "en" else ""
    out, heads, lines, i, listcls = [], [], body.split("\n"), 0, ""
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1; continue
        if m := re.match(r"\{\{fig:([\w-]+)\}\}$", l.strip()):
            out.append((SRC / "figs" / f"{m[1]}.html").read_text()); i += 1; continue
        if m := re.match(r"\{\{principles:(\d)\}\}$", l.strip()):
            import principles_fig
            out.append(principles_fig.figure(TOC, int(m[1]), LANG, SRC)); i += 1; continue
        if m := re.match(r"\{\{formula:(.+)\|(.+)\}\}$", l.strip()):
            out.append(f'<div class="formula"><span>{inline(m[1])}</span><span class="bar"></span><span class="den">{inline(m[2])}</span></div>'); i += 1; continue
        if l.startswith((":::原理", ":::重跑", ":::principle", ":::rerun")):
            kick = ui("推演至此，得到一条原理" if l.startswith((":::原理", ":::principle")) else "重跑至此，重新检验一条原理")
            name, i = l[3:].split(" ", 1)[1].strip() if " " in l[3:] else "", i + 1
            buf = []
            while i < len(lines) and lines[i].strip() != ":::":
                if lines[i].strip(): buf.append(lines[i].strip())
                i += 1
            i += 1
            EN_KEYS = {"Discipline": "学科", "Type": "类型", "Standing": "地位", "Constraint": "约束", "Premises": "前提", "Proposed": "提出", "Question": "问题", "Rerun": "重跑"}
            f = {}
            for x in buf[1:]:
                k, v = (x.split("：", 1) if "：" in x else x.split(": ", 1))
                f[EN_KEYS.get(k.strip(), k.strip())] = v.strip()
            chips = "".join(f'<span><em>{ui(k)}</em>{inline(f[k])}</span>' for k in ("学科", "类型") if k in f)
            labels = {"地位": "在学科中的位置", "约束": "回应的约束", "前提": "成立的前提", "提出": "提出者", "问题": "留下的问题", "重跑": "重跑之后"}
            rows = "".join(f'<div><dt>{ui(labels[k])}</dt><dd>{inline(f[k])}</dd></div>' for k in labels if k in f)
            out.append(f'<aside class="principle"><p class="pr-k">{kick}</p><p class="pr-n">{inline(name)}</p><p class="pr-c">{chips}</p><p class="pr-s">{inline(buf[0])}</p><dl>{rows}</dl></aside>'); continue
        if l.startswith("## "):
            h = l[3:].strip()
            listcls = {"参考文献": "refs", "口径与局限": "notes", "几点约定": "notes", "References": "refs", "Scope and limitations": "notes", "Conventions": "notes"}.get(h, "")
            sid = f"sec-{len(heads) + 1}"
            heads.append((sid, h))
            out.append(f'<h2 id="{sid}">{inline(h)}</h2>'); i += 1; continue
        if l.startswith("### "):
            out.append(f"<h3>{inline(l[4:].strip())}</h3>"); i += 1; continue
        if l.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip()); i += 1
            paras = "\n".join(buf).split("\n\n")
            out.append("<blockquote>" + "".join(f"<p>{inline(p.replace(chr(10), JOIN))}</p>" for p in paras if p.strip()) + "</blockquote>"); continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body_rows = rows[0], rows[2:]
            t = "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body_rows) + "</tbody>"
            out.append(f'<div class="tablewrap"><table>{t}</table></div>'); continue
        if re.match(r"(- |\d+\. )", l):
            tag = "ol" if re.match(r"\d+\. ", l) else "ul"
            items = []
            while i < len(lines) and (re.match(r"(- |\d+\. )", lines[i]) or (lines[i].startswith("   ") and items)):
                if re.match(r"(- |\d+\. )", lines[i]):
                    items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                else:
                    items[-1] += JOIN + lines[i].strip()
                i += 1
            cls = f' class="{listcls}"' if listcls else ""
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(#|>|\||- |\d+\. |\{\{|:::)", lines[i]):
            buf.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(JOIN.join(buf))}</p>")
    return "\n".join(out), heads

def sidebar(current, heads=()):
    """全书目录：两层，部分标题（即导读链接）与各章；当前篇目高亮"""
    def link(f, label, cls=""):
        c = " cur" if f == current else ""
        cur = ' aria-current="page"' if f == current else ""
        return f'<a class="{cls}{c}" href="{f}.html"{cur}>{label}</a>'
    out = [f'<nav class="side" id="sidenav" aria-label="{ui("全书目录")}">',
           f'<div class="side-head"><a class="sidetitle" href="{HOME}">{HOME_TITLE}<small>{HOME_SUB}</small></a></div>',
           f'<div class="side-view" role="group" aria-label="{ui("阅读方式")}">' + "".join(
               f'<a href="{u}"' + (' class="on" aria-current="true"' if v == VIEW and current != "index" else "") + f'>{ui(n)}</a>' for v, n, u in VIEWS) + "</div>"]
    if ABOUT:
        out.append('<a class="side-about' + (' cur" aria-current="page' if current == "index" else '') + f'" href="{ABOUT[0]}">{ui(ABOUT[1])}</a>')
    for f, no, title, part in TOC:
        if part == "sec" or not f:
            continue
        if part is None:
            lab, cls = f'<span class="n">{no}</span>{html.escape(title)}', "side-app" if no in ("结语", "Epilogue") else ""
        elif part == "part":
            lab, cls = f'<span class="pn">{no}</span>{html.escape(title)}', "side-part"
        elif part == "app":
            lab, cls = f'<span class="n">{ui("附录")}</span>{html.escape(title)}', "side-app"
        else:
            lab, cls = f'<span class="n">{no.replace("第 ", "").replace(" 章", "").replace("Chapter ", "")}</span>{html.escape(title)}', ""
        out.append(link(f, lab, cls) if f in DONE else f'<span class="todo {cls}">{lab}</span>')
    if OTHER:
        out.append(f'<a class="side-other" href="{OTHER[0]}">{OTHER[1]} →</a>')
    out.append("</nav>")
    return "\n".join(out)

def parse(path):
    s = path.read_text()
    _, fm, rest = s.split("---\n", 2)
    meta = dict(re.match(r"(\w+):\s*(.*)", l).groups() for l in fm.strip().split("\n"))
    body = rest.split("<!-- body -->", 1)[1] if "<!-- body -->" in rest else rest
    return meta, body

def nav(current):
    idx = [t[0] for t in WRITTEN].index(current)
    def lab(t):
        return f"{t[1]}{': ' if LANG == 'en' else '　'}{t[2]}" if t[1] != t[2] else t[2]
    prev = WRITTEN[idx - 1] if idx > 0 else (HOME[:-5], "", ui("封面"), None)
    nxt = WRITTEN[idx + 1] if idx + 1 < len(WRITTEN) else None
    p = f'<a href="{prev[0]}.html">← {lab(prev) if prev[1] else prev[2]}</a>' if prev[0] != current else "<span></span>"
    n = f'<a href="{nxt[0]}.html">{lab(nxt)} →</a>' if nxt else "<span></span>"
    return f'<footer class="nav">{p}{n}</footer>'

def langbits(f):
    """HEAD 中与语言有关的字段：html lang、目录按钮文字、切换到另一语言同名页面的链接"""
    other = f"../{f}.html" if LANG == "en" else f"en/{f}.html"
    return dict(lang="en" if LANG == "en" else "zh-CN", l_open=ui("展开目录"), l_toc=ui("目录"), l_views=ui("次阅读"), stats=STATS, other=other,
                olang="zh-CN" if LANG == "en" else "en", olabel="中文" if LANG == "en" else "English")

def build_page(path):
    global VIEW
    meta, body = parse(path)
    keep = VIEW
    if meta.get("view") == "both":
        VIEW = ""
    kind, f = meta["kind"], meta["file"]
    content, heads = md(body)
    out = [HEAD.format(css=CSS, page=f, pre="", side=sidebar(f, heads), title=meta["title"], desc=html.escape(meta.get("desc", "")), book=BOOK, home=HOME, part=meta.get("part", ""), **langbits(f))]
    if kind == "part":
        sub = f'<small>{meta["subtitle"]}</small>' if meta.get("subtitle") else ""
        out.append(f'<div class="partno">{meta["no"]}</div><h1>{meta["title"]}{sub}</h1>')
    elif kind == "preface":
        out.append(f'<div class="chapno">{ui("序")}</div><h1>{meta["title"]}</h1>')
    else:
        sub = f'<small>{meta["subtitle"]}</small>' if meta.get("subtitle") else ""
        out.append(f'<div class="chapno">{meta["no"]}</div><h1>{meta["title"]}{sub}</h1>')
        if meta.get("term"):
            out.append(term_strip(meta["term"]))
    if meta.get("asof"):
        out.append(f'<div class="stamp">{ui("资料截至")} {meta["asof"]}</div>')
    out += [content, nav(f), TAIL]
    (OUT / f"{f}.html").write_text("\n".join(out))
    VIEW = keep
    return f

def build_cover():
    meta, body = parse(SRC / "cover.md")
    content, _ = md(body)
    hero = (SRC / "figs" / "cover-hero.html").read_text().replace("{credits}", "".join(f'<p><span>{html.escape(r)}</span>{html.escape(n)}</p>' for r, n in (c.split("|", 1) for c in meta.get("credits", "").split(";") if "|" in c))).replace("{start}", WRITTEN[0][0] + ".html").replace("{edition}", html.escape(meta.get("edition", "")))
    lb = langbits("index")
    hero = re.sub(r'(<div class="hero-top">.*?)</div>', lambda m: m[1] + f'<a class="hero-lang" href="{lb["other"]}" hreflang="{lb["olang"]}">{lb["olabel"]}</a></div>', hero, count=1, flags=re.S)
    out = [HEAD.format(css=CSS, page="index", pre=hero, side=sidebar("index"), title=HOME_TITLE, desc=html.escape(meta["desc"]), book=BOOK, home=HOME, part=ui("关于本书"), **lb)]
    out.append('<div class="about" id="about">')
    out.append(content)
    out.append(f'<p><a class="startbtn" href="{WRITTEN[0][0]}.html">{ui("从序开始阅读 →")}</a></p></div>')
    out.append(TAIL)
    (OUT / "index.html").write_text("\n".join(out))

def retitle(toc, pages):
    """英文目录的篇目标题取自英文稿的 title，使目录与页面标题一致；部分（part）与篇（sec）保留目录里的写法"""
    t = {m["file"]: m["title"] for m in (parse(p)[0] for p in pages)}
    return [(f, no, t.get(f, title) if part not in ("part", "sec") else title, part) for f, no, title, part in toc]

def set_lang(lang):
    """切换语言：设置源目录、输出目录、目录与书名；生成式（build_gen.py）随后覆盖 TOC 与 VIEW"""
    global LANG, SRC, OUT, TOC, DONE, WRITTEN, BOOK, HOME_TITLE, HOME_SUB, VIEW
    LANG = lang
    SRC = ROOT / "en" if lang == "en" else ROOT
    OUT = ROOT / "site" / "en" if lang == "en" else ROOT / "site"
    OUT.mkdir(exist_ok=True)
    TOC = TOC_EN if lang == "en" else TOC_ZH
    BOOK = "Product × Finance × AI: Financial Products in the Age of AI" if lang == "en" else "产品×金融×AI：AI 时代的金融产品"
    HOME_TITLE, HOME_SUB = ("Product × Finance × AI", "Financial Products in the Age of AI") if lang == "en" else ("产品×金融×AI", "AI 时代的金融产品")
    VIEW = "d"
    pages = sorted((SRC / "chapters").glob("*.md"))
    DONE = {parse(p)[0]["file"] for p in pages}
    if lang == "en":
        TOC = retitle(TOC, pages)
    WRITTEN = [t for t in TOC if t[0] in DONE]
    return pages

def build_all(lang):
    pages = set_lang(lang)
    for old in OUT.glob("*.html"):
        if not old.name.startswith("g-"):
            old.unlink()
    built = [build_page(p) for p in pages]
    if (SRC / "cover.md").exists():
        build_cover()
    print(f"[{lang}] 已生成：", ", ".join(built + ["index"]))
    import build_gen, sys
    build_gen.build = sys.modules[__name__]  # 以脚本运行时本模块名为 __main__，让生成式沿用当前语言设置
    build_gen.main()

if __name__ == "__main__":
    build_all("zh")
    if (ROOT / "en" / "chapters").exists():
        build_all("en")
