# 医学科学可视化AI视频生成 - 内部参考手册

## 方法论详解

基于ReelMind/Flux Pro/Runway Gen-4的AI科学可视化生成方法论。核心技法：科学准确性四约束（形态/比例/颜色/交互必须基于真实数据）、微观到宏观的尺度过渡叙事（细胞→组织→器官→人体）、多模态参考融合（电子显微镜图+示意图+3D模型作为参考输入）、分层渲染策略（先骨架后细节逐层叠加）。Prompt公式：科学主体+微观环境+运动机制+渲染风格+标注需求。

## 风格特征详解

显微级细胞渲染（细胞器/蛋白质/膜结构）、3D解剖分层展示（骨骼→肌肉→血管→皮肤逐层）、分子动力学模拟（蛋白质折叠/药物结合）、半透明材质+发光边缘、冷色调（蓝/青/紫）科技感配色、标注与图解叠加、微观到宏观尺度过渡

## 详细工作流

### Step 1: 科学需求分析
科学需求分析：确定可视化目标、目标受众（专家/学生/公众）、科学准确性要求

### Step 2: 参考资料收集
参考资料收集：电子显微镜照片、X射线晶体学数据、医学插画参考

### Step 3: 脚本设计
脚本设计：按科学逻辑构建视觉叙事（如信号通路→细胞响应→组织变化）

### Step 4: 多模态融合
多模态融合：上传显微镜图/3D模型/示意图作为AI生成参考输入

### Step 5: Prompt编写
Prompt编写：科学主体+微观环境+运动机制+渲染风格+标注

### Step 6: 分层生成
分层生成：先骨架后细节，逐层叠加生成

### Step 7: 标注叠加
标注叠加：后期添加文字标注、箭头、比例尺等科学注释

## Prompt词库

### 核心Prompt公式
- 基础：`科学主体（细胞/分子/器官） + 微观环境（细胞基质/血管腔/细胞膜） + 运动机制（扩散/分裂/折叠） + 渲染风格（半透明3D/发光边缘/冷色调） + 科学标注`
- 进阶：`主体(细胞类型/分子名称/解剖结构) + 环境(细胞外基质/血流/组织微环境) + 运动(细胞分裂/蛋白质折叠/药物结合动力学) + 渲染(体积渲染/半透明材质/冷色科技蓝青紫调) + 景别(显微级/亚细胞级/分子级) + 参考(基于电子显微镜图/PDB结构数据) + 标注(关键结构文字注解)`

### 景别 (Shot Size)
- 极远景 (Extreme Long Shot / ELS)
- 远景 (Long Shot / LS)
- 全景 (Full Shot / FS)
- 中景 (Medium Shot / MS)
- 近景 (Close-Up / CU)
- 特写 (Extreme Close-Up / ECU)
- 微距 (Macro)

### 运镜 (Camera Movement)
- 推 (Dolly In / Push In)
- 拉 (Dolly Out / Pull Out)
- 摇 (Pan)
- 移 (Truck / Crab)
- 跟 (Tracking Shot)
- 升/降 (Pedestal Up/Down)
- 固定镜头 (Static / Locked-off Shot)
- 手持微晃 (Handheld Slight Shake)
- 航拍 (Aerial / Drone Shot)

### 光照 (Lighting)
- 自然光 (Natural Light)
- 黄金时刻 (Golden Hour)
- 蓝调时刻 (Blue Hour)
- 柔光 (Soft Light)
- 逆光 (Backlight)
- 侧光 (Side Light)
- 霓虹灯 (Neon Light)
- 电影光 (Cinematic Lighting)
- 三点布光 (Three-Point Lighting)
- 窗光 (Window Light)

### 风格化标签
- 电影级 (Cinematic)
- 写实 (Photorealistic)
- 复古 (Vintage/Retro)
- 赛博朋克 (Cyberpunk)
- 极简 (Minimalist)
- 梦幻 (Dreamy/Ethereal)
- 广播级 (Broadcast Quality)
- 纪录片美学 (Documentary Aesthetic)

## 常见问题排查

### 人物/主体变脸不一致
- 原因：Seed值未锁定，Reference未正确注入
- 解决：锁定Seed+上传参考图+开启Character Reference模式

### 视频闪烁/画面不稳定
- 原因：逐帧生成缺乏时间一致性
- 解决：使用首尾帧模式+降低运动复杂度

### 动作穿模/不自然
- 原因：动作幅度设置过大或运动叠加过多
- 解决：降低动作幅度，每次仅描述1-2种运动

### 运动模糊过度
- 原因：快速运动超出AI生成能力
- 解决：降低速度要求，改为"缓慢"+"匀速"

### 风格不稳定
- 原因：多风格混合描述
- 解决：统一风格标签，明确主次比例

## 参考来源
- Wyzowl 2025 Video Marketing Report
- Seedance 2.0 官方文档
- Runway/Kling/Sora 官方文档
- AI视频生成行业最佳实践
