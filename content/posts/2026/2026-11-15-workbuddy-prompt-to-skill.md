+++
date = '2026-11-15T11:10:19+08:00'
draft = false
title = '在 Workbuddy 上传了两个技能：一个批作文，一个仿产业观察'
description = "把三年级作文批改和上观「产业观察」两份提示词做成 Workbuddy 技能，一万多字的产业观察被缩到六千多，few-shot 案例大量丢失，只能手动下指令补回、按题材重切。提示词转技能，人工这步省不掉。"
tags = ["AI工具", "提示词", "写作"]
+++

昨天做了一个上海小学三年级语文作文批改的系统提示词，突然想到应该上传到 Workbuddy 上，独乐乐不如众乐乐。

要把技能上传到 Workbuddy 上，得用 [Workbuddy 开放平台](https://open.workbuddy.cn/)，用微信号注册并实名认证后就能上传，从 Buddy 应用、专家、技能到连接器都可以传。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261115_111019_812_7194987c_image-20261115104959777.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="image-20261115104959777" style="width:25%" />

普通的 Skill 就是技能。

从系统提示词转换成技能，让大模型直接操作就行。不过转换完后，还是建议详细看一遍，尤其是原始提示词比较庞大的时候。

我这次上传了两个技能，一个是新做的上海小学三年级作文批改技能，一个是之前抓取了[上观新闻](https://www.shobserver.com/staticsg/home)“[产业观察](https://www.shobserver.com/staticsg/res/html/web/subsection.html?id=16&v=2.5)”栏目 20 篇稿子，蒸馏出来的写作技能。

![image-20261115105137227](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261115_111019_920_e7a43618_tmpgt_199cn.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

产业观察那个系统提示词，原本有 1 万多字，但是转化成 skill 的时候被大模型缩水到 6000 多字，最重要的 few-shot 案例大量丢失。

所以还得手动下指令，让它把这些内容补回来。

此外，模型写 skill 往往还是简单粗暴，连“渐进披露”其实做得也比较粗糙，最后是我人工指定按题材切分案例来实现的。

所以系统提示词和 skill 的转化，还是需要人工花点心思。

此外，Workbuddy 的 skill 需要不少头部参数（frontmatter），下面这些字段要发给大模型补全。

```yaml
version: "1.0.0"          
display_name: 中文展示名
display_name_en: English Display Name
description_zh: 中文描述   # 可与 description 一致
description_en: English description
```

等 skill 完善后，打包成 zip 就能上传了。

而且因为 Workbuddy 是 GUI 界面，每个技能都需要一个图标：512×512px，不大于 500KB，仅支持 JPG/PNG。

这类图标，我也是让大模型用 SVG 画、再导出 PNG。反正思路告诉它，它都能搞定，就是美感差点意思。

上传后等审核通过，就能发布了。

值得注意的是，上传审核有每日和每月的额度限制，不能高频提交，所以得谨慎。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261115_111019_813_e9f66a3a_image-20261115110500403.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="image-20261115110500403" style="width:67%" />

最后，给一下相关技能的二维码，欢迎取用。

下面这个，是作文批改的。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261115_111019_813_e75daf57_image-20261115110244428.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="image-20261115110244428" style="width:50%" />

这个，是上观「产业观察」深度稿写作的。

<img src="https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261115_111019_832_9ae2fa67_-15452.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80" alt="上观「产业观察」深度稿写作助手-15452" style="width:50%" />
