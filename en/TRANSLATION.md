# English edition: translation guide

The Chinese source is canonical. The English edition mirrors it file by file:

| Chinese source | English file |
|---|---|
| `chapters/<name>.md` | `en/chapters/<same name>.md` |
| `gen/<name>.md` | `en/gen/<same name>.md` |
| `figs/<name>.html` | `en/figs/<same name>.html` |
| `cover.md` | `en/cover.md` |

Keep file names (including the Chinese part of the name) unchanged so the two editions stay paired.

## Voice

- Mature, plain written English for an educated non-specialist: clear sentences, precise terms, no slang, no hype, no rhetorical questions added for effect.
- Translate meaning, not word order. Chinese often strings clauses with commas and semicolons; split into clean English sentences.
- No meta-narration ("In this chapter we will…", "As mentioned above"). The Chinese avoids it; so must the English.
- Do not add or drop facts, numbers, hedges, sources or examples. If the Chinese says 示意, the English says "Illustrative"; if it says 作者估算, the English says "author's estimate".
- Keep every number exactly. Convert Chinese units: 6.6 万 → 66,000; 1.2 亿 → 120 million. Use % and thousands separators as in English.
- Chinese section numbering 一、二、三 → 1. 2. 3.; （一）→ (1).

## Markdown files

- Front matter: keep every key; translate the values of `no`, `title`, `subtitle`, `part`, `desc`, `asof` text. Keep `file`, `kind`, `view`, `term` values unchanged.
  - `no`: 第 7 章 → `Chapter 7`; 第一部分 → `Part One` (Two, Three, Four); 序 → `Preface`; 结语 → `Epilogue`; 附录 → `Appendix`.
  - `part` strings, e.g. `第一部分 · 第二篇　风险补偿：承担风险的价格` → `Part One · Section Two  Risk compensation: the price of bearing risk`.
- Replace the whole version history (everything between the front matter and `<!-- body -->`) with exactly one line: `Translated from the Chinese edition on 2026-11-09.` Keep the `<!-- body -->` marker.
- Keep `{{fig:…}}`, `{{formula:…|…}}`, `{{principles:N}}` lines exactly, translating only the text inside `{{formula:…}}`.
- Headings: `## 参考文献` → `## References`; `## 口径与局限` → `## Scope and limitations`; `## 几点约定` → `## Conventions`. These three exact English headings are recognised by the build.
- References: keep entries that are already in English unchanged. Translate Chinese entries into English (official English names of laws and bodies where they exist, e.g. 《中华人民共和国道路交通安全法》第九十一条 → Road Traffic Safety Law of the People's Republic of China, Article 91). Keep alphabetical order where the Chinese list was alphabetical.
- In-text citations: Chinese transliterations go back to the original Latin names: 巴伯与奥迪恩（2000） → Barber and Odean (2000); 克雷普斯、米尔格罗姆、罗伯茨与威尔逊 → Kreps, Milgrom, Roberts and Wilson. Use the names as spelled in the reference list.
- `**今天的对应。**` → `**Today's counterpart.**`
- Do not mention China-specific readers or Chinese-language sources unless the original does.

### Principle cards (generative view)

Chinese:

```
:::原理 名称
一句话表述
学科：…
类型：…
地位：…
约束：…
前提：…
提出：…
问题：…
重跑：…
:::
```

English (use exactly these markers and field keys, with an ASCII colon and a space):

```
:::principle Name
One-sentence statement.
Discipline: …
Type: …
Standing: …
Constraint: …
Premises: …
Proposed: …
Question: …
Rerun: …
:::
```

`:::重跑 名称` → `:::rerun Name`. Field order stays as in the source; omit fields the source omits. `Proposed` must keep the year(s) as four-digit numbers (the overview chart reads them), e.g. `Proposed: Kreps, Milgrom, Roberts and Wilson, 1982`.
Discipline uses ` › ` between levels, e.g. `经济学 › 信息经济学（信贷市场）` → `Economics › Information economics (credit markets)`.
Type: 理论 → Theory; 理论模型 → Theoretical model; 定理 → Theorem; 定律 → Law; 假说 → Hypothesis; 设计原则 → Design principle.

## Figure files

- Translate only text a reader sees: visible HTML text, `aria-label`, `title`, `alt`, captions, and string literals in scripts that end up on screen (labels, messages, tooltips, data names).
- Never change element ids, class names, `data-*` attribute names and values used by code, CSS, function names, variable names, numbers in the logic, or the structure of template literals. The figure must behave exactly as before.
- English is longer than Chinese. Inside SVG, keep labels short (abbreviate sensibly, or break a long label into two `<text>` lines only if the code already supports it). Do not let text overflow the viewBox. Prefer moving explanation into HTML text below the SVG over shrinking fonts below 10px.
- Grids and buttons in HTML usually reflow; still prefer concise labels.
- Number formatting in JS: if code builds Chinese strings such as `第 ${n} 年`, rewrite to `Year ${n}`; `${x} 万` style must be converted consistently with the numbers shown.
- After editing, extract the `<script>` contents and run `node --check` on them; every figure must pass.
- Links inside figures (e.g. `href="estimates.html"`, `href="g-12.html"`) stay unchanged; the English site has the same file names.
- Simulator rule tags (`cs-rules`): 储蓄 Saving; 留种 Seed; 借贷 Lending; 承诺 Commitment; 货币 Money; 保险 Insurance; 银行 Bank; 股份 Shares; 市场 Market; 价格中的信息 Information in prices; 委托 Delegation; 监管与托管 Regulation & custody; 默认选项 Defaults; 参数：认知劳动的价格 Parameter: price of cognitive labour; 专属代理 Personal agent; 代理的担保 Guaranteeing agents; 人人都有分析师 Analysts for all; 代理成为市场参与者 Agents as market participants; 代理与人的偏差 Agents and human bias; 没有改变的东西 What did not change; 产品：承诺什么 Product: what to promise; 产品：委托参数与授权 Product: mandate and authority; 产品：过程记录与可核对的证据 Product: process records and verifiable evidence; 产品：上限、确认与赔付 Product: limits, confirmation and compensation; 产品：信任的建立路径 Product: the path to trust. `· 第 N 章` lock suffix → `· Ch. N`.

## Glossary

Book and views
- 产品×金融×AI → Product × Finance × AI
- AI 时代的金融产品 → Financial Products in the Age of AI
- 从零推演 → Derived from Zero
- 分解式 → Decomposition; 生成式 → Derivation (the two ways of reading)
- 推演 → derivation / to derive (verb: "work out", "derive"); 推演一下 → "Work it through:" or recast the sentence
- 推演至此，得到一条原理 → "Derived so far: a principle" (set by the build; do not write it in text)
- 原理卡 → principle card; 原理的位置 → Where the principles sit
- 文明模拟器第 N 版 → Civilization Simulator, version N
- 今天的对应 → Today's counterpart
- 示意 → Illustrative; 示意模型 → Illustrative model; 作者估算 → author's estimate
- 这一步留下的问题 → What this step leaves open; 对产品的含义 → Implications for products; 对产品设计的含义 → Implications for product design; 本章小结 → Chapter summary
- 新的约束只有一个 → There is one new constraint

Generative world
- 岛 / 村 → the island / the village; 村民 → villager; 我 (narrator) → I
- 收成 → harvest; 年景 → a run of years (one simulated history of good and bad years); 风暴 → storm
- 粮食 / 份 → grain / portion; 种子 / 留种 → seed / keeping seed
- 粮仓 → the granary; 互助公仓 → mutual granary
- 船 / 船队 → ship / fleet; 船股 → ship shares; 稳妥份额 → safe holdings
- 集市 → the market square (or the market); 账房 → counting house
- 书记员 → scribe (plural scribes); 运营者 → operator; 委托人 → principal (or "the villager" where the source says 这位村民); 受托人 → trustee / fiduciary (follow context)
- 约定 → the agreement (the written mandate between principal and scribe); 三本账 → the three accounts: 应急 emergency, 盖房 house, 养老 retirement
- 授权四级：自行处理、事后告知、事前确认、禁止 → act on its own; act, then tell; confirm first; forbidden

Finance and economics
- 时间补偿 → time compensation; 风险补偿 → risk compensation; 信息优势 → information advantage; 交易成本 → trading costs; 运气 → luck; 承诺得到兑现 → promises kept
- 实际回报 → realized return; 净价值 → net value
- 波动拖累 → volatility drag; 因子 → factors; 买卖价差 → bid-ask spread; 做市商 → market maker
- 主动管理的算术 → the arithmetic of active management
- 放大倍数 → amplification factor; 可达份额 → reachable share; 适用比例 → applicable share
- 委托参数 → mandate parameters; 委托书 → mandate; 授权 → authority / authorization; 不可逆敞口 → irreversible exposure
- 能力装配 → capability assembly; 过程可见 → process visibility; 保障强度 → assurance level
- 时点记录 / 当时知道什么 → point-in-time record / what was known at the time
- 风险承受力的三个面 → the three faces of risk tolerance: capacity (能承受), willingness (愿意承受), behaviour (实际承受)
- 画像 → profile
- 适当性 → suitability; 受托义务 → fiduciary duty; 全权委托账户 → discretionary account
- 现状的稳态 / 理想的稳态 → the steady state of current practice / the steady state of the ideal; 先尊重，再邀请 → respect first, then invite
- 自由主义的家长制 → libertarian paternalism

Principle names (use exactly)
- 现在物品与将来物品的价值差 → Present goods are worth more than future goods
- 边际效用递减 → Diminishing marginal utility
- 生命周期与持久收入假说 → Life-cycle and permanent-income hypotheses
- 费雪的利息理论 → Fisher's theory of interest
- 交换媒介的自发产生 → Spontaneous emergence of a medium of exchange
- 货币即记忆 → Money is memory
- 世代交叠模型中的货币 → Money in the overlapping-generations model
- 银行挤兑模型 → Bank-run model
- 委托监督 → Delegated monitoring
- 价差是即时成交的价格 → The spread is the price of immediacy
- 流动性溢价 → Liquidity premium
- 风险分担的相互性 → Mutuality of risk sharing
- 按情形兑付的索取权 → State-contingent claims
- 保险市场的逆向选择 → Adverse selection in insurance markets
- 准双曲贴现 → Quasi-hyperbolic discounting
- 选择架构 → Choice architecture
- 有效市场假说 → Efficient market hypothesis
- 格罗斯曼—斯蒂格利茨悖论 → Grossman–Stiglitz paradox
- 主动管理的算术 → The arithmetic of active management
- 代理成本的三项 → The three components of agency costs
- 信息量原则 → The informativeness principle
- 资金追逐业绩、业绩不能持续 → Money chases performance; performance does not persist
- 信息的私人价值与社会价值 → Private and social value of information
- 信息丰富导致注意力贫乏 → A wealth of information creates a poverty of attention
- 阿姆达尔定律 → Amdahl's law
- 声誉机制 → Reputation mechanism
- 抵押的激励与筛选 → Collateral as incentive and screen
- 信贷配给 → Credit rationing
- 默顿的组合选择 → Merton's portfolio choice
- 人力资本与生命周期组合 → Human capital and life-cycle portfolios
- 按目标分账的组合 → Goal-based mental accounts
- 信息瀑布 → Information cascades
- 流动性螺旋 → Liquidity spirals
- 有限责任的经济理由 → The economic case for limited liability
- 莫迪利安尼—米勒定理 → Modigliani–Miller theorem
- 信任的三个来源 → Three sources of trustworthiness
- 信号传递 → Signalling
- 从小处开始 → Starting small
- 声誉的建立 → Building a reputation
- 不完全契约与剩余控制权 → Incomplete contracts and residual control rights
- 最小权限原则 → Principle of least privilege
- 正式权威与实际权威 → Formal and real authority
- 柠檬市场 → The market for lemons
- 信任品 → Credence goods
- 监管俘获 → Regulatory capture
- 资本资产定价模型 → Capital asset pricing model
- 不可逆性效应 → Irreversibility effect
- 判决无法执行问题 → The judgment-proof problem
- 替代责任的经济理由 → The economic case for vicarious liability
- 自动化的误用与弃用 → Misuse and disuse of automation
- 成本病 → Cost disease
- 交易成本与组织的边界 → Transaction costs and the boundary of the firm
- 佣金与推荐的偏向 → Commissions and biased advice
- 瑞士奶酪模型 → Swiss cheese model
- 正常事故 → Normal accidents
- 信息披露的解开效应 → Unravelling in information disclosure
- 有成本的状态核查 → Costly state verification
