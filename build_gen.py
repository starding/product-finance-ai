# 用法：python3 build_gen.py → 由 gen/*.md 生成生成式版本 site/g-*.html（图共用 figs/，样式共用 site/book.css）
# 生成式版本：从一个没有金融的世界出发，每章引入一个约束，推演金融制度与产品如何出现；第二部分改变“代理成本”这一参数重跑一遍。
import pathlib
import build

ROOT = pathlib.Path(__file__).parent

TOC = [
    ("g-preface", "序", "理解金融产品最好的方法，是从零造一个", None),
    ("g-part1", "第一部分", "从 0 到 1：一个没有金融的世界如何长出金融", "part"),
    ("g-01", "第 1 章", "一个人，一年的收成", 1),
    ("g-02", "第 2 章", "两个人，缺的时间不同", 1),
    ("g-03", "第 3 章", "借了不还怎么办", 1),
    ("g-04", "第 4 章", "很多人一起交换", 1),
    ("g-05", "第 5 章", "收成好坏不定", 1),
    ("g-06", "第 6 章", "存的人要随时取，借的人要长期用", 1),
    ("g-07", "第 7 章", "一个人出不起一艘船的钱", 1),
    ("g-08", "第 8 章", "证券要能卖出去", 1),
    ("g-09", "第 9 章", "价格里有所有人的信息", 1),
    ("g-10", "第 10 章", "普通人没有时间也没有专长", 1),
    ("g-11", "第 11 章", "受托人可能不尽责", 1),
    ("g-12", "第 12 章", "制度齐备，人仍会犯错", 1),
    ("g-part2", "第二部分", "改变一个参数：当代理变得几乎免费", "part"),
    ("g-13", "第 13 章", "新参数：认知劳动的成本骤降", 2),
    ("g-14", "第 14 章", "人人都能有专属代理人吗", 2),
    ("g-15", "第 15 章", "谁来为代理人的承诺担保", 2),
    ("g-16", "第 16 章", "如果人人都有分析师", 2),
    ("g-17", "第 17 章", "代理人成为市场的主要参与者", 2),
    ("g-18", "第 18 章", "代理人能否矫正人的偏差", 2),
    ("g-19", "第 19 章", "没有改变的东西", 2),
    ("g-part3", "第三部分", "在新的世界里推演一个产品", "part"),
    ("g-20", "第 20 章", "一个人和一笔钱", 3),
    ("g-21", "第 21 章", "用户不在场", 3),
    ("g-22", "第 22 章", "用户看不见过程", 3),
    ("g-23", "第 23 章", "代理会出错", 3),
    ("g-24", "第 24 章", "信任需要时间", 3),
    ("g-epilogue", "结语", "回到总则", None),
    ("method", "附录", "本书的写法", "app"),
]

TOC_EN = [
    ("g-preface", "Preface", "The best way to understand financial products is to build one from zero", None),
    ("g-part1", "Part One", "From 0 to 1: how a world without finance grows finance", "part"),
    ("g-01", "Chapter 1", "One person, one year's harvest", 1),
    ("g-02", "Chapter 2", "Two people, short at different times", 1),
    ("g-03", "Chapter 3", "What if a borrower does not repay", 1),
    ("g-04", "Chapter 4", "Many people trading together", 1),
    ("g-05", "Chapter 5", "Harvests are uncertain", 1),
    ("g-06", "Chapter 6", "Savers want their money any time; borrowers need it for years", 1),
    ("g-07", "Chapter 7", "No one person can pay for a ship", 1),
    ("g-08", "Chapter 8", "Securities must be sellable", 1),
    ("g-09", "Chapter 9", "Prices carry everyone's information", 1),
    ("g-10", "Chapter 10", "Ordinary people have neither the time nor the expertise", 1),
    ("g-11", "Chapter 11", "Trustees may not do their duty", 1),
    ("g-12", "Chapter 12", "Even with the institutions in place, people still err", 1),
    ("g-part2", "Part Two", "Changing one parameter: when agency becomes almost free", "part"),
    ("g-13", "Chapter 13", "The new parameter: the cost of cognitive labour collapses", 2),
    ("g-14", "Chapter 14", "Can everyone have a personal agent?", 2),
    ("g-15", "Chapter 15", "Who guarantees an agent's promises?", 2),
    ("g-16", "Chapter 16", "If everyone had an analyst", 2),
    ("g-17", "Chapter 17", "Agents become the main market participants", 2),
    ("g-18", "Chapter 18", "Can agents correct human bias?", 2),
    ("g-19", "Chapter 19", "What did not change", 2),
    ("g-part3", "Part Three", "Deriving a product in the new world", "part"),
    ("g-20", "Chapter 20", "One person and a sum of money", 3),
    ("g-21", "Chapter 21", "The user is not there", 3),
    ("g-22", "Chapter 22", "The user cannot see the process", 3),
    ("g-23", "Chapter 23", "Agents make mistakes", 3),
    ("g-24", "Chapter 24", "Trust takes time", 3),
    ("g-epilogue", "Epilogue", "Back to the general rule", None),
    ("method", "Appendix", "How this book was written", "app"),
]

def main():
    pages = sorted((build.SRC / "gen").glob("*.md"))
    done = {build.parse(p)[0]["file"] for p in pages} | ({"method"} if (build.SRC / "chapters" / "A2-本书的写法.md").exists() else set())
    build.TOC, build.DONE = (build.retitle(TOC_EN, pages + sorted((build.SRC / "chapters").glob("A2-*.md"))) if build.LANG == "en" else TOC), done
    build.WRITTEN = [t for t in build.TOC if t[0] in done]
    build.VIEW = "g"
    for old in build.OUT.glob("g-*.html"):
        old.unlink()
    built = [build.build_page(p) for p in pages]
    print(f"[{build.LANG}] 生成式已生成：", ", ".join(built))

if __name__ == "__main__":
    build.set_lang("zh"); main()
    if (ROOT / "en" / "gen").exists():
        build.set_lang("en"); main()
