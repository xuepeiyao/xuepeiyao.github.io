# 图片与性能记录

时间：2026-10-21T02:35:38.437Z。环境：macOS、Node.js v22.22.0、sharp 0.34.5。

36 张本地原图：82.92 MB。生成 408 个 AVIF/WebP/JPEG 尺寸衍生文件，共 47.30 MB。多格式文件是部署磁盘体积，浏览器只选用其中一种格式和一个适合的宽度，不能把所有文件相加当作一次页面下载。

36 张图各取最小尺寸 WebP 合计 1.59 MB；各取最大尺寸 WebP 合计 6.73 MB。这是文件统计，不是一次实际页面请求的测量。

|原图标识|原图|480px 或更小 WebP|详情 WebP|
|---|---:|---:|---:|
|media/naruto-membership-card/01.png|1.89 MB|25.4 KB|171.9 KB|
|media/iflytek-storyboard/01.png|0.66 MB|15.4 KB|112.2 KB|
|media/kfc/01.png|0.95 MB|92.4 KB|185.3 KB|
|media/xian-community-market/01.png|1.83 MB|17.9 KB|145.9 KB|
|media/xian-community-market/02.png|1.79 MB|25.1 KB|151.0 KB|
|media/xian-community-market/03.png|1.05 MB|15.4 KB|77.9 KB|
|media/xian-community-market/04.png|1.90 MB|29.3 KB|167.7 KB|
|media/chongqing-joy-city/01.png|1.98 MB|51.0 KB|252.1 KB|

使用 picture/srcset/sizes；最大生成宽度 1600px，不放大小图。封面 object-fit:contain，详情高度自然，不强制裁切。AVIF quality 60、WebP 85、JPEG 88；尚待人工核查海报细字、细线和渐变。长图仍可点击放大。最宽网页衍生图不等于原始可印刷文件。

首页前两张卡片优先加载，其余懒加载。详情第一张 eager，其他 lazy。新图指定宽高；旧图在优化前缺少精确尺寸，详情仍可能发生布局位移，因此不宣称 CLS 达标。无远程字体、跟踪代码或运行时第三方 JS。CSS 和脚本文件名带哈希，静态图衍生路径带原文件哈希；没有配置 GitHub Pages 不支持的自定义缓存头。

旧图尚未下载或压缩。旧站目录树共有 191 个 images 条目（含目录）；137 个不同的项目图片地址被新页面引用。真实图片请求、首屏加载、LCP、CLS 和 Lighthouse 分数均未测得，不提供估计分数。
