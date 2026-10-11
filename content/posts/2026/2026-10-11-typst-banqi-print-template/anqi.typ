// 象棋暗棋套装（A4 竖版两页，矢量打印）
//   第 1 页：棋盘 4×8 格阵，格宽 35mm → 棋盘 140×280mm，竖版撑满
//   第 2 页：32 枚圆子（Ø32mm，与棋格格内匹配），同格阵排布，红/黑双色
//
// 子力（每方 16 枚）：帥/將×1　仕/士×2　相/象×2　俥/車×2　傌/馬×2　炮/砲×2　兵/卒×5
//
// 编译：
//   typst compile anqi.typ
// 使用建议：棋子页用厚纸打印，或打印后贴硬纸板剪裁，背面朝上即为暗子。

#let CELL = 35mm          // 棋格格宽
#let PW = 4 * CELL        // 棋盘宽 140mm
#let PH = 8 * CELL        // 棋盘高 280mm
#let PIECE-R = 16mm       // 棋子半径（Ø32）

#assert(PH <= 290mm, message: "棋盘超出 A4 纸面")

#set page(paper: "a4", margin: 0pt)
#set text(
  font: ("Times New Roman", "Liberation Serif", "Songti SC", "SimSun", "Noto Serif CJK SC"),
  size: 10pt,
)

#let red = rgb("C8102E")
#let ink = rgb("1A1A1A")

/// 在 (cx, cy) 处居中放置文字块
#let tag(body, cx, cy, w: 8mm, h: 6.4mm) = place(
  top + left,
  dx: cx - w / 2,
  dy: cy - h / 2,
  box(width: w, height: h, align(center + horizon, body)),
)

// ---------- 第 1 页：棋盘 ----------
#let board = box(width: PW + 6mm, height: PH + 6mm)[
  // 外圈装饰边（双线框，传统象棋盘样式）
  #rect(width: PW + 6mm, height: PH + 6mm, stroke: 1pt + black)
  // 主框
  #place(top + left, dx: 3mm, dy: 3mm,
    rect(width: PW, height: PH, stroke: 1.4pt + black))
  // 内部格线
  #for i in range(1, 8) {
    place(top + left, dx: 3mm, dy: 3mm + i * CELL,
      line(start: (0pt, 0pt), end: (PW, 0pt), stroke: 0.8pt + black))
  }
  #for i in range(1, 4) {
    place(top + left, dx: 3mm + i * CELL, dy: 3mm,
      line(start: (0pt, 0pt), end: (0pt, PH), stroke: 0.8pt + black))
  }
]

#place(center + horizon, board)

#pagebreak()

// ---------- 第 2 页：棋子 ----------
// 每行 4 枚，红方 4 行 + 黑方 4 行，与棋盘同格阵
#let pieces = (
  ("帥", "仕", "仕", "相"),
  ("相", "俥", "俥", "傌"),
  ("傌", "炮", "炮", "兵"),
  ("兵", "兵", "兵", "兵"),
  ("將", "士", "士", "象"),
  ("象", "車", "車", "馬"),
  ("馬", "砲", "砲", "卒"),
  ("卒", "卒", "卒", "卒"),
)

/// 在 (cx, cy) 处绘制一枚棋子：双线圆框 + 居中字
#let piece-at(ch, col, cx, cy) = {
  place(top + left, dx: cx - PIECE-R, dy: cy - PIECE-R,
    circle(radius: PIECE-R, stroke: 1.1pt + col))
  place(top + left, dx: cx - PIECE-R + 2.6mm, dy: cy - PIECE-R + 2.6mm,
    circle(radius: PIECE-R - 2.6mm, stroke: 0.5pt + col))
  tag(text(size: 46pt, fill: col)[#ch], cx, cy, w: 30mm, h: 30mm)
}

#let piece-grid = box(width: PW, height: PH)[
  #for r in range(8) {
    let col = if r < 4 { red } else { ink }
    for c in range(4) {
      piece-at(pieces.at(r).at(c), col, (c + 0.5) * CELL, (r + 0.5) * CELL)
    }
  }
]

#place(top + center, dy: 4mm,
  text(size: 8pt, fill: rgb("888888"))[象棋暗棋 · 棋子（沿外圈剪裁 · 建议厚纸或贴硬纸板）])
#place(center + horizon, piece-grid)
