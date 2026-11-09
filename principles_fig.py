# 原理的位置总图：从 gen/*.md 中收集原理卡，按推演顺序与提出年份画在同一张图上。由 build.md 遇到 {{principles:部分序号}} 时调用。
import json, re, pathlib

ROOT = pathlib.Path(__file__).parent

def cards(toc, part, src=ROOT):
    files = {p: p for p in (src / "gen").glob("*.md")}
    byid = {}
    for p in files:
        s = p.read_text()
        m = re.search(r"^file:\s*(\S+)", s, re.M)
        if m: byid[m[1]] = s
    out = []
    for t in toc:
        if (part and t[3] != part) or t[0] not in byid or t[3] not in (1, 2, 3): continue
        body = byid[t[0]].split("<!-- body -->", 1)[1]
        no = int(re.search(r"\d+", t[1])[0])
        for k, name, inner in re.findall(r"^:::(原理|重跑|principle|rerun) (.+?)\n(.*?)\n:::$", body, re.M | re.S):
            ls = [x.strip() for x in inner.split("\n") if x.strip()]
            f = {}
            for x in ls[1:]:
                if "：" in x: a, b = x.split("：", 1)
                elif ": " in x: a, b = x.split(": ", 1)
                else: continue
                f[{"Discipline": "学科", "Proposed": "提出"}.get(a.strip(), a.strip())] = b.strip()
            yr = re.search(r"(1[6-9]\d\d|20\d\d)", f.get("提出", ""))
            out.append({"ch": no, "file": t[0], "title": t[2], "name": name.strip(), "rerun": k in ("重跑", "rerun"),
                        "s": ls[0], "sub": f.get("学科", ""), "who": f.get("提出", ""), "y": int(yr[1]) if yr else None})
    return out

L = {
    "zh": dict(title="原理的位置", sub="横轴是推演的先后，纵轴是原理提出的年份。点选一个圆点，查看这条原理回应的问题与提出者；逻辑上靠后、历史上却更早的原理，说明实践往往先于理论长出了制度。",
               aria="原理的推演顺序与提出年份", cap="圆点由各章的原理卡自动汇总，纵轴以 1900 年为界分段，此前的年份压缩显示；同一章的几条原理按出现的先后左右错开。空心圆表示第二部分重新检验的原理，画在它被重新检验的那一章。",
               none="本部分尚无原理卡。", replay="重播", pre1900="1900 年以前压缩显示", xaxis="推演的先后（章）→", other="其他", ch="第 ${c.ch} 章", rerun=" · 重新检验", open="打开第 ${c.ch} 章：${c.title}"),
    "en": dict(title="Where the principles sit", sub="Across: the order of the derivation. Up: the year each principle was proposed. Tap a dot to see the principle and who proposed it. A principle that comes later in the logic but earlier in history shows practice growing institutions before theory explained them.",
               aria="Principles by order of derivation and year proposed", cap="Dots are collected automatically from each chapter's principle cards. The vertical axis is split at 1900; earlier years are compressed. Several principles from one chapter are spread left to right in order of appearance. Hollow dots are principles re-examined in Part Two, drawn at the chapter where they are re-examined.",
               none="No principle cards in this part yet.", replay="Replay", pre1900="before 1900, compressed", xaxis="Order of derivation (chapter) →", other="Other", ch="Chapter ${c.ch}", rerun=" · re-examined", open="Open Chapter ${c.ch}: ${c.title}"),
}

def figure(toc, part, lang="zh", src=ROOT):
    C = cards(toc, part, src)
    T = L[lang]
    fid = f"pp{part}"
    data = json.dumps(C, ensure_ascii=False)
    return f'''<figure>
  <div class="card">
    <div class="figbar"><div><p class="figtitle">{T["title"]}</p><p class="figsub">{T["sub"]}</p></div><button class="replay" type="button" data-replay="{fid}">{T["replay"]}</button></div>
    <div class="pp" id="{fid}" data-anim>
      <svg viewBox="0 0 660 300" role="img" aria-label="{T["aria"]}"><g id="{fid}-g"></g></svg>
      <div class="legend" id="{fid}-lg"></div>
      <div class="pp-d" id="{fid}-d" aria-live="polite"></div>
    </div>
  </div>
  <figcaption>{T["cap"]}</figcaption>
</figure>
<style>
.pp svg{{width:100%;height:auto;display:block}}
.pp circle{{cursor:pointer;transition:r .2s}}
.pp circle.sel{{stroke:var(--ink);stroke-width:2.5}}
.pp-d{{margin-top:10px;background:var(--quote);border-radius:9px;padding:10px 12px;font-size:13.5px;line-height:1.65;min-height:5.5em}}
.pp-d b{{font-size:15px}} .pp-d span{{color:var(--faint);font-size:12px}}
@media (max-width:640px){{.pp svg text{{font-size:15px}}}}
</style>
<script>
(function(){{
  const C={data},$=id=>document.getElementById('{fid}'+id);if(!C.length){{$('-d').textContent='{T["none"]}';return;}}
  const top=s=>(s.split('›')[0]||'').trim(),Ds=[...new Set(C.map(c=>top(c.sub)))],COL=['var(--accent)','var(--blue)','var(--warm)','var(--gold)','var(--ink)','var(--faint)','#8b5fb0','#2f8f8f'];
  const chs=[...new Set(C.map(c=>c.ch))].sort((a,b)=>a-b),X0=56,X1=640,YT=14,YB=262;
  const ys=C.filter(c=>c.y).map(c=>c.y),y0=Math.min(1900,Math.floor((Math.min(...ys)-10)/50)*50),y1=Math.ceil((Math.max(...ys)+5)/10)*10,BR=1900,YM=YB-(y0<BR?.2:0)*(YB-YT),yy=v=>v>=BR||y0>=BR?YM-(v-Math.max(y0,BR))/(y1-Math.max(y0,BR))*(YM-YT):YB-(v-y0)/(BR-y0)*(YB-YM);
  const xs=chs.length>1?(X1-X0)/(chs.length-1):0,cx=(c,i)=>{{const same=C.filter(d=>d.ch===c.ch),k=same.indexOf(c);return X0+chs.indexOf(c.ch)*xs+(k-(same.length-1)/2)*Math.min(14,xs/3);}};
  const TK=[...(y0<BR?[y0,(y0+BR)/2]:[]),...Array.from({{length:Math.floor((y1-Math.max(y0,BR))/25)+1}},(_,k)=>Math.max(y0,BR)+k*25)];let h=(y0<BR?`<line x1="${{X0}}" x2="${{X1}}" y1="${{YM}}" y2="${{YM}}" stroke="var(--faint)" stroke-dasharray="2 4"/><text x="${{X1}}" y="${{YM+12}}" text-anchor="end" font-size="10" class="t-faint">{T["pre1900"]}</text>`:'');for(const v of TK)h+=`<line x1="${{X0}}" x2="${{X1}}" y1="${{yy(v)}}" y2="${{yy(v)}}" class="s-line"/><text x="${{X0-8}}" y="${{yy(v)+4}}" text-anchor="end" font-size="11" class="t-faint">${{v}}</text>`;
  chs.forEach((ch,i)=>{{h+=`<text x="${{X0+i*xs}}" y="${{YB+20}}" text-anchor="middle" font-size="11" class="t-faint">${{ch}}</text>`;}});
  h+=`<text x="${{X1}}" y="${{YB+34}}" text-anchor="end" font-size="11" class="t-faint">{T["xaxis"]}</text>`;
  C.forEach((c,i)=>{{if(!c.y)return;const col=COL[Ds.indexOf(top(c.sub))%COL.length];h+=`<circle data-i="${{i}}" cx="${{cx(c,i)}}" cy="${{yy(c.y)}}" r="0" fill="${{c.rerun?'var(--bg)':col}}" stroke="${{col}}" stroke-width="${{c.rerun?2.5:1}}"/>`;}});
  $('-g').innerHTML=h;$('-lg').innerHTML=Ds.map((d,i)=>`<span><i style="background:${{COL[i%COL.length]}}"></i>${{d||'{T["other"]}'}}</span>`).join('');
  const dots=[...$('-g').querySelectorAll('circle')];
  function set(i){{const c=C[i];dots.forEach(d=>d.classList.toggle('sel',+d.dataset.i===i));
    $('-d').innerHTML=`<span>{T['ch']} · ${{c.sub}}${{c.rerun?'{T['rerun']}':''}}</span><br><b>${{c.name}}</b>　<span>${{c.who}}</span><br>${{c.s}}<br><a href="${{c.file}}.html">{T['open']}</a>`;}}
  dots.forEach(d=>d.addEventListener('click',()=>set(+d.dataset.i)));
  // 找一对逻辑在后、年份更早差距最大的原理作为默认展示
  let best=0,bi=0;C.forEach((a,i)=>C.forEach(b=>{{if(a.y&&b.y&&a.ch>b.ch&&b.y-a.y>best){{best=b.y-a.y;bi=i;}}}}));
  const grow=()=>dots.forEach((d,k)=>setTimeout(()=>d.setAttribute('r',6),k*60));
  $('').addEventListener('anim-in',()=>{{dots.forEach(d=>d.setAttribute('r',0));grow();setTimeout(()=>set(bi),dots.length*60+400);}});
  dots.forEach(d=>d.setAttribute('r',6));set(bi);
}})();
</script>'''
