+++
date = '2026-10-30T08:32:13+08:00'
draft = false
title = '当Workbuddy不支持Win7'
description = "给上海区级机构做 AI 培训，有学员问 Win7 能不能装 Workbuddy。答案是装不了：现代 Agent 多基于 Electron 架构，命令行也依赖高版本 Node.js，最后只剩网页版可用，却也动不了本机硬盘。"
tags = ["AI工具", "AI落地", "操作系统"]
+++

这两天在给上海一些区级机构的公务员做AI培训，会后有一位学员提出了一个好问题：Win7电脑能装Workbuddy之类的Agent吗？

这是一个非常有现实意义的问题。2014年的时候，就有过禁止采购安装Win8操作系统的指引。所以基层有许多早年的电脑，也并未随后升级到Win10，那么多年依然以Win7的状态在服役。

![image-20261030073534484](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261030_083214_084_c3db44bd_tmp6l1fog4j.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

很可惜，Win7的电脑，装不了Workbuddy。其实也不仅是装不了Workbuddy，包括千问办公、豆包工作这些，也是一样。

大量现代化的软件，往往都基于VS Code、Electron等现代化的架构开发，而后者大多早早地结束了对Win7的支持。

所以这些办公Agent软件，不是不想支持Win7，而是用了现代化的开发架构，就做不到了。

更何况，Win7的电脑，即使在政府办公体系中，应该也是极少数的存量遗留了。新一代则大量是统信UOS、银河麒麟这类定制Linux版本了。

这类系统，国产办公Agent反而普遍支持。比如Workbuddy可以直接去这两个系统的应用商店下载。

![1793317316850](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261030_083213_799_d8e1cc35_1793317316850.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

千问办公更全，还可以直接下载deb版本，支持Ubuntu和Debian。

![1793319516293](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261030_083213_798_f1108dc3_1793319516293.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

显然，GUI图形界面此路不通。

本想着是否可以改用命令行呢？类似Claude Code或者国产版的。

本以为命令行要求低，但查了下才发现，现在的命令行程序，往往也依赖高版本的Node.js之类，同样不支持Win7了。

兜兜转转，似乎使用**网页版**是最后的选择了。

目前Workbuddy、千问办公都有网页版（*豆包工作没找到*）。

当然，两者入口的处理略有不同。

Workbuddy的下载是大大的图标，网页版用了“在线使用”的小字补充，得留神才行。

![1793319910452](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261030_083213_797_3d2bbb36_1793319910452.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

千问办公，这两者是平级关系。都用了按钮，而且一样大小。

![1793319955937](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261030_083213_798_802df9d1_1793319955937.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

登录后可以在浏览器里做许多操作。如果是简单地上传资料做一些处理，或者需要直接对远程网页做抓取之类，都没问题。甚至像Workbuddy的连接器也一样能用——跑个长耗时的流程不用自己电脑开着，也是件好事。

不过，网页版终究是网页版，这就意味着动不了本机电脑。

类似我经常做的在本地硬盘里查垃圾文件、几百个本地文件转换格式，甚至让Agent帮我配置优化网络这些，就都做不了了，只能无奈。
