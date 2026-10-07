// yuangao:0.1.0 lib.typ - Typst Chinese Manuscript Paper (文稿纸 / 原稿纸)
// Author: 张翼轸 <me@earlmind.com>
// AI Assistant: SWE-2 (Cognition Devin)
// License: MIT
// Repository: https://earlmind.com/2026/2026-10-07-yuangao-typst-manuscript-paper/

/// 递归提取 content 或 string 中的纯文本
#let extract-text(c) = {
  if type(c) == str {
    c
  } else if type(c) == content {
    if c.has("children") {
      c.children.map(extract-text).join("")
    } else if c.has("body") {
      extract-text(c.body)
    } else if c.has("text") {
      c.text
    } else if c.func() == parbreak {
      "\n\n"
    } else if c.func() == [ ].func() {
      " "
    } else {
      ""
    }
  } else if c == none {
    ""
  } else {
    str(c)
  }
}

/// 解析文本为 20x20（或自定义行列）的格子二维数组
#let parse-text-to-cells(
  body-text,
  cols: 20,
  rows: 20,
  title: none,
  date: none,
  author: none,
  title-in-grid: true,
  indent: 2,
  combine-digits: true,
) = {
  let lines = ()
  let current-line = ()

  let is-ascii(ch) = {
    if ch.len() != 1 { return false }
    let cp = ch.to-unicode()
    (cp >= 48 and cp <= 57) or (cp >= 65 and cp <= 90) or (cp >= 97 and cp <= 122)
  }

  // 1. 如果标题放在格子里 (title-in-grid)
  if title-in-grid and title != none and title != "" {
    let title-str = extract-text(title).trim()
    if title-str != "" {
      let t-chars = title-str.clusters()
      let t-len = t-chars.len()
      let left-pad = calc.max(0, calc.floor((cols - t-len) / 2))
      for _ in range(left-pad) { current-line.push("") }
      for c in t-chars {
        if current-line.len() < cols { current-line.push(c) }
      }
      while current-line.len() < cols {
        current-line.push("")
      }
      lines.push(current-line)
      current-line = ()
    }

    // 副标题 / 日期 / 作者
    let sub-parts = ()
    if date != none and extract-text(date).trim() != "" {
      sub-parts.push(extract-text(date).trim())
    }
    if author != none and extract-text(author).trim() != "" {
      sub-parts.push(extract-text(author).trim())
    }
    if sub-parts.len() > 0 {
      let sub = sub-parts.join("  ")
      let s-chars = sub.clusters()
      let s-len = s-chars.len()
      let s-left-pad = calc.max(0, calc.floor((cols - s-len) / 2))
      for _ in range(s-left-pad) { current-line.push("") }
      for c in s-chars {
        if current-line.len() < cols { current-line.push(c) }
      }
      while current-line.len() < cols {
        current-line.push("")
      }
      lines.push(current-line)
      current-line = ()
    }
  }

  // 2. 正文分段排入格子
  let raw-str = extract-text(body-text)
  let raw-paras = raw-str.split(regex("\r?\n+"))
  
  // 中文标点避头与避尾规则
  let avoid-start-punct = (
    "，", "。", "、", "！", "？", "；", "：", "”", "’", "》", "）", "】", "…", "—",
    ",", ".", "!", "?", ";", ":", ")", "]", "}", "%", "‰"
  )
  let avoid-end-punct = (
    "“", "‘", "《", "（", "【", "(", "[", "{"
  )

  for raw-p in raw-paras {
    let p = raw-p.trim()
    if p == "" { continue }

    // 每段开头缩进 2 格
    for _ in range(indent) {
      current-line.push("")
      if current-line.len() == cols {
        lines.push(current-line)
        current-line = ()
      }
    }

    let chars = p.clusters()
    let idx = 0
    while idx < chars.len() {
      let c = chars.at(idx)

      // 合并双位英数（例如 "A4"、"10"、"15"）在同一个格子中
      if combine-digits and idx + 1 < chars.len() {
        let next-c = chars.at(idx + 1)
        if is-ascii(c) and is-ascii(next-c) {
          c = c + next-c
          idx += 1
        }
      }

      // 避头禁则：如果行首（current-line为空且非首行）遇到句末标点，挂到上一行末尾格
      if current-line.len() == 0 and lines.len() > 0 and avoid-start-punct.contains(c) {
        let last-line = lines.pop()
        let last-val = last-line.at(cols - 1)
        last-line.at(cols - 1) = last-val + c
        lines.push(last-line)
      } else if current-line.len() == cols - 1 and avoid-end-punct.contains(c) {
        // 避尾禁则：如果第20格遇到前引号/前书名号，留空移到下一行
        current-line.push("")
        lines.push(current-line)
        current-line = (c,)
      } else {
        current-line.push(c)
        if current-line.len() == cols {
          lines.push(current-line)
          current-line = ()
        }
      }

      idx += 1
    }

    // 段末结束当前行
    if current-line.len() > 0 {
      while current-line.len() < cols {
        current-line.push("")
      }
      lines.push(current-line)
      current-line = ()
    }
  }

  lines
}

/// 渲染单页稿纸
#let render-yuangao-page(
  page-lines,
  page-idx: 1,
  total-pages: 1,
  cols: 20,
  rows: 20,
  cell-size: 8.5mm,
  row-gap: 3.4mm,
  grid-color: rgb("#70a174"),
  text-font: ("Kaiti SC", "STKaiti", "KaiTi", "Songti SC", "PingFang SC"),
  text-size: 15.5pt,
  text-color: rgb("#1a1a1a"),
  paper-title: "文 稿 纸",
  header-info: none,
  show-word-count: true,
  page-numbering: true,
) = {
  set text(font: text-font, fill: text-color)

  // 1. 纸头标题
  if paper-title != none and paper-title != "" {
    align(center)[
      #text(size: 15pt, weight: "bold", fill: grid-color.darken(20%), tracking: 0.6em)[#paper-title]
    ]
    v(2mm)
  }

  // 2. 纸头信息栏（若有）
  if header-info != none {
    let grid-width = cols * cell-size
    align(center)[
      #block(width: grid-width)[
        #set text(size: 9.5pt, fill: grid-color.darken(30%))
        #grid(
          columns: (1fr, auto),
          align: (left + horizon, right + horizon),
          header-info.at("left", default: []),
          header-info.at("right", default: []),
        )
      ]
    ]
    v(2mm)
  } else {
    v(2mm)
  }

  // 3. 20 行方格子
  let rows-content = ()
  for r in range(rows) {
    let line-cells = if r < page-lines.len() { page-lines.at(r) } else { () }

    let cell-boxes = ()
    for c in range(cols) {
      let char-val = if c < line-cells.len() { line-cells.at(c) } else { "" }
      
      // 单个方格
      cell-boxes.push(
        box(
          width: cell-size,
          height: cell-size,
          stroke: 0.55pt + grid-color,
          radius: 0pt,
          align(center + horizon)[
            #set text(size: text-size, fill: text-color)
            #char-val
          ]
        )
      )
    }

    // 右侧字数标记（每5行显示 100, 200, 300, 400）
    let word-count-mark = if show-word-count and calc.rem(r + 1, 5) == 0 {
      let count-num = (page-idx - 1) * (cols * rows) + (r + 1) * cols
      text(size: 7.5pt, fill: grid-color.darken(15%))[#count-num 字]
    } else {
      none
    }

    let row-block = stack(
      dir: ltr,
      spacing: 0pt,
      ..cell-boxes,
      if show-word-count {
        box(width: 14mm, height: cell-size, align(left + horizon)[
          #h(2mm)#word-count-mark
        ])
      }
    )

    rows-content.push(row-block)
  }

  // 居中渲染方格网格
  align(center)[
    #stack(
      dir: ttb,
      spacing: row-gap,
      ..rows-content
    )
  ]

  // 4. 页脚
  if page-numbering {
    v(1fr)
    align(center)[
      #set text(size: 8.5pt, fill: grid-color.darken(25%))
      #block(width: cols * cell-size)[
        #grid(
          columns: (1fr, 1fr, 1fr),
          align: (left, center, right),
          text(size: 7.5pt, fill: grid-color.darken(15%))[#cols × #rows = #(cols * rows) 格],
          [— 第 #page-idx 页 / 共 #total-pages 页 —],
          [],
        )
      ]
    ]
  }
}

/// 文稿纸主函数 / 模板入口
#let yuangao(
  cols: 20,
  rows: 20,
  grid-color: rgb("#70a174"), // 淡绿色
  cell-size: 8.4mm,
  row-gap: 3.2mm,
  title: none,
  date: none,
  author: none,
  paper-title: "文 稿 纸",
  header-info: none,
  title-in-grid: true,
  show-word-count: true,
  page-numbering: true,
  font: ("Kaiti SC", "STKaiti", "Songti SC", "PingFang SC"),
  text-size: 15.5pt,
  text-color: rgb("#1a1a1a"),
  paper: "a4",
  margin: (x: 12mm, top: 16mm, bottom: 14mm),
  combine-digits: true,
  indent: 2,
  body,
) = {
  // 设置页面全局属性
  set page(
    paper: paper,
    margin: margin,
  )

  set text(
    font: font,
    lang: "zh",
    region: "cn",
  )

  // 解析正文内容并分配到行和格子
  let all-lines = parse-text-to-cells(
    body,
    cols: cols,
    rows: rows,
    title: title,
    date: date,
    author: author,
    title-in-grid: title-in-grid,
    indent: indent,
    combine-digits: combine-digits,
  )

  // 计算总页数
  let lines-count = calc.max(all-lines.len(), 1)
  let total-pages = calc.ceil(lines-count / rows)
  if total-pages == 0 { total-pages = 1 }

  // 逐页输出
  for p in range(total-pages) {
    let start-idx = p * rows
    let end-idx = calc.min(start-idx + rows, all-lines.len())
    let page-lines = if start-idx < all-lines.len() {
      all-lines.slice(start-idx, end-idx)
    } else {
      ()
    }

    render-yuangao-page(
      page-lines,
      page-idx: p + 1,
      total-pages: total-pages,
      cols: cols,
      rows: rows,
      cell-size: cell-size,
      row-gap: row-gap,
      grid-color: grid-color,
      text-font: font,
      text-size: text-size,
      text-color: text-color,
      paper-title: paper-title,
      header-info: header-info,
      show-word-count: show-word-count,
      page-numbering: page-numbering,
    )

    if p + 1 < total-pages {
      pagebreak()
    }
  }
}

/// 空白稿纸生成函数（便于直接打印手写）
#let yuangao-sheet(
  pages: 1,
  cols: 20,
  rows: 20,
  grid-color: rgb("#70a174"),
  cell-size: 8.4mm,
  row-gap: 3.2mm,
  paper-title: "文 稿 纸",
  header-info: (
    left: [题目：#box(width: 50mm, baseline: 0.5pt, line(length: 100%, stroke: 0.5pt + rgb("#70a174")))],
    right: [班级：#box(width: 25mm, line(length: 100%, stroke: 0.5pt + rgb("#70a174"))) 姓名：#box(width: 25mm, line(length: 100%, stroke: 0.5pt + rgb("#70a174")))],
  ),
  show-word-count: true,
  page-numbering: true,
  paper: "a4",
  margin: (x: 12mm, top: 16mm, bottom: 14mm),
) = {
  for p in range(pages) {
    yuangao(
      cols: cols,
      rows: rows,
      grid-color: grid-color,
      cell-size: cell-size,
      row-gap: row-gap,
      paper-title: paper-title,
      header-info: header-info,
      title-in-grid: false,
      show-word-count: show-word-count,
      page-numbering: page-numbering,
      paper: paper,
      margin: margin,
      "",
    )
    if p + 1 < pages {
      pagebreak()
    }
  }
}
