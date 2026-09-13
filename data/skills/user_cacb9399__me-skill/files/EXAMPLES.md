# me.skill 使用示例

## 快速入门

### 问题 1: "我是谁?"

**触发**: me skill 自动激活

**执行流程**:
1. 读取 `USER.md` 和 `IDENTITY.md`
2. 扫描最近安装的 skills
3. 呈现简要档案

**示例输出**:
```markdown
## 🧑 你是谁

你是 joinishu,在腾讯工作,主要负责后端开发和 DevOps。
从你安装的 55 个 skills 来看,你是一个追求效率的技术专家,
关注企业工具集成、数据分析、自动化和知识管理。

## 💼 专业档案

**角色**: 后端工程师 / DevOps
**领域**: 企业工具、大数据、基础设施
**工具**: gongfeng, claude-internal, tapd, iwiki, datatalk

## 🎯 关键模式

- **工作风格**: 自动化优先,工具驱动
- **兴趣**: 知识管理、研效分析、监控告警
- **偏好**: CLI 工具、内网平台集成

## 📊 技能分布

### 开发工具 (8)
- claude-internal, gongfeng, distill-person...

### 企业集成 (6)
- tapd, iwiki, km, lexiang, eplus...

### 数据分析 (3)
- datatalk-card-query, tencent-bigdata...
```

---

### 问题 2: "深度分析我"

**触发**: 详细模式

**执行流程**:
1. 完整 memory 扫描(14天)
2. Skills 分类统计
3. 加载 `detailed-template.md`
4. 生成全面报告

**输出结构**:
- 📋 执行摘要
- 🧑 核心身份
- 🎭 性格画像
- 💻 技术档案
- ⏰ 行为模式
- ❤️ 偏好设置
- 🌱 成长领域
- 📊 技能生态
- 💡 可操作洞察

---

### 问题 3: "我应该学什么?"

**触发**: 技能推荐模式

**执行流程**:
1. 分析当前 skill set
2. 识别技能空白
3. 从 memory 提取目标
4. 匹配推荐

**示例输出**:
```markdown
## 🎯 技能推荐

基于你的档案分析:

### 强项领域
- ✅ 企业工具集成 (6 skills)
- ✅ 知识管理 (多平台覆盖)
- ✅ 代码开发 (gongfeng, claude-internal)

### 潜在成长方向

1. **前端开发**
   - 理由: 你专注后端,但缺少前端技能
   - 推荐: 学习 React/Vue,安装 frontend-webapp-builder

2. **数据可视化**
   - 理由: 有数据查询能力,缺少可视化
   - 推荐: 学习 ECharts/D3.js

3. **测试自动化**
   - 理由: 有 DevOps 技能,可补充测试
   - 推荐: 安装 playwright skill

### Skill 推荐
- [ ] `frontend-webapp-builder` - 补充前端能力
- [ ] `database-skill` - 增强数据库操作
- [ ] `test-automation` - 自动化测试
```

---

## 高级用法

### 组合查询

```
用户: 分析我的工作习惯,推荐优化建议

Agent 执行:
1. 读取 memory/2026-04-*.md (最近日志)
2. 提取时间戳分布
3. 分析任务类型
4. 识别效率瓶颈
5. 提供优化建议
```

### 对比分析

```
用户: 对比我和另一个工程师的技能差异

Agent 执行:
1. 运行 me skill 获取自己的档案
2. 如果对方有 distill-person skill,加载对比
3. 列出共同点和差异
4. 推荐互补学习方向
```

---

## 隐私保护

### 安全机制

✅ **主会话 (main session)**:
- 可访问 MEMORY.md
- 可读取所有 memory files
- 完整档案分析

⚠️ **群聊 (group chat)**:
- 不访问 MEMORY.md
- 仅公开信息
- 有限档案分析

❌ **禁止行为**:
- 暴露 tokens/passwords
- 引用完整私密对话
- 泄露敏感项目信息

### 置信度标记

所有分析都包含置信度:
- **确定** ✅: 来自明确文件
- **推测** 🔍: 基于模式推断
- **可能** ❓: 低置信度猜测

---

## 故障排查

### 问题: "Skill 没有触发"

**可能原因**:
1. 问题不够明确
2. 描述词未匹配

**解决方法**:
- 明确说 "使用 me skill 分析"
- 或直接问 "我是谁?"

### 问题: "分析不够深入"

**可能原因**:
1. Memory files 不存在
2. Skills 数量少

**解决方法**:
- 创建 USER.md / MEMORY.md
- 写 daily logs (memory/YYYY-MM-DD.md)
- 安装更多 skills

### 问题: "隐私担忧"

**解决方法**:
- 检查 session type (main/group)
- 要求 "只分析公开信息"
- 审查输出,要求删除敏感部分

---

## 最佳实践

### 1. 定期更新档案

```bash
# 每周更新 USER.md
# 记录新学习的技能
# 更新偏好设置
```

### 2. 写 Daily Logs

```bash
# 创建 memory/2026-04-13.md
# 记录重要决策
# 记录学到的教训
```

### 3. 定期回顾

```
每月问一次: "深度分析我,对比上个月的变化"
```

### 4. 结合其他 Skill

```
me skill + distill-person = 团队画像
me skill + skill-creator = 个性化 skill 开发
me skill + work-at-tencent = 内网工具推荐
```

---

## 开发者笔记

### 扩展建议

1. **时间线分析**: 可视化技能成长轨迹
2. **团队对比**: 多人档案对比功能
3. **自动报告**: 定期生成成长报告
4. **推荐引擎**: AI 驱动的 skill 推荐

### 贡献指南

改进建议:
- 增加新的分析维度
- 优化分类算法
- 改进隐私保护
- 扩展输出格式

提交 PR 到 me skill 仓库

---

**版本**: 1.0  
**作者**: joinishu  
**更新**: 2026-04-13
