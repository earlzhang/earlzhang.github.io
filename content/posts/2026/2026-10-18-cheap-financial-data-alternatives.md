+++
date = '2026-10-18T21:52:49+08:00'
draft = false
title = 'AI时代，指数投资量化数据的穷鬼平替'
description = "用不起Wind和Choice，我把指数量价、估值、美股、黄金、宏观数据的下载换成了万得艾思、红色火箭、Tiingo和FRED，让大模型直接拉。平替能跑通，只是EDB一次就烧掉三百多积分。"
tags = ["金融数据", "AI×投资", "AI工具", "金融终端"]
+++

作为一向以量化思维驱动指数投资的散户，我对金融数据是有强依赖的。

当然，今年的主要工作，是寻找穷鬼平替，摆脱对Wind金融终端(主要是太贵用不起了)和Choice API(同样因为太贵了)的依赖。

这里，与诸位分享一些平替数据源。

## A股：万得艾思

虽然不用Wind终端了，但是系出同门的万得艾思 · Alice Market(https://market.windalice.com/)却是极好的平替，只需要安装一个Skill或者MCP，就能使用。如果你用的是Workbuddy之类的软件，有现成的连接器，配置就更方便了。

![image-20261018211439691](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_399_db582bbb_tmpx7_1b807.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

万得艾思能提取的数据很多，我主要是下载指数的量价数据和估值数据。

目前它家每天送300积分，精打细算，四舍五入相当于免费——当然我已经充值过100元了，这里就要和诸位分享省积分攻略。

![image-20261018211629868](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215249_729_6db58d75_image-20261018211629868.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

在万得艾思体系下，不同数据消耗的积分是有巨大差异的。

我下载最多的是指数的收盘价数据，这个非常便宜，走get_index_kline功能，一个指数正常是1积分，目前打折只要0.6积分。

但是如果你要的是类似指数估值(比如市盈率)的数据，走get_index_fundamentals，动不动就好几个积分，而且数据下载还有诸多bug。我刚刚就遇到过，下载万得全A指数2016年迄今的周收盘价和市盈率，通过这个接口拿到的数据大模型认为有问题，最终走了EDB——数据是拿到了，积分也悲剧了，一下子300多积分没了。

![image-20261018211924517](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215249_880_d0061a55_tmpszi8r_0q.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

是的，万得艾思体系下，EDB非常贵，消耗积分非常厉害，我上一次充值，也是因为使用EDB把送的积分用完，必须充值。

这里有两个技巧分享：

1. 针对EDB，必须有本地缓存。这个你和大模型直说就行，就说EDB消耗很贵，必须有本地缓存，每次只下载本地没有的数据，这样拉取的时间段短，做增量提取，除了第一次大消耗逃不掉，后面就省钱了。
2. 换别家Skill。哪怕是万得全A这样的Wind独家数据，也不是完全没有其他方法。我发现华宝基金的Skill(参见旧文《[易方达、华宝、南方三家ETF skill，哪家更好用](<https://mp.weixin.qq.com/s/aOa37hc7SOdjAozYFrijCg>)》)，应该也是采购了Wind的数据源，可以轻松提取数据，而且暂时没有额度限制。

所以，装了万得艾思，依然建议把上面三家基金公司的Skill也装了备用。

类似万得艾思的，还有Choice妙想、同花顺iFind，也可以考虑。

## A股ETF：红色火箭

在研究指数的时候，最常要做的事情不外乎是横向和纵向的分析：横向就是多个指数的比较；纵向则是观察一个指数的历史走势和估值。

这类分析自然是类似万得金融终端这样的收费终端最拿手的，但自打有了红色火箭小程序之后，普通基民也有了免费而强大的工具可用。

当然，这里要说的不是红色火箭小程序，而是[红色火箭网页版](https://www.hongsehuojian.com/red-rocket/)。更适合严肃和复杂的研究。

![image-20261018214526792](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_064_d44a46bf_tmp2jw6s4qx.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

比如下图就是沪深300的股息率走势图。

![image-20261018214609360](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_097_bb586d06_tmpqi2u_neg.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

比如下面就是中证红利、红利低波和红利低波100这三个红利指数的行业对比，可以精细到申万三级行业。之前也说过，哪怕是一年几万块的万得金融终端，在行业指数对比上也只能做到二级行业，红色火箭竟然可以做到三级行业，可以说是非常的牛。

![image-20261018214657527](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215249_885_7bf5e053_image-20261018214657527.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

## 美股：Tiingo

下载美股数据，Yahoo似乎是最常见的。不过这个接口是逆向出来的，时不时限流。

如果你下载的频率不高，数量不多，Tiingo是个好选择(参见旧文《[美股数据API新选择：Tiingo](<https://mp.weixin.qq.com/s/mDP7eot32aRA4OKf_nhu0g>)》)，免费用户每天有1000次调用额度，每小时50次，这些调用限定在500个品种内；如果要更多额度，升级到每月30美元的Power版即可。

![image-20261018212555853](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215249_971_3c392c66_image-20261018212555853.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

Tiingo的数据质量还是不错的，因为研究美国基金的发展，经常需要下载一些1990年代就成立的古老基金的数据，它家竟然也有齐全的数据，就更不要说ETF这种后起之秀了。

当然，如果你是要研究美股整体的长期价格、估值、同期国债利率等，那么就必须去诺奖得主罗伯特·席勒(Robert Shiller)的官网[Shiller Data](https://shillerdata.com/)，从下面的Excel表头可以看到，数据非常详实。

![image-20261018213017074](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_148_6a5f64c7_tmpz4ykvt4d.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

## 黄金

黄金数据，我聚焦现货，有两个数据源。

如果你研究的是过去百年的大变革，那么MacroTrends的[Gold Prices - 100 Year Historical Chart](https://www.macrotrends.net/1333/historical-gold-prices-100-year-chart)是一个非常好的数据源。

可以直接看图，也有数据表。

![image-20261018213113409](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_436_335d6094_tmpt8lehri3.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

既然这是前端渲染出来的走势，那就把网址扔给AI，他知道怎么提取数据。不过这个网站的黄金数据是月度的，适合研究大格局，不适合微观的。

微观数据，还是要看世界黄金协会，他有一个[Gold spot prices](https://www.gold.org/goldhub/data/gold-prices)的页面。这个页面，直接有1978年迄今的月度数据下载。这份数据是各国货币报价都有，如果要研究汇率的影响，非常有用。

![image-20261018213449225](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_427_d063ac45_tmpjlu9ovve.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

但如果你要的是逐日价格，下面有一个选择日期后查看阶段价格的功能。既然前端能查看，那么AI就能获得数据。你就把网址发给你用的大模型，告诉它希望从1978年开始下载日线数据，他会想办法的。如果你用的大模型解决不了这个问题，那就是智商堪忧，建议换一个。

![image-20261018213622806](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_442_a3597827_tmp4z80g_x0.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

## 全球宏观

宏观数据，做得比较好的是[FRED](https://fredaccount.stlouisfed.org/)，由美国**圣路易斯联邦储备银行**(Federal Reserve Bank of St. Louis)研究部门维护和运营的在线宏观经济数据库。它是全球宏观经济学、金融学研究以及量化投资领域最权威、使用最广泛的免费公共数据平台之一。

类似美国的 CPI、10 年期美债收益率之类的数据，在上面都可以查到。他家的数据可以免费查询，但是需要你在网站上注册，然后在后台申请一个 API key 就行。这个工作还是需要你自己完成，完成之后把 key 交给大模型，告诉他去 FRED 下载数据，他一般就知道该怎么下载。

![image-20261018214024235](https://earlmind.oss-cn-shanghai.aliyuncs.com/blog/20261018_215250_525_43f8165f_tmpl6qqmfr5.png?x-oss-process=image/resize,w_1200/format,webp/quality,q_80)

如果你用Python写程序，也可以进一步告诉它使用类似 fredapi 或 pandas-datareader 的包来下载。

我自己暂时常用的，就以上这些。未来如果还有扩展，我再继续更新。
