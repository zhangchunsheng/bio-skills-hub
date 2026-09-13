# C1 · 医院 GCP 机构指南采集

## 目标

给定一家医院，找到其**官方公开**的 CRA 工作指引 / 监查 SOP / 办事指南，按「最新优先」呈现，并打开网页。

## 工作流

### 1. 检索（并行 2 条查询）
- `"<医院名> CRA 监查员 工作指引 SOP 药物临床试验机构"`
- `"<医院名> 临床试验机构 办事指南 监查"`

优先命中形态：医院**主站**的「科研 / 临床试验机构 / 办事指南」栏目（`*/cat/*`、`*/info/*/*.htm`）；独立 **GCP 子站**（`gcp.<domain>`）；常见 CMS（博达等）栏目页 `.../bszn.htm`。

### 2. 确认最新版本（关键）
- 打开**列表页**按日期看有无更新条目（立项须知、结题流程、安全性信息报告流程）。
- **老式 ASP 站点**（`fwzx.asp?a=lm_xx`、`info/1510/xxxx.htm`）：子栏目链接常不在正文，需对原始 HTML **正则扫 href** 抓参数（如 `lm_96` 下辖 `lm_97~lm_101`）。
- **同名文件可能重复上传**：同标题多个 id（不同日期）→ 下载 PDF 做**文本 diff / 比对文件大小**，取日期较新者。
- **特别注意「变更通知 / 迁移公告」**：很多机构已把指南迁到**临床试验综合管理平台**（`*.digitalp.cn`、CTMS、eSite 等），此时官网旧页面只是历史版本，须标注。
- **旧版不隐藏**：最新版在前并重点标注，旧版在后标「仅供参考/可能已过时」。

### 3. 抓正文（**优先用本技能自带脚本，跨平台**）

- **首选**：本技能自带只读抽取脚本（本技能 `scripts/extract_text.py`），**不依赖平台**，已内置中文编码回退：
  - `python3 extract_text.py page.html` → 输出正文
  - `python3 extract_text.py page.html --links pdf` → 只列页面里的 PDF 直链
  - `python3 extract_text.py guide.pdf` → 抽 PDF 文本（优先 `pdftotext`，缺失时回退 `pypdf`）
- 抓页面本身用 `WebFetch`；若 `fetch failed`（`WebFetch` 对 **http 站点会自动升级 https**），退回 `curl`：
  `curl -sSL --max-time 30 -A "Mozilla/5.0" "<url>" -o <工作目录>/page.html`
  —— **落盘到当前工作目录，不要写死 `/tmp`（Windows 无此路径）**。
- 中文站点常为 `utf-8-sig` / `gbk`，脚本已按 `utf-8-sig → gbk → utf-8` 依次尝试解码（不必手工处理）。
- 去标签提正文：删 `<script>/<style>` → 把 `</p></div></li></tr>`、`<br>` 换成换行 → `html.unescape`；从「正文 / 当前位置」之后截取（脚本的 `--after` 参数即为此）。
- PDF 直链型站点：优先 `pdftotext`；若抽不出文字（**公文体 PDF 常见**），改用无 `-layout` 模式或 `pypdf` —— 脚本已自动两段回退。

### 4. 登录墙 / 内网处理（重要）
- 平台类页面多为 SPA（`#/portal/...`），curl 只能拿到空壳。
- 探测公开接口（如 `/api/portal/announcement/list`）；返回 `{"code":401,"message":"未登录"}` 即需登录。
- **遇到需登录 / 内网：不停下、不只报失败**。标注「🔒 需登录/内网，无法访问」，继续把**公开渠道能查到的**全部展示。
- **不使用用户凭据代登录、不越权访问**。

### 5. 呈现
- 用 `present_files` 打开，**顺序 = 重要性**：最新版在前，旧版在后。
- 只对**公开可达**的 URL 调用打开；登录墙平台仍可列（用户自行登录），说明中注明需登录。
- 文末给「版本对照」：指出旧版已失效信息（旧网址/邮箱/联系人），给出**当前有效**联系方式。

## 输出模板

1. ⚠️（如有）渠道已变更：最新指南在「XX 平台」，需登录，无法抓取
2. 🟢 最新版：标题 + 日期 + 链接 + 要点
3. ⚪ 旧版（仅供参考）：标题 + 日期 + 链接 + 与新版差异
4. 📁 栏目索引页链接
5. 现行联系方式 / 待确认项

## 已知样例（仅示范**方法论**，不是现行情报）

> ⚠️ 下列 URL 与日期是**抓取当时**的记录，**随时可能变化**。引用前必须**实时复核**；过期一律按「旧版」处理，不得当作现行要求告知用户。

- 中山大学附属第一医院：主站 `fahsysu.org.cn/article/18323`（2019 工作指引，旧）；GCP 站 `gcp.fahsysu.org.cn/index.php/article/21165`（2025-06-20 监查 SOP，最新）；栏目 `fahsysu.org.cn/cat/559`
- 江南大学附属医院：`wuxihospital.com/info/1510/3412.htm`（2021 CRA 须知）；栏目 `wuxihospital.com/kxyj1/lcsyjg1/bszn.htm`；2025-09-25 起迁至 `wxjngcp.digitalp.cn`（需登录）
- 濮阳油田总医院：栏目 `pysytzyy.com/pc/fwzx.asp?a=lm_96`，**下载专区 lm_100**；CRA 工作指引 V3.3 `?a=newsview_3476`（2024-12-18，PDF 直链）；管理制度 V3.3 `?a=newsview_3473`。⚠️ 同名重复上传，比对后取 3476
- 衢州市人民医院：官网「GCP机构」栏目 `qzhospital.com/news_list.aspx?kind_id=68&menuid=64`（条目为 `detail.aspx?NewsId=xxx`，需进详情页抓 `UploadFile/...pdf`）；抓取时最新为《GCP机构办指南2026》（2026-07）；另有《临床试验管理平台CRA操作手册》；公开平台 `qzsrmyy.runtrial.net`（免登录）
