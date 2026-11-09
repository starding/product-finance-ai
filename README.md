# Product × Finance × AI　产品×金融×AI

An interactive web book on financial products in the age of AI, in Chinese and English.
一本关于 AI 时代金融产品的交互式网页书，中英双语。

**Read online 在线阅读:** see the GitHub Pages link in the repository's About panel. 见仓库 About 栏中的 GitHub Pages 链接。

## Two ways of reading　两种读法

- **Decomposition 分解式** — starts from four equations and takes each term apart: markets, users, AI, and the design of financial products under those three sets of constraints.
  从四个等式出发逐项拆开：市场、用户、AI，以及在三组约束下如何设计金融产品。
- **Derivation 生成式** — starts from a world without finance and derives, one constraint at a time, how financial institutions and products arise; then changes one parameter, the price of cognitive labour, and runs the derivation again.
  从一个没有金融的世界出发，每次引入一个约束，推演金融制度与产品如何出现；再改变一个参数（认知劳动的价格）重新推演。

Every page has a switch between Chinese and English. 每页右上角可切换中文与英文。

## Credits　署名

- Concept and structure 立意与结构: 兴华 XingHua
- Text and interactive figures 正文与交互图: written by Claude, directed and revised by 兴华 XingHua　Claude 撰写，兴华 XingHua 指导与修订
- Fact-checking 事实核实: Claude
- Copy review 审校: 兴华 XingHua

The Chinese text is the canonical edition; the English edition is a translation. 中文为正本，英文为译本。

## Build　构建

```bash
python3 build.py
```

Sources 源文件: `chapters/`, `gen/`, `figs/`, `cover.md` (Chinese 中文) and the same paths under `en/` (English 英文). Output 输出: `site/` (Chinese) and `site/en/` (English). No dependencies beyond Python 3. 除 Python 3 外无其他依赖。

This book is for education only and is not investment advice. 本书仅供学习，不构成投资建议。
