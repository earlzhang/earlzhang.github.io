// 20×20 淡绿色文稿纸通用模板
// 编译命令：typst compile 本文件.typ
// 说明：lib.typ 已复制到本目录，可直接分享给别人使用

#import "lib.typ": *

#show: yuangao.with(
  cols: 20,                   // 每行20格
  rows: 20,                   // 每页20行（共400格）
  grid-color: rgb("#70a174"), // 淡绿色方格
  title: "标题",          // 作文标题（自动居中排在第一行方格）
  date: "日期",  // 如不需要日期，直接注释掉或设为 none 即可
  paper-title: "文 稿 纸",     // 顶部标题
  show-word-count: true,      // 右侧显示 100/200/300/400 字标记
  title-in-grid: true,        // 标题排在方格内（第一行）
)

正文