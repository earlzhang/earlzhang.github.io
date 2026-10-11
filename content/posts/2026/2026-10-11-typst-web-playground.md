+++
date = '2026-10-11T10:13:38+08:00'
draft = false
title = '免安装，用网页渲染Typst模板'
description = "前两期分享了用 Typst 模板给娃出语文数学题，但命令行安装劝退了不少人。其实把模板文件里的文本粘进 Typst 官方 Playground，几秒就能预览，点下载就能拿到可打印的 PDF。"
tags = ["Typst", "排版", "效率工具"]
+++

最近分享了两期关于用Typst模板来给娃做语文和数学的案例。

随之问题就来了，Typst这套架构，需要命令行安装，对普通人不太优化。

虽然在大模型时代，其实只要把生成的typ扩展名的模板交给大模型，让他自行安装环境并渲染即可，但终究还需要额外安装类似Workbuddy或者千问办公之类的Agent环境。

有没有更简单的方法？

有的，那就是使用Typst官方的在线编辑器。

Typst在官网上，提供了一个名为 [Typst Playground(https://typst.app/play/)](https://typst.app/play/) 的在线免费编辑器，左边是代码，右边是预览，和很多编辑器非常类似。

![image-20261011101129801](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261011_101339_604_e972e207_tmpks473b0i.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

下载的typ扩展名的文件，你如果有类似VS code之类的编辑器，可以拖入直接打开，typ本质上是一个纯文本文件，只是用了自己的扩展名。所以如果你电脑上没装VS code之类编辑器，将其扩展名改成txt，用系统文本编辑器打开就行。

打开typ模板，将所有的纯文本复制到上面左侧①的区域，一般渲染个几秒钟，在右侧区域②就能看到预览了。这时候点击③的下载按钮，就能获得渲染后的PDF文件用于打印了。

如果希望更方便的流程，也可以在Typst上注册一个免费账户，然后就可以直接上传Typst模板文件，直接打开使用了。
