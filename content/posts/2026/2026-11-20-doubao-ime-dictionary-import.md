+++
date = '2026-11-20T09:22:50+08:00'
draft = false
title = '豆包输入法支持词库导入了，但导出不支持'
description = "实测把搜狗导出的词库文件导入豆包输入法，一次成功，比只认系统词库的微信输入法强，但导出同样没有。新生代输入法都是只吃不吐的貔貅，词库互通不符合抢入口的产品定位，只能盼着略微开放。"
tags = ["输入法", "效率工具", "AI工具"]
+++

豆包输入法的测试版昨天推送了一条消息，自定义词组支持导入了。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261120_092251_406_13d0725a_longshot20261120082432.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="longshot20261120082432" style="width:67%" />

目前，豆包的批量导入支持两种功能：

1. 系统词库，这个算是 MacOS 类输入法的标配，可以将 MacOS 的系统自定义词导入。
2. 自定义文件。界面上说支持导入其他输入法的常用语文件，但从哪里获得这个常用语文件，暂时还语焉不详，只是提供了一个模板文件，允许你设计导入。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261120_092251_406_bd95b820_image-20261120090110193.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="image-20261120090110193" style="width:50%" />

模板文件我下载了，大体还是挺简单，支持单行和多行，但不似搜狗输入法还支持自定义变量。

```
// 豆包输入法--常用语导入文件

// 常用语导入文件使用方式说明：
// 1、常用语支持单行、多行。
// 2、每条常用语最多支持5000个汉字，总共支持500条常用语。
// 3、每条常用语的匹配码建议使用英文、数字，最多8个字符。
// 4、导入的格式如下：

// 单行的格式：
// 匹配码,=短语（注意：格式中的“,”为英文逗号）

// 多行的格式：
// 匹配码,=
// 多行第一行（注意：格式中的“,”为英文逗号）
// 多行第二行


// 如下为参考样例，请导入前自行删除
hf,=稍等一下，我忙完就回复你。
hy,=
每周例会提醒
时间：周一上午10点
形式：线上会议
请大家准时参加。
```

我尝试导入了从搜狗输入法导出的词库文件`phrases.ini`，一次就成功了。

这点，已经比微信输入法强了。暂时后者只支持导入系统词库。

说到这，顺便要吐槽一句，新生代的输入法，都是貔貅性格，只吃不吐。

比如微信输入法，可以导入系统词库，但导出对不起是不行的。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261120_092251_406_3ea8cb60_longshot20261120082504.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="longshot20261120082504" style="width:67%" />

豆包输入法目前也是，没有导出的。

这时候，再看看从上古时代就存在的搜狗输入法，有导入有导出，简直是眉清目秀了许多。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261120_092251_406_51088bce_longshot20261120082533.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="longshot20261120082533" style="width:67%" />

我明白，无论微信还是豆包，做一个输入法，还将优秀的语音输入功能给大家免费用，希望的就是以输入法的形态抢占住大家的入口，所以只有类似语音全局唤醒这样抢入口的功能会层出不穷，类似词库导出这样的功能，是不符合产品定位的。

但作为一个输入法的用户，终究还是希望彼此能够更互通一点，至少在自有词库上略微开放一些。

PS：顺便发现豆包输入法的`rq`快捷键终于做了迭代，现在可以出来非常多的日期格式，相当给力。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261120_092251_406_33765fc9_image-20261120090904223.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="image-20261120090904223" style="width:67%" />
