+++
date = '2026-10-22T22:09:54+08:00'
draft = false
title = 'blog.earlzhang.net解封记'
description = "刚复活的博客在 Chrome 里满屏红字，域名被 Google 安全浏览拉黑。查存档才知它曾被抢注做足球转播站，在 Search Console 申诉约 12 小时后警告消失、站点恢复正常。"
tags = ["域名", "创作者生态", "网站安全"]
+++

之前说到[“捡”](2026-10-21-reclaim-earlzhang-net.md)回了`earlzhang.net`这个域名，并将古老的“理性谈风月”，以https://blog.earlzhang.net/ 复活。

一切操作都是在Edge上，一切太平。

但偶然在Chrome上打开，满眼红字警告。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261022_220954_968_5bfc4a9e_longshot20261022073545.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="longshot20261022073545" style="width:50%" />

即使强行进入，地址栏依然有红色的警告，很是刺眼。

![longshot20261022073534](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261022_220954_969_e1d528b1_longshot20261022073534.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

循惯例，问Gemini怎么回事——毕竟Chrome也是同门。

Gemini说：

> **Google 安全浏览 (Google Safe Browsing)** 机制将域名列入了黑名单（可能标记为仿冒网站、恶意软件或含有欺骗性内容）。Edge 使用的是微软的 SmartScreen，因此两者的黑名单库存在差异。

怎么办？

去 [Google Search Console](https://search.google.com/search-console) 申请解封。

跳转过去，在**安全问题与人工处置措施 (Security & Manual Actions)** -> **安全问题 (Security Issues)**中看到了警告：

![longshot20261022073413](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261022_220955_192_612b0272_tmpjtuw2gl0.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

因为我当年的blog下线许久，域名都丢了许久，也不知道什么原因。反正先申请申诉，说这是我新买的域名。

在等申诉结果的过程中，去https://web.archive.org/ 查了一下这个域名过去几年到底发生了什么。

才发现，竟然被人抢注变成了足球转播，虽然看不出特别离谱的，但想想估计也有问题。

真是庆幸，幸好这次把域名买回来了。

等了差不多12小时，再登录谷歌后台，发现上面的警告已经没有了，网站在Chrome中也能正常访问了，总算是解封了。




