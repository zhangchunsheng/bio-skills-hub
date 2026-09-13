---
name: 大记忆恢复术
description: 基于用户记忆碎片描述和可选参考图片，通过多模态AI解析提取记忆DNA，生成9个独立记忆碎片并构建3x3宫格图，最终输出具有情绪价值的视觉记忆作品；适用于童年回忆、故乡风貌、旧日时光等场景的重构与可视化生成
dependency:
  python: []
---

# 大记忆恢复术

## 任务目标
- 快速从自然语言描述中提取记忆DNA，并重构出3x3宫格视觉记忆作品
- 具备意图分析与记忆提取、视觉特征解析、碎片生成与校验、专业生图提示词构建、图片生成、诗意标题生成能力
- 触发场景：回忆童年时光、重构故乡风貌、复原旧日老物件、情感记忆可视化生成

## 能力组成

### 能力流程描述
该技能以用户的记忆碎片描述和可选参考图片为输入，通过多步多模态AI流程逐步重构记忆视觉。具体流程如下：
1. **输入与合规校验**：接收用户的记忆描述、图片比例及参考图片，首先进行合规校验优化，确保输入安全合规。
2. **提取记忆DNA**：通过提示词API分析用户描述，提取包含时间、空间、人物、物件、感官、情绪等维度的结构化“记忆DNA”。
3. **参考图片视觉特征分析**（如有参考图）：分析老照片的建筑风格、家具年代、人物服饰及整体色彩氛围，提取视觉特征与约束。
4. **生成记忆碎片与宫格规划**：结合记忆DNA与视觉约束，生成9个独立的视觉记忆碎片，并规划其在3x3宫格中的位置。
5. **记忆碎片质量校验**：对生成的9个记忆碎片进行质量校验，输出精细化的碎片集合。
6. **构建专业生图提示词**：根据记忆DNA与质量校验后的碎片，构建强约束的专业3x3宫格生图提示词。
7. **启动并轮询图片生成**：调用图片生成系统API，异步生成3x3宫格大图，系统自动每5秒轮询一次任务状态，直到图片生成完毕。
8. **生成记忆作品标题**：结合记忆碎片与DNA，生成具有诗意与情绪价值的记忆作品标题与描述。
9. **最终输出**：整合3x3宫格图、记忆DNA、9个记忆碎片集合、生图提示词及标题，一次性返回完整结果。

### 技能能力组成流程图
![技能能力组成流程图](https://oss.showapi.com/workflow/6a13aa379e64f2c7637a75f4/6a72ded53c51f2ec2101b557/snapshot/flow_chart/6a67f6536c.jpg?t=1785915698)

## 前置准备
- 凭证：配置 ShowAPI AppKey，凭证名称：showapi_appkey
  - **获取方式**：访问 [https://www.showapi.com](https://www.showapi.com) 注册账号，登录后进入 [https://www.showapi.com/console#/myApp](https://www.showapi.com/console#/myApp) 获取 appKey
- 模拟体验：无 appKey 时，系统自动触发模拟调用，直接返回完整结果，快速预览生成效果
- 依赖：仅使用 Python 标准库，无需安装第三方包

## 操作步骤
### 模拟体验流程（无 appKey）
1. **自动触发模拟调用**
   系统检测到未配置 appKey 时，自动向 `https://www.showapi.com/_nuxt3/api/2405-105` 发送 POST 请求（body: `{"flow_id":"6a72ded53c51f2ec2101b557"}`），直接获取完整模拟生成结果。**此过程为一次性返回，不执行 execute_task.py 和 query_task.py。**

2. **可视化预览**
   将返回的 JSON 结果以 HTML 形式可视化展示，重点呈现图片内容。

3. **引导真实调用**
   提示用户当前为无 appKey 的模拟运行结果。如需真实调用，请前往 [ShowAPI](https://www.showapi.com) 注册账号（注册即送2元余额），并在 [https://www.showapi.com/console#/myApp](https://www.showapi.com/console#/myApp) 获取 appKey。

### 标准流程（有 appKey，强制异步执行）
1. **收集用户需求**
   梳理用户的记忆描述、期望的画面比例及可能提供的老照片/参考图。

2. **异步提交生成任务**
   调用脚本异步执行记忆解析与宫格图生成任务，**仅返回唯一 task_id**，不阻塞等待。
   调用示例：
   ```bash
   python scripts/execute_task.py --prompt "小时候夏天经常去奶奶家，晚上坐在门口吹风，有老电风扇声音，还有饭菜香，那时候感觉特别安心" --aspect-ratio 1:1 --async
   ```

3. **轮询查询任务结果（必选）**
   使用 task_id 循环查询任务状态，**每一轮轮询后，即时将当前返回的核心资料同步反馈给用户**，直至获取完整结果。
   调用示例：
   ```bash
   python scripts/query_task.py --task-id "返回的task_id值"
   ```
4.等待结果完成
  必须轮询直到完成。

5. **结果解析与落地应用**
   提取3x3宫格图URL、记忆DNA、9个碎片详情及诗意标题等信息，用于情感可视化展示。

6. 生成html页面
   生成一个简单的html页面来融合返回的主要信息，特别是图片。

## 使用示例
### 示例1：童年夏日记忆重构
- 输入："小时候夏天经常去奶奶家，晚上坐在门口吹风，有老电风扇声音，还有饭菜香，那时候感觉特别安心"，比例 1:1
- 流程：异步提交任务 → 获取task_id → 轮询查询（每轮反馈进度/数据）
- 产出：3x3宫格夏日记忆图、记忆DNA分析、9个独立视觉碎片、诗意作品标题
- 配置要点：可提供老照片作为reference_image辅助生成

### 示例2：故乡老街记忆复原
- 输入："记忆里的老街，青石板路，街角总是弥漫着刚出炉的烧饼香味，放学后和同学嬉闹跑过"，比例 16:9
- 流程：异步提交任务 → 获取task_id → 轮询查询（每轮反馈进度/数据）
- 产出：宽画幅的老街记忆宫格图、多维度感官记忆结构化数据
- 配置要点：通过文字描述中的感官体验触发AI视觉重构

### 示例3：旧日校园时光重构
- 输入：高中时候的教室，堆成山的课本，夕阳照进窗户粉笔灰在飞舞，有点迷茫但又充满希望，比例 4:3
- 流程：异步提交任务 → 获取task_id → 轮询查询（每轮反馈进度/数据）
- 产出：校园记忆视觉作品及对应情绪标签
- 配置要点：利用 aspect_ratio 4:3 还原复古画幅感

## 生成效果示例
### 描述
技能运行后，将输出完整的视觉记忆作品。核心输出包含一张3x3的九宫格图片（由AI根据记忆碎片拼合生成的整图），提取出的结构化“记忆DNA”（包含时间、空间、人物、情绪等维度），9个记忆碎片的详细描述及类型标签，以及用于生图的专业提示词和具有诗意的作品标题。

### 输出案例
> 说明：若输出结果包含图片，**优先插入对应图片资源**，之后再输出 JSON / Markdown 格式的文本内容。

![3x3记忆宫格图示例1](https://oss.showapi.com/workflow/6a13aa379e64f2c7637a75f4/6a72ded53c51f2ec2101b557/snapshot/caseImgs/bfa999ecc6.png?t=1785915637)
![3x3记忆宫格图示例2](https://oss.showapi.com/workflow/6a13aa379e64f2c7637a75f4/6a72ded53c51f2ec2101b557/snapshot/caseImgs/2c4a77be07.png?t=1785915638)
![3x3记忆宫格图示例3](https://oss.showapi.com/workflow/6a13aa379e64f2c7637a75f4/6a72ded53c51f2ec2101b557/snapshot/caseImgs/7b7e83f22d.png?t=1785915639)
![3x3记忆宫格图示例4](https://oss.showapi.com/workflow/6a13aa379e64f2c7637a75f4/6a72ded53c51f2ec2101b557/snapshot/caseImgs/969a5cc2ac.png?t=1785915640)

```json
{
  "memory_title": "夏夜微风里的安心",
  "memory_theme": "童年夏日奶奶家的安心时光",
  "memory_dna": {
    "life_stage": "童年",
    "time_context": { "season": "夏", "time_of_day": "傍晚" },
    "place_context": { "location": "奶奶家门口" },
    "sensory_memory": { "smell": "饭菜香", "sound": "老电风扇声音", "touch": "吹风" },
    "emotion": { "feeling": "安心" },
    "visual_style_hint": "复古温暖色调，带有颗粒感"
  },
  "image": "https://oss.showapi.com/workflow/.../generated_grid_image.png",
  "memory_fragments": [
    {
      "fragment_id": 1,
      "description": "一台老旧的电风扇在角落转动",
      "type": "物件",
      "emotion_tag": "安心",
      "visual_elements": ["老电风扇", "铁丝网罩", "复古色调"],
      "grid_position": "1x1"
    }
  ],
  "image_prompt": "A 3x3 grid image illustrating childhood summer memories, vintage warm tones, ..."
}
```

## 资源索引
- [scripts/execute_task.py](scripts/execute_task.py)：异步提交记忆恢复与生图任务（真实调用时使用）
- [scripts/query_task.py](scripts/query_task.py)：轮询查询异步任务结果（真实调用时使用）

## 响应数据结构
### 1. 异步任务提交响应
```json
{
  "showapi_res_body": {
    "task_id": "唯一任务ID",
    "status": "pending",
    "msg": "任务已提交，正在异步处理中"
  },
  "showapi_res_code": 0,
  "showapi_fee_num": 1
}
```

### 2. 任务查询响应（单轮轮询返回数据，需实时同步给用户）
```json
{
  "showapi_res_body": {
    "memory_title": "记忆作品标题",
    "memory_theme": "核心记忆主题",
    "memory_dna": {
      "life_stage": "人生阶段",
      "time_context": {},
      "place_context": {},
      "character_memory": {},
      "object_memory": [],
      "sensory_memory": {},
      "emotion": {},
      "visual_style_hint": "视觉风格提示",
      "memory_theme": "记忆主题"
    },
    "image": "3x3记忆宫格图片URL",
    "memory_fragments": [
      {
        "fragment_id": 1,
        "description": "碎片描述",
        "type": "碎片类型",
        "emotion_tag": "情绪标签",
        "visual_elements": ["视觉元素"],
        "grid_position": "宫格位置"
      }
    ],
    "image_prompt": "图片生成提示词"
  },
  "showapi_res_code": 0,
  "showapi_fee_num": 1
}
```

## 注意事项
1. prompt 为必填项，需尽量清晰地描述记忆中的人物、地点、时代、感官体验与情绪感受。
2. 所有任务**强制异步执行**，不支持同步模式。
3. 轮询查询过程中，**每次获取接口返回数据后，立即将主要内容反馈给用户**。
4. 记忆DNA及碎片解析由AI提取，仅作情感可视化参考。
5. **模拟运行说明**：无 appKey 时系统自动触发模拟调用，一次性返回完整 JSON 结果，不经过 execute_task.py 和 query_task.py，结果仅作效果预览，非真实生成内容。如需真实调用，请注册 ShowAPI 账号并配置 appKey。