+++
date = '2026-10-22T09:23:29+08:00'
draft = false
title = 'Quarto启用Pagefind'
description = "在 Quarto 里把全文检索从 fuse.js 换成 Pagefind：搜「DFA」能跳到 26.5 节并高亮，但搜「阿斯内斯」仍会拆字误命中。全程由大模型操刀，靠谱的库名就像咒语。"
tags = ["搜索", "效率工具", "AI编程"]
+++

最近在用Quarto慢慢的写《[给少数人的基金投资书](https://earlfund.com/)》。

Quarto部署的是一个静态的HTML网站，但是支持全文检索。于我而言，写这个系列，首先是给自己的文献索引概述，其次才是给读者看的读物。所以有全文检索，以后想起某个话题，自己“检索”自己，就太方便了。

不过Quarto默认的全文检索，用的是`fuse.js`，是将全书的文字打包成一个文件载入网页内存来实现全文检索，这不但对页面多的网站是噩梦，而且对中文分词做的也不好。

在AI建议下，换成了更友好的`Pagefind`，据说原理是将所有的内容切分成许多的切片，按需加载。

当然，顺便做了两个优化：

1. 搜索支持子标题。会告诉你某个词是在某个页面的哪一章，点击可以直接跳转过去；
2. 黄色高亮关键词。点击进入页面后，你搜索的词会被黄色高亮，方便你查看，具体效果如下。

比如我搜索“DFA”，可以直接跳转到26.5，并且所有的DFA都高亮了。

![image-20261022091841064](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261022_092330_987_591f8fe2_tmpa8_3pd_y.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

不过，Pagefind也不是完美。比如我搜索阿斯内斯，只要页面中包含了“阿”、“斯”、“内”，就会出现在搜索结果中，所以会有一些错误的搜索结果。要做二次过滤似乎非常复杂，暂时就忍了。

![longshot20261022090431](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261022_092330_854_4aeb72e1_tmp0xqtml95.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

PS：上述的切换，全部是在大模型的建议和操作下完成，我就是知道有Pagefind这个东西提出需求而已。

AI时代，靠谱的软件或者库的名字，真是如咒语一样，可以大幅提升大模型产出的质量。
