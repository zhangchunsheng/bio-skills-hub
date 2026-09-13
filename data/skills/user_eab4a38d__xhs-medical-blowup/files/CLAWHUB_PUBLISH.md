# ClawHub 发布指南

> SkillHub（腾讯云）审核 3-7 工作日，ClawHub（社区市场）1-3 工作日。**两边同步发，流量双倍。**

## ClawHub vs SkillHub 对比

| 维度 | SkillHub（腾讯云） | ClawHub（社区） |
|------|---------------------|------------------|
| 审核周期 | 3-7 工作日 | 1-3 工作日 |
| 流量 | 慢但精、稳定 | 快但杂、波动大 |
| 审核严格度 | 高（合规+漏洞+AI 安全） | 中（社区驱动） |
| 适合阶段 | 长期主推 | 早期试水+引流 |
| 入口 | skillhub.tencent.com | clawhub.ai |
| CLI | `skillhub` | `clawhub` |
| 变现 | 免费/买断/订阅/分成 | 买断/订阅 |
| 数据 | 平台统一看板 | GitHub 仓库自带 Star |

## 发布步骤（命令行方式）

### Step 1：注册 ClawHub 账号
```bash
# GitHub 登录（推荐）
open https://clawhub.ai/login
# 用 GitHub 账号 OAuth 授权
```

### Step 2：安装 CLI
```bash
npm install -g clawhub
clawhub --version  # 验证安装
```

### Step 3：登录
```bash
clawhub login
# 浏览器会自动打开 GitHub OAuth 授权页
# 凭证存到 ~/.clawhub/auth.json
```

### Step 4：上传 Skill（两种方式）

#### 方式 A：直接上传文件夹
```bash
cd /Users/zhangquanfang/WorkBuddy/2026-09-04-17-56-16/output
clawhub skill publish ./xhs-medical-blowup \
  --slug xhs-medical-blowup \
  --version 1.0.0 \
  --name "医药小红书爆款生成器" \
  --description "30 秒生成可发布的医药类小红书爆款笔记，自动规避广告法违规词。内置合规话术库、5 种爆款结构模板、3 种文风预设。" \
  --tags "小红书,医药,保健品,内容创作,爆款文案" \
  --category "内容创作"
```

#### 方式 B：从 GitHub 导入（推荐）
```bash
# 1. 先推到 GitHub
cd /Users/zhangquanfang/WorkBuddy/2026-09-04-17-56-16/output
git init xhs-medical-blowup
cd xhs-medical-blowup
git add .
git commit -m "feat: 医药小红书爆款生成器 v1.0.0"
gh repo create xhs-medical-blowup --public --source=. --push

# 2. 从 GitHub 导入到 ClawHub
clawhub import --repo https://github.com/<your-username>/xhs-medical-blowup
```

### Step 5：检查发布状态
```bash
clawhub search xhs-medical-blowup
clawhub view xhs-medical-blowup
```

---

## 发布后必做

### 1. 优化 README 展示
GitHub 仓库的 README.md 会作为 ClawHub 详情页展示。已包含的内容：

- ✅ 一句话定位
- ✅ 核心功能列表
- ✅ 快速上手示例
- ✅ 文件结构说明
- ✅ 定价策略
- ✅ 反馈渠道

### 2. 制作 demo gif
录一段 30 秒动图：
- 输入："维生素 D3 + 新手妈妈 + 闺蜜分享风"
- 输出：完整笔记生成过程
- 加速度调到 2x

工具：ScreenFlow / OBS Studio / LICEcap

### 3. 写发布博文
建议发布到：
- 掘金 / CSDN：「我从 0 到 1 上架 SkillHub 赚了 100 元」
- 知乎：「医药商家做小红书爆款的 3 个工具」
- 小红书：「医药老板的私藏神器（不违规）」
- 公众号：引流到 SkillHub 下载页

### 4. 同步到社区
- V2EX：「分享一个医药小红书爆款生成器」
- 即刻：发想法
- 微博：#AI 工具# 话题
- 微信群：垂直行业群（母婴、保健品商家群）

---

## 版本管理

ClawHub 支持语义化版本：

| 版本号 | 含义 | 何时升级 |
|--------|------|----------|
| 1.0.0 | 首发 | 初版 |
| 1.0.x | Bug 修复 | 修复用户反馈的 bug |
| 1.1.0 | 新功能 | 加 1-3 个新功能（如新模板） |
| 2.0.0 | 重大重构 | 架构变化、不兼容更新 |

更新命令：
```bash
clawhub skill publish ./xhs-medical-blowup \
  --slug xhs-medical-blowup \
  --version 1.0.1 \
  --changelog "修复 description 触发词问题"
```

---

## 数据监控

### ClawHub 后台看
- 安装量
- 评分（1-5 星）
- 评论数
- 版本下载分布

### 平台外看
- 知乎/掘金文章阅读量
- 微博话题讨论度
- 小红书引流笔记互动数

### 关键指标
- **安装→使用转化率**：> 30% 算优秀
- **评分**：> 4.5 星算优秀
- **评论率**：> 5% 算优秀

---

## 风险提示

| 风险 | 应对 |
|------|------|
| 评分低于 4.0 | 主动联系差评用户，了解原因，3 天内修复 |
| 流量低 | 在小红书/公众号写"我用 XX 工具做出爆款"引流 |
| 同质化 | 加差异化功能（如"AI 配图 prompt"） |
| 平台下架 | 提前备份 GitHub 仓库，迁移到 ClawHub |

---

## 时间表（同步发布计划）

| 时间 | SkillHub | ClawHub |
|------|----------|---------|
| Day 1 | 提交审核 | 发布 |
| Day 1-3 | 审核中 | 流量测试 |
| Day 4-7 | 通过，开始推广 | 持续优化 |
| Day 7+ | 双平台稳定 | 双平台稳定 |

**关键：ClawHub 上线后立刻引流，SkillHub 通过后无缝衔接**。

---

## 一键命令汇总

```bash
# === SkillHub（慢但稳）===
skillhub login
skillhub push /Users/zhangquanfang/WorkBuddy/2026-09-04-17-56-16/output/xhs-medical-blowup.zip
skillhub publish --visibility public

# === ClawHub（快但杂）===
clawhub login
clawhub skill publish /Users/zhangquanfang/WorkBuddy/2026-09-04-17-56-16/output/xhs-medical-blowup \
  --slug xhs-medical-blowup \
  --version 1.0.0

# === GitHub 仓库（沉淀资产）===
cd /Users/zhangquanfang/WorkBuddy/2026-09-04-17-56-16/output
git init xhs-medical-blowup
cd xhs-medical-blowup
git add .
git commit -m "feat: 医药小红书爆款生成器 v1.0.0"
gh repo create xhs-medical-blowup --public --source=. --push
```

---

## 联系作者

- SkillHub 评论：24h 内回复
- ClawHub 评论：48h 内回复
- GitHub Issues：48h 内回复
- 紧急：直接改 description（用户看到的第一句话）

---

**最后提醒**：先把 ClawHub 发出去（快），3-7 天后 SkillHub 通过接流量。**两个平台共用同一个 SKILL.md，无需重写**。