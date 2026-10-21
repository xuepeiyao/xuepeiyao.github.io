# 验证及发布状态

2026-10-21，macOS / Node.js 22.22.0。交付目录：`Documents/Codex-Workspace/Projects/agnes-rebuild`。

## 已完成

- 独立本地分支 rebuild/agnes-2026，不改动远程 master。
- 从 GitHub 读取并保留 index.html、js/data.js、js/detail.js 和完整目录树。API 确认默认分支 master、has_pages=true，旧站最新提交 5af767fb6a7a26168264efc6e8d257946e4822b1。
- 32 个旧项目和 16 组新素材，共 48 个独立作品页面；首页、列表、关于页、旧链接入口和 404，总计 53 个 HTML。
- 用户新简介、核心能力、公司、公开客户与奖项已按原文录入，没有编造工作日期和项目成果。
- 新素材 36 张已优化为多格式、多尺寸，详见 performance.md。
- `npm run build` 成功；`npm run check` 成功：773 处本地引用，48 个作品路由，32 个旧 ID 映射，元信息和 sitemap。
- DOM 模拟测试通过：URL 恢复海报筛选（9 项）、点击 UI 筛选（6 项）并更新 URL、未知分类空状态、灯箱打开/左右键切换/关闭后恢复焦点、失败图片提示、旧链接目标全部存在。
- prefers-reduced-motion、语义化标题、跳过导航、focus-visible、原生 dialog、图片 alt、无效 ID 提示、生成式 SEO 与 sitemap 已实现。
- 手动触发 GitHub Pages 工作流已准备：PREVIEW 构建产物，DEPLOY 部署；固定旧站提交复制原图，避免切换后原图丢失。没有 push 自动发布。

## 未验证 / 阻塞

- 终端 `git ls-remote` 报 Could not resolve host: github.com，无法 clone、安装远程依赖、push 或下载原图。
- GitHub 连接能读文本和目录，返回的仓库 permissions 含 push，但可用工具只有读操作；不能据此声称已上传或部署。二进制下载被工具拒绝（only accepts UTF-8 text）。
- 本地 HTTP 服务启动被环境拒绝：listen EPERM 127.0.0.1:4321；未请求绕过权限限制。
- 现有 Chrome 无头启动失败，进程 SIGABRT。DOM 测试使用 happy-dom，没有布局引擎，dialog 行为做了模拟。它不能验证真实浏览器 Escape、焦点圈定、字体、移动端溢出、图片视觉质量、横向滑动等效果。
- 真实手机/平板/桌面视觉检查、控制台和实际资源请求未完成。没有运行 Lighthouse，未提供分数。
- 旧图片没有在本地，预览使用原站图片地址。137 个图片地址仅验证仓库路径存在，未验证在线加载。正式部署必须先保留/优化旧图，工作流已实现准备步骤。
- 仓库树中没有现有 workflow 或 CNAME。现有 Pages Source、域名和平台设置无法通过可用 GitHub API 读取，必须发布前在 Settings → Pages 核实。未修改 DNS。
- 没有远程开发分支、PR、构建运行或部署链接；`https://xuepeiyao.github.io/` 是部署目标及原站地址，不是本次部署成功凭证。

## 本地预览

`review/index.html` 可直接双击；本地文件链接已改写。分类等脚本可运行，但旧链接跳转依赖 fetch，须用 HTTP 服务。旧图依赖原站网络。正式 HTTP 预览命令见 README。

## 需要补充或审核

1. 真实浏览器审核布局、海报文字清晰度、筛选与键盘操作。
2. 可公开联系方式、是否提供简历和肖像。
3. 新作品职责、年份、项目背景和成果（可不填；不填则隐藏模块）。
4. “插画近作”三图是否拆分、logo.png 的归属、“捷业独角兽”的真实说明。
5. 正式发布确认。依据桌面《Agnes网站重建与部署完整提示词.pages》第二部分“先完成可本地预览、可审核的版本，再请求我确认正式发布。未经确认，不切换线上网站。”当前交付不切换原站。

部署及回滚操作见 README。网络和 GitHub 写入通道恢复后，先上传独立开发分支并完成审核，再按文档要求确认正式发布。

## 后续阻塞诊断与修复（2026-10-21 11:06）

重新发现 GitHub 写入工具后，实际调用 create_blob，GitHub 返回 HTTP 403 `Resource not accessible by integration`。这说明工具可见不等于连接具备写入授权。没有创建文件、分支、提交或 PR，原站未改动。终端域名解析失败仍在；这两项是不同阻塞。

新增桌面“上传Agnes新版到GitHub.command”。由用户在本机终端双击后运行，避免依赖代理执行环境的网络权限。脚本使用本机 GitHub CLI；未安装时从 GitHub 官方发行下载并校验 SHA-256，必要时通过 GitHub 官方浏览器流程登录。它不读取或输出令牌，不修改全局 Git 凭据配置。

脚本先构建检查，再保留旧 Git 历史、创建带时间戳的开发分支、上传源码和优化图并打开草稿 PR。任何失败都会停止，不 merge、不 force push、不切换 Pages。实际推送需要用户运行脚本并完成官方登录，尚未执行。

PR 工作流增加 pull_request 触发，解决“默认分支还没有工作流导致无法从界面运行”的问题。GitHub 托管 Runner 会保留并优化旧图，使用 Chromium 检查 390/768/1440px 布局、所有项目 HTTP 路由、32 个旧链接、分类和原生图片预览，并上传截图与预览产物。浏览器脚本目前仅通过语法检查，远程运行结果待真实上传后验证。

上传脚本通过 Python 语法检查及 mock 演练，确认只推开发分支并创建草稿 PR；mock 不包含真实网络、GitHub 登录或实际远程写入，不能视为上传成功。

## GitHub 登录 EOF 修复（2026-10-21）

用户运行本机脚本后，GitHub CLI 在 POST /login/device/code 阶段返回 unexpected EOF，尚未登录或上传。“进程已完成”仅表示脚本退出。

检测到本机 Clash Verge 的 mixed-port 配置为 7897。同步脚本增加进程级代理支持：优先使用 AGNES_PROXY 或现有 HTTPS_PROXY，否则读取本机 Clash mixed-port。仅影响脚本及其子进程，不改动系统代理、不关闭 TLS 校验。新增 GitHub 登录页面连通检查与最多三次重试；检查失败时先停止并提示打开 Clash/检查节点。Git 使用进程级 HTTP/1.1，避免部分代理的 HTTP/2 兼容问题。

已通过 Python 语法检查及模拟测试：代理端口检测、尊重已有代理、连通成功路径、三次失败后停止。未在代理执行环境中发起通过本机代理的真实网络请求；需用户在自己的终端重新运行同一桌面脚本验证实际连接。代理缺失是可能原因，不能仅凭 EOF 认定根因已确认。

## 持续设备登录 EOF 的替代方式（2026-10-21）

用户再次报告 /login/device/code POST unexpected EOF。没有证据证明单纯设置代理已解决。桌面上传入口现传入 --token，认证缺失时直接使用 GitHub 官方细粒度令牌，不再调用设备验证码接口。令牌表单预填目标 owner xuepeiyao、7天有效期，以及 Contents / Workflows / Pull requests 写入权限；用户须选择 Only select repositories 中的 xuepeiyao.github.io。

终端通过 getpass 隐藏输入，令牌仅放入当前脚本的子进程环境，未写入源码、文件或命令行参数，也不发送到聊天。认证测试在仓库 API 完成。原有 GitHub CLI 默认入口保留设备登录失败后的令牌回退。GitHub 连通检查改为仓库 API，避免令牌模式继续依赖设备登录页面。

已通过语法检查与全部 mock 测试：隐藏输入、参数不含凭据、验证失败清理令牌、拒绝非交互输入。真实令牌验证、推送和 PR 创建尚待用户本机运行，不宣称已上传。

官方依据：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens （表单预填参数与细粒度权限）；https://cli.github.com/manual/gh_help_environment （GH_TOKEN）。

## Git clone LibreSSL 失败的修复（2026-10-21）

用户已完成令牌验证，但 git clone 返回 LibreSSL SSL_connect SSL_ERROR_SYSCALL。这不能视为令牌失败，也不再要求用户重新创建令牌。

同步入口已改为 Python 标准库调用 GitHub Git Data / Pull Requests API，不再调用 Git clone/push、GitHub CLI 或设备登录接口。通过原默认分支的 Git tree 和 commit 作为基准创建新树和子提交，保留原文件与完整父提交关系；仅创建唯一的 rebuild/agnes-* 分支和草稿 PR，不修改默认分支或 Pages。

二进制图片以 base64 blob 上传并核对 Git blob SHA；本机缓存只保存已上传对象的哈希，不含凭据。写入请求间隔至少 1.15 秒，遇到限流暂停并重试。中断后重用已上传 blob；分支已建立但 PR 失败时可续建 PR。报告中的每次检查时间戳不影响续传源指纹。令牌只在本机终端隐藏输入并保存在当前进程内存。

语法和模拟测试通过：二进制哈希、上传中断后复用已成功文件、原树/父提交保留、开发分支及草稿 PR、重复运行不重复创建 PR、没有修改线上分支的 PATCH 请求。尚未实际执行 API 文件上传；需用户在本机重新运行现有桌面脚本。

## API HTTP 400 诊断（2026-10-21）

用户报告 API 返回 HTTP 400 malformed request。本机上传缓存显示 281 个已知 Git 对象，约 100 个当前源码文件可复用；没有 remote-sync.json，尚未确认开发分支已创建。不能据此认定令牌有误或所有请求格式都错误。

请求仍使用 GitHub 官方 blobs API 的 base64 JSON 字段。增加紧凑 JSON 序列化、显式字节 Content-Length、Connection: close 和固定支持的 API 版本。仅对带 malformed request 的 400 响应最多尝试四次；持续失败时显示 HTTP 方法、端点、具体文件与字节数、GitHub 请求编号，不输出令牌或完整请求体。

语法和模拟测试通过：400 后成功、持续400有限停止、请求长度正确、请求编号和文件上下文、原有断点续传行为。真实故障根因仍未确定，未宣称已经成功上传。

## 上传途中 401 Bad credentials（2026-10-21）

用户报告 e0088cdd56b5-1200.webp（234078字节）上传时 GitHub 返回 401 Bad credentials，请求编号 AEBD:13162D:15BBE21:1FAF4CD:6AD877E5。此前已有上传成功，不能推定用户最初粘贴错误；可能为失效或撤销，实际原因未确认。本机缓存检查时有383个当前文件可复用，尚未生成远程成功报告。

新增一次受限的本机交互令牌更换：上传收到401时暂停，打开官方7天细粒度令牌表单，用户在终端隐藏输入并验证新令牌，再用原请求继续当前文件。每次运行最多进行一次途中换令牌，避免无限重复。启动时旧令牌验证401也允许一次替换；不把401当成普通网络错误反复重试。

语法、401后换令牌继续同一请求、换后仍401立即停止、原断点续传模拟测试通过。没有获取用户真实新令牌，也未执行实际远程续传；需要用户本机输入有效令牌。
