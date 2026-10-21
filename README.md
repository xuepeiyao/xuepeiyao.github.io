# Agnes · 薛佩瑶作品集

新版包含 32 个旧作品及从“文稿/作品”整理出的 16 组新作品。线上切换尚未执行，见 `reports/verification.md`。旧站基准提交：`5af767fb6a7a26168264efc6e8d257946e4822b1`。

## 先看预览

双击 `review/index.html` 查看静态预览，链接已经调整为本地文件路径。旧作品图片仍需网络，旧 ID 自动跳转必须用下方 HTTP 预览。`review` 是生成结果，不要在里面改内容。

正常网络和本机权限环境下，安装 Node.js 22 或更新版本，在这个文件夹打开终端：

```sh
npm run build
npm run preview
```

浏览器访问 `http://127.0.0.1:4321`。修改内容后重新执行 `npm run build`，刷新浏览器。查看服务器输出时按 Control+C 停止。

构建本身没有第三方依赖。只在需要处理新图片时执行 `npm install`，它会安装 sharp。当前执行环境不能联网、不能监听本地端口，已交付静态文件预览。

## 改文字、排序和精选

- `content/profile.json`：姓名、一句话、技能、工作经历、客户项目、奖项与联系方式。只放已确认可公开内容。不填写的字段不会伪造。
- `content/projects.json`：所有真实项目数据。只改对应字段，不需要修改页面代码。
- `order` 越小，作品越靠前；`featured: true` 会进入首页精选。
- `status: "public"` 表示公开；`"hidden"` 或 `"draft"` 不生成页面、不进入列表和站点地图。为保证历史兼容，32 个旧项目须保留公开；如确需隐藏，应同时明确旧链接的新去向，再调整校验规则。
- `summary` 是简短说明。`role`、`background`、`goal`、`process`、`outcome` 分别是职责、背景、目标、过程与成果，留空则整个模块隐藏。无需填满，也不要推测成果。
- `contacts` 例如 `[{"label":"邮箱","url":"mailto:真实邮箱"}]`。社交链接使用完整 `https://` 地址；简历 PDF 放在 `public/`，将 `resume` 设置成 `/文件名.pdf`（推荐英文文件名）。

## 新增作品和放图片

1. 原图继续放在“文稿/作品”，或者设置 `AGNES_ASSETS` 环境变量指定另一个原图目录。不要覆盖原图。
2. 复制 `content/project-template.json` 的对象到 `content/projects.json` 数组末尾，填写标题、唯一的英文 `slug`、分类、封面和图片列表。模板本身不会公开。
3. 分类：`communication` 视觉传达、`ui` UI、`web` 网页、`poster` 海报、`illustration` 插画。
4. 在 `content/media-sources.json` 增加原图映射，例如：

```json
{"original":"Poster Design/你的项目/作品.jpg","src":"media/your-project/01.jpg"}
```

5. 项目的 `cover` 填 `media/your-project/01.jpg`，`media` 填：

```json
[{"src":"media/your-project/01.jpg","alt":"项目名称 · 海报主视觉","caption":""}]
```

6. 执行 `npm install`、`npm run images`。处理脚本生成 AVIF、WebP、JPEG 的多种尺寸，原图不变。再执行 `npm run build` 和 `npm run check`。确认内容可公开后，将项目状态改成 `public` 并重新构建。

`slug` 发布后尽量不要改。它对应 `/work/your-project/`，改变它会改变分享链接。不要再次运行 `scripts/migrate.mjs`：它只用于首次导入，会覆盖你手动编辑的项目数据。

## 图片如何加载

优化图在 `public/media/optimized/`，文件名带源文件哈希。`content/image-meta.json` 记录尺寸和格式，页面自动生成 picture/srcset/sizes。封面使用 contain，完整保留作品边缘；详情尊重原图比例，点击可放大，方向键切换，Escape 关闭。

目前仅本地新素材完成优化；旧素材因网络限制尚未下载。预览中的旧图指向原站。正式部署前必须把旧图带入新部署，否则站点切换后旧图会失效。工作流已包含这个步骤，不要跳过。

```sh
npm run download:legacy
node scripts/prepare-legacy.mjs originals
node scripts/images.mjs --legacy-only
npm run build
npm run check
```

下载脚本固定旧站提交并核对文件大小。GitHub Actions 会直接检出旧站提交、保留完整 images 和 CNAME，再优化旧项目引用的图片。GIF 保留动画及原格式，不强制转视频。没有提供视频素材，因此没有虚构视频入口。

## 发布到 GitHub Pages

当前文件夹是独立本地分支 `rebuild/agnes-2026`，尚未与远程 Git 历史连接，也未推送。不要 force push、不要直接覆盖 master。保留原站：

1. 在网络正常且已登录 GitHub 的终端，另行克隆原仓库，并创建分支：

```sh
git clone https://github.com/xuepeiyao/xuepeiyao.github.io.git agnes-publish
cd agnes-publish
git switch -c rebuild/agnes-2026
```

2. 将本交付中的 `.github`、`content`、`legacy`、`public`、`scripts`、`src`、`reports`、`package.json`、`.gitignore`、`README.md` 复制进克隆目录；不要复制 `.git`、`node_modules`、`dist` 或 `review`。旧仓库根目录已有的原文件可以先保留，构建产物仅由新脚本生成。
3. `git add .`、`git commit -m "Rebuild Agnes portfolio"`、`git push -u origin rebuild/agnes-2026`。这一步只上传独立分支，不切换旧站。
4. 先完成本机浏览器审核。工作流在默认分支尚不存在时，GitHub 网页的“Run workflow”可能不会显示，所以不要假定上传开发分支后已有远程预览。
5. 获得正式发布确认后，将 PR 合并入 master。工作流没有 push 触发器，合并本身不会调用新版 Pages 部署。若旧站由 master 根目录发布，合并时保留旧 index.html 可使旧站继续工作。
6. 在仓库 Settings → Pages 检查现有来源、域名和 HTTPS，记录原配置。切换 Source 为 GitHub Actions 会影响发布来源，应在获准发布后操作；不要改 DNS。
7. Actions → Build and deploy Agnes portfolio → Run workflow，先保持 `PREVIEW`。它只生成可下载的 `agnes-review` 构建与报告。
8. 审核无误且确认发布后再次运行，输入 `DEPLOY`。部署步骤可能需要 GitHub 的 Environment 审批。等待成功，然后检查 `https://xuepeiyao.github.io/`、`/work/`、任一详情页、`/detail.html?id=0` 和关键图片。

本次 GitHub 连接仅提供读取工具；终端无法解析 GitHub 域名，无法替你执行上述远程写入。现有 Pages 来源未能经 API 核实，因此发布前检查不可省略。

## 恢复原站

先记录当前 Pages 来源与默认分支 SHA。原站固定提交为 `5af767fb6a7a26168264efc6e8d257946e4822b1`，不要删除它或重写历史。

如已经用 Actions 发布新版：在 GitHub 新建 `rollback/original-site` 分支指向这个旧提交，将 Pages Source 恢复为 Deploy from a branch，选择该分支的 `/ (root)`，等待发布完成并复查首页和图片。也可以发布之前保存的原站部署产物。保留 CNAME，回滚时不修改 DNS。这个恢复过程不需要对 master 强制推送。

## 实现与验证范围

采用 Node.js 静态生成、JSON 数据及原生 JavaScript，取代 Vue/jQuery/Swiper；运行时无 CDN、无框架脚本、无后台、无跟踪。当前无法安装 Astro，零构建依赖方案可立即运行，且能生成全部稳定独立 URL；`content/types.d.ts` 提供字段类型，构建时执行运行时数据校验。

`npm run check` 检查项目数据、独立页面、32 个旧链接映射、HTML 元信息、本地引用与 sitemap。报告见 `reports/`。真实浏览器布局、线上资源、键盘 Escape 的浏览器原生行为与 Lighthouse 仍需在具备浏览器权限的环境验证，不能把 DOM 模拟测试当作视觉验收。

## 一键上传（推荐）

桌面已放置 `上传Agnes新版到GitHub.command`。双击后会在你本机终端执行构建与检查，使用 GitHub 官方登录，上传带时间戳的独立分支并创建草稿 PR。没有安装 GitHub CLI 时，脚本会从官方发行下载并验证校验和；不会要求你在聊天中发送令牌。

PR 将自动触发远程构建、旧图保留/优化、Chromium 浏览器测试以及可下载的截图和预览。成功后脚本会打开 PR，并将地址记录在 `reports/remote-sync.json`。该流程不会自动合并或修改线上网站。若本机网络也无法访问 GitHub，脚本会报出实际错误并停止。

当前 GitHub 连接的写入测试返回 HTTP 403 `Resource not accessible by integration`，因此仅调整“是否询问”不能修复服务器端授权。也可以在连接管理中重新完成该仓库的 GitHub 写入授权后，由代理再次尝试上传。

### 当前上传方式：GitHub API

桌面上传脚本已改为 API 方式，不再下载仓库或调用 Git push，避开本机 Git 的 LibreSSL 连接错误。重新双击相同脚本，输入已有令牌即可；无需安装 GitHub CLI或重新生成令牌。首次上传约需 5～10 分钟（实际取决于网络与 API 限流），会显示文件数进度。中断后再次运行可复用已上传文件。

脚本使用原仓库 Git tree 和父提交创建唯一的开发分支，并建立草稿 PR。它不更新默认分支、不切换 Pages。缓存文件仅存放 Git blob 哈希，不包含令牌。当前入口以本段为准；前文关于 clone 和 GitHub CLI 的旧同步实现不再使用。
