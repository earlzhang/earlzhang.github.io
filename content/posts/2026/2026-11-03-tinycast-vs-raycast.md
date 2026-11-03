+++
date = '2026-11-03T08:40:46+08:00'
draft = false
title = 'Tinycast取代Raycast，可用但升级代价不小'
description = "装上 Tinycast 实测，内存只降到 130MB 左右，导入配置时 quicklink 和 script 的快捷键还全丢了。收益太小、折腾太多，我决定继续用 Raycast，非深度用户倒是可以试试。"
tags = ["效率工具", "操作系统", "AI工具"]
+++

macOS用户，相信不少是[Raycast](https://www.raycast.com/)的拥趸，我自然也是。

从快速启动、剪贴板管理到窗口布局乃至script，这些功能一应俱全，而且全部免费，只是像AI这样的功能才收费，绝对算是良心软件。

不过最近一个叫[Tinycast](https://tinycast.dev/)的软件，一下子热起来了。

看了一些介绍，算是Raycast的简约瘦身版，只保留了上面提到的那些最朴素的功能，所以可以大大降低内存占用，甚至有的评论说可以控制在100M以内，对我这样16G内存的玩家，的确有吸引力。

下载安装测试了下，最终还是**放弃**了。

原因是两点。

### 内存占用优势有限

我在安装Tinycast前，让大模型测了下Raycast的内存占用，包含相关的**WebContent 进程**，大体在300-400MB之间。

安装Tinycast后，也测了一下它的内存占用，似乎没网上说的那么小，大概在130MB左右。

有节省吗？的确有，但差距没那么离谱。

### 导入功能有缺陷

之前之所以勇于尝试Tinycast，主要在于网上说它可以将Raycast导出的配置文件完整地导入。

很可惜，试下来并非如此，有严重的“缺陷”。

我是Raycast的重度玩家，所以大量的quicklink、script等都设置了缩写和快捷键，但导入后，**这些全部丢失**，只有App的缩写和快捷键可以导入。

查了下[官方文档](https://tinycast.dev/docs/reference/import-from-raycast/)，的确，只支持导入App aliases。

让大模型分析了下原因，应该是quicklink等相关的缩写和快捷键内容在Raycast中使用的是**内部命令ID**，Tinycast无法识别，就无法导入。

对我来说这是最要命的，这意味着如果我迁移，就必须重新设置大量的快捷键和缩写，劳师动众了。

### 继续用Raycast

本着奥卡姆剃刀原则（Occam's Razor），在收益微乎其微，折腾却要多许多的前提下，还是不换，继续老老实实用Raycast，直到哪天Raycast臃肿到我真受不了吧。

不过如果你还不算Raycast的深度用户，或者还没接触过这种macOS工具，倒是建议从Tinycast开始尝试。
