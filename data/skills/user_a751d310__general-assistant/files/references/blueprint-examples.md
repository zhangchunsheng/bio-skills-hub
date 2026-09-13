# 蓝图示例与表单模板

本文件提供 GA（全能运营指挥官）决策表单模板、完整 JSON 蓝图示例与通知策略详表。SKILL.md 给出精简版，此处为完整参考。

---

## 一、决策表单模板

表单结构：`{ 参数名, 问法, 选项/示例, 默认值 }`。一次性交互呈现，用户填完即确认，不逐项追问。

### 助理型表单（以 FB 发帖为例）

| 参数名 | 问法 | 选项/示例 | 默认值 |
|---|---|---|---|
| material_source | 素材来源？ | 本地文件夹 / 微云 / COS | 微云 |
| clip_rule | 剪辑规则？ | 本地 FB.skill 约束段 / 市场通用 | 本地约束 |
| copy_tone | 文案调性？ | 美式口语 / 英式正式 / 东南亚风 | 美式口语 |
| review_method | 审核方式？ | 腾讯文档智能文档 / HTML面板 / 无需审核 | 腾讯文档 |
| publish_method | 发布方式？ | 封装本地脚本 / Buffer连接器 | 本地脚本 |
| daily_limit | 日更上限？ | 1条 / 2条 / 3条 / 按需 | 2条 |
| timezone | 目标时区？ | 欧洲(CET) / 美国(EDT) / 欧美双发 | 欧美双发 |
| auto_schedule | 自动化时间？ | 素材扫描 02:00 / 审核推送 09:00 / 发布 13:30 & 19:30 | 上述默认 |
| api_key | 关键授权 | API Key、云盘Token等 | （需用户填写） |

### 搭子型表单（以北京旅游为例）

| 参数名 | 问法 | 选项/示例 | 默认值 |
|---|---|---|---|
| travel_dates | 出行日期？ | 例：7/20-7/22 | （需用户填写） |
| interests | 兴趣标签？ | 博物馆 / 美食 / 胡同 / 夜生活 / 摄影 / 历史（可多选） | 博物馆+美食 |
| lodging | 住宿区域？ | 东城区(近地铁) / 朝阳区 / 海淀区 | 东城区 |
| budget | 预算范围？ | 经济型 / 舒适型 / 中档(含2-3顿特色大餐) / 轻奢 | 中档 |
| dietary | 忌口/过敏？ | 无 / 素食 / 海鲜过敏 / 其他 | 无 |
| remind_pref | 提醒偏好？ | 饭点美食推荐 / 天气突变 / 抢票通知（可多选） | 全选 |
| notify_method | 通知方式？ | 企微全程轰炸(允许语音呼叫) / 企微静默 / 仅关键节点 | 企微全程轰炸 |
| pace | 行程节奏？ | 紧凑 / 适中 / 轻松 | 适中 |
| emergency_contact | 紧急联系人？ | 手机号（可选） | （留空） |

---

## 二、完整 JSON 蓝图示例

决策确认后，生成 ME 可执行的结构化 JSON 蓝图：

```json
@助手总包 执行需求：
{
  "project_name": "贴合场景的名字（如 FB社媒SOP / 北京旅游搭子）",
  "project_type": "companion",
  "workflow": [
    {"step": "素材获取", "trigger": "daily@02:00", "skill": "scan_inbox", "config": {"path": "{{material_source}}"}},
    {"step": "视频剪辑", "trigger": "after_素材获取", "skill": "video-clip-assistant-fb", "config": {"rule": "{{clip_rule}}"}},
    {"step": "文案生成", "trigger": "after_剪辑", "skill": "content-writer-fb", "config": {"count": 3, "lang": "en", "tone": "{{copy_tone}}"}},
    {"step": "审核", "trigger": "after_文案", "skill": "tencent-docs", "config": {"mode": "review_table"}},
    {"step": "发布", "trigger": "on_review_approved", "skill": "{{publish_method}}", "config": {"daily_limit": 2, "timezone": "{{timezone}}"}}
  ],
  "experts": [
    {"name": "FB运营官", "bind_skills": ["video-clip-assistant-fb", "content-writer-fb", "tencent-docs"], "bind_kb": ["品牌规范库"]},
    {"name": "FB发布员", "bind_skills": ["Buffer", "fb-slot-scheduler"], "bind_kb": []}
  ],
  "automations": [
    {"name": "素材扫描", "trigger": "daily@02:00", "executor": "FB运营官", "notify": false, "need_decision": false},
    {"name": "文案生成", "trigger": "after_扫描", "executor": "FB运营官", "notify": false, "need_decision": false},
    {"name": "审核推送", "trigger": "daily@09:00", "executor": "FB运营官", "notify": true, "need_decision": true},
    {"name": "欧洲发布", "trigger": "daily@13:30", "executor": "FB发布员", "notify": false, "need_decision": true},
    {"name": "美国发布", "trigger": "daily@19:30", "executor": "FB发布员", "notify": false, "need_decision": true}
  ],
  "notification_policy": {
    "type": "assistant",
    "default_notify": false,
    "notify_when": "need_decision == true",
    "channel": "企微",
    "tone": "concise"
  },
  "decision_log": {
    "material_source": "微云",
    "clip_rule": "本地约束",
    "copy_tone": "美式口语",
    "review_method": "腾讯文档",
    "publish_method": "本地脚本",
    "daily_limit": "2条",
    "timezone": "欧美双发"
  }
}
```

> 搭子型蓝图结构相同，区别在于 `notification_policy.type` 设为 `"companion"`，`default_notify` 为 `true`，`tone` 为 `"热情口语化"`，并增加定时推送类自动化（如饭点推荐、天气预警）。

---

## 三、通知策略详表

通知策略必须与项目类型绑定，贯穿所有自动化：

| 项目类型 | 默认 notify | 语气 | 通知触发条件 | 消息形式 |
|---|---|---|---|---|
| companion（搭子） | `true` | 热情口语化 | 所有自动化都通知 | 企微卡片 + 允许语音呼叫 |
| assistant（助理） | `false` | 简洁专业 | 仅当 `need_decision: true` 或异常时 | 企微卡片消息 |

### 通知模板风格示例

**助理型（简洁专业）：**
```
【审核提醒】FB 帖子待审核
3 条文案已生成，截止 13:00 前确认即可发布。
[查看腾讯文档] [全部通过] [需修改]
```

**搭子型（热情口语化）：**
```
 hey~ 午饭时间到啦！🍚
 附近有家评分 4.8 的京菜馆，步行 5 分钟，招牌烤鸭评价超好～
 要不要帮你查查排队情况？
```
