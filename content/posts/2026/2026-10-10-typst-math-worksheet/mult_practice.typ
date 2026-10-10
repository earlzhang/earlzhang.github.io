// 三位数 × 一位数 竖式计算练习
// A4 · 每页 4 列 × 5 行 = 20 题 · 每题保证竖式计算中至少出现一次进位
// 默认一次生成 10 页（200 题互不相同），页脚自动编页码。
//
// 生成新题（换一个数字就是一份新卷子）：
//   typst compile mult_practice.typ out.pdf --input seed=12345
// 指定页数：
//   typst compile mult_practice.typ out.pdf --input seed=12345 --input pages=5
// 每次编译都出新题：用当前秒级时间戳做种子
//   typst compile mult_practice.typ out.pdf --input seed=$(date +%s)
// 不带 --input 时以当天日期为种子（同一天编译结果固定）。

// ---------- 排版组件（内联自 shuxue.typ，无外部依赖） ----------
/// 横线填空
#let fill-blank(len) = box(
  width: len,
  baseline: 0.1em,
  stroke: (bottom: 0.7pt + black),
)

/// 卷头信息栏：左侧若干「标签+横线」，可选右侧编号与角标，下方点线分隔
/// fields: ((标签, 横线长度), ...)
#let paper-header(
  fields: (("班级", 1.7cm), ("姓名", 1.7cm), ("学号", 1.7cm)),
  note: none,
  badge: none,
  separator: true,
  gutter: 0.45cm,
  rule-stroke: (thickness: 0.9pt, dash: "dotted"),
) = {
  let has-note = note != none
  let has-badge = badge != none
  let n = fields.len()
  let note-cells = if has-note { (note,) } else { () }
  let badge-cells = if has-badge { (badge,) } else { () }
  let cols = (auto,) * n + (if has-note { (1fr,) } else { () }) + (if has-badge { (auto,) } else { () })
  let aligns = (left,) * n + (if has-note { (left,) } else { () }) + (if has-badge { (right,) } else { () })
  let cells = fields.map(((label, w)) => [#label#h(0.3em)#fill-blank(w)]) + note-cells + badge-cells
  let bar = grid(columns: cols, column-gutter: gutter, align: aligns, ..cells)
  if separator {
    block(bar, width: 100%, stroke: (bottom: rule-stroke), inset: (bottom: 0.25em))
  } else {
    bar
  }
}

/// 大题标题（数学卷用常规字重）
#let section-title(t) = block(above: 1.02em, below: 0.45em, text(t, weight: "regular"))

/// 算式网格：items 为算式内容数组，逐行排布，整块左缩进
#let calc-grid(items, cols: 4) = pad(
  left: 1.75em,
  grid(
    columns: (1fr,) * cols,
    column-gutter: 1.2em,
    align: left,
    ..items,
  ),
)

#set page(
  paper: "a4",
  margin: (x: 1.5cm, top: 1.4cm, bottom: 1.3cm),
  footer: context align(center)[
    #text(size: 10pt)[第 #counter(page).display() 页 / 共 #counter(page).final().first() 页]
  ],
)
#set text(font: ("Times New Roman", "Songti SC"), size: 14pt)

// ---------- 伪随机数（线性同余发生器） ----------
#let M = 2147483648
#let lcg(s) = calc.rem-euclid(1103515245 * s + 12345, M)

// 返回 (新状态, [lo, hi] 之间的整数)
#let rand-int(s, lo, hi) = {
  let s2 = lcg(s)
  (s2, lo + calc.rem-euclid(calc.div-euclid(s2, 65536), hi - lo + 1))
}

// 判断 n × k 逐位竖式计算是否至少产生一次进位
#let has-carry(n, k) = {
  let carry = 0
  let found = false
  let x = n
  while x > 0 {
    let t = calc.rem-euclid(x, 10) * k + carry
    if t >= 10 { found = true }
    carry = calc.div-euclid(t, 10)
    x = calc.div-euclid(x, 10)
  }
  found
}

// ---------- 出题 ----------
#let today = datetime.today()
#let seed-str = sys.inputs.at(
  "seed",
  default: str(today.year() * 10000 + today.month() * 100 + today.day()),
)
#let page-count = int(sys.inputs.at("pages", default: "10"))
#let state = lcg(calc.rem-euclid(int(seed-str), M))
#let problems = ()
#while problems.len() < 20 * page-count {
  let (s1, k) = rand-int(state, 2, 9)
  let (s2, n) = rand-int(s1, 100, 999)
  state = s2
  if has-carry(n, k) { problems.push((n, k)) }
}

// ---------- 单题排版：竖式 ----------
#let prob(n, k) = {
  let h = calc.div-euclid(n, 100)
  let t = calc.div-euclid(calc.rem-euclid(n, 100), 10)
  let o = calc.rem-euclid(n, 10)
  align(center)[
    #text(size: 17pt)[
      #grid(
        columns: (1em, 1.1em, 1.1em, 1.1em),
        row-gutter: 7pt,
        align: center,
        [], [#h], [#t], [#o],
        [×], [], [], [#k],
      )
    ]
    #v(3pt)
    #line(length: 4.4em, stroke: 0.8pt)
  ]
}

// ---------- 页面 ----------
#for i in range(page-count) {
  paper-header(fields: (("班级", 1.7cm), ("姓名", 1.7cm), ("日期", 1.7cm)))
  section-title([一、用竖式计算。])
  calc-grid(
    problems
      .slice(i * 20, i * 20 + 20)
      .map(p => box(width: 100%, height: 4.8cm, inset: (top: 5mm), prob(p.at(0), p.at(1)))),
    cols: 4,
  )
  if i < page-count - 1 { pagebreak() }
}
