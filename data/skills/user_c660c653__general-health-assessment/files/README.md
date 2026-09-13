# 通用健康评估（general-health-assessment）

把普通运动人群或久坐人群的**体测数据 + 运动手表/App/体测设备数据**，变成一份带真实计算、可视化图表和可执行建议的专属「运动健康体检报告」。

---

## 一句话说明

不是模板套话，而是带入你的真实数值，算出 BMI、心率五区间、强度结构、运动模式风险，并指出那些"练得不少却没效果"的反直觉根因。

## 这个技能能做什么

- **解读体测数据**：BMI、体脂率、腰围、腰臀比、静息心率，对照中国成人标准判定肥胖/中心性肥胖。
- **揪出强度倒挂**：Z4 阈值区占比过高、Z2 有氧区过少，是"练得多却体脂高"的常见根因。
- **分析运动手表/App 数据**：心率区间分布、平均/最大心率、步数/距离/配速，一眼看出"你是不是一直在阈值区硬撑"。
- **评估运动模式与动作质量**：结合运动类型（跑步/健身/游泳/瑜伽等）与旧伤，提示代偿与关节劳损风险。
- **有氧能力结构**（有 FTP/跑步功率/骑行台功率时）：功率六区间、W/kg 分级、基于功率的"慢运动"目标值。
- **多数据源交叉验证**：手表 App + 跑步机/智能设备/运动 App 同一 session 的不同切片，不再被平均值误导。
- **饮食与补给分析**（有饮食记录时）：三大营养素结构、训练日补给方案。
- **女性月经周期与训练周期化**（女性用户并提供月经数据时）：周期阶段推算与训练适配。
- **久坐人群评估**：活动量、站立时间、NEAT（非运动性活动产热）与基础健康风险。

## 适合谁用

- 想减脂但掉秤慢、总觉得"动得多却没瘦"的普通运动者
- 想知道自己训练强度合不合理的健身/跑步/游泳爱好者
- 有旧伤、想科学防护的运动人群
- 久坐办公、想改善精力与体成分的上班族
- 想"认识自己运动状态"的普通运动者
- 想帮朋友/客户做健康体检报告的人

## 你需要提供什么（输入）

**必填核心项**：年龄、身高、体重（用于算 BMI 和心率区间）。
**建议补充**：体脂率、腰围、臀围、静息心率；一次运动数据（手表/App 截图/导出：距离/步数、心率区间、时长）。
**可选**：功率计 FTP、饮食记录、损伤史、女性月经数据（自愿）、睡眠情况。

> 收数可以发一份**纯前端数据收集表**（`assets/inquiry-form.html`）给对方填，填完生成自带截图的自包含 .html，直接回传即可。

## 你会得到什么（输出）

一份自包含 HTML 报告，浏览器打开即看、本地可存，包含：
核心指标卡 → 反直觉洞察卡 → 体成分评估（BMI 定位条）→ 运动数据深度解读（心率区间分布条 + 运动模式分析）→ 综合诊断 → 修正周训练计划 → 损伤防护 → 恢复监测说明 → 行动项 → 参考文献。

**红线**：本报告为运动健康评估，**不构成医疗诊断**；旧伤防护为运动建议，不适请就医。

## 一个最小例子

输入（节选）：
- 男 / 35岁 / 175cm / 85kg / 体脂28% / 腰围92cm
- 单次跑步：5km / 配速6:30 / 平均心率 155 / Z4 占 50%、Z2 仅 15%

报告会告诉你：
- BMI 27.8（超重）、腰臀比 0.95（中心性肥胖）→ "运动型体成分不佳"
- **强度倒挂**：Z4 占 50%（健康应 ≤5%），Z2 仅 15%（健康应 ≈80%）
- 根因不是运动量不够，而是强度结构错了 → 给出"80% 拉回 Z2"的修正周计划

完整示例见 `assets/sample-report.html`（虚构数据，仅作展示）。

## 快速上手

1. 收集对方的体测 + 运动数据（用 `assets/inquiry-form.html` 或手动询问）。
2. 让 AI 用本技能跑计算与诊断。
3. 基于 `assets/report-template.html` 生成 HTML 报告并交付。

**怎么触发？** 直接对 AI 说以下任何一句话即可：
- 「帮我做一份健康评估」
- 「分析我的运动数据」
- 「解读我的心率区间」
- 「我想知道自己的运动强度结构对不对」
- 「为什么我运动不少却体脂高」
- 「帮我看看运动模式/动作合不合理」
- 「评估我的睡眠和恢复」
- 「帮我做体测报告」
- 「多数据源交叉验证」
- 「帮朋友做健康体检报告」
- 「我是女性，帮我安排月经周期训练」

**数据不全怎么办？** 技能会明确告诉你缺什么、错在哪，并给出正确格式示例——不会沉默跳过或自己假设值。

## 第一次使用，照这 5 步走

1. **触发技能**：对 AI 说"帮我做一份健康评估"（或上面「怎么触发」里的任意一句）。
2. **填收数表**：打开 `assets/inquiry-form.html`，填体测 + 运动数据，点「下载数据卡」生成自带截图的自包含 .html 回传；或直接把运动手表/App 截图发给 AI 也行。
3. **等 AI 读取与分析**：AI 会先核对数据；若缺项会明确告诉你补什么、格式错在哪（不会自己编）。
4. **拿到 HTML 报告**：浏览器打开即看，含指标卡、心率区间、运动模式、周计划等模块。
5. **看不懂就问**：报告里任何结论可直接追问 AI 解读；体脂/腰围缺失不影响核心诊断。

> 对话中途断开？重新上传数据卡 .html 即可恢复全部数据，无需从头填写。更多疑问见下方 FAQ。

## FAQ

**Q：只有手表 App 截图，没有专业设备，能用吗？**
可以。手表 App 数据（华为运动健康 / Garmin Connect / Keep / 悦跑圈 / Apple Watch 等）同样支持，只是室内模式会包含热身冷身、平均值被拉低——技能会标注记录范围并修正。

**Q：没有体脂率和腰围，还能出报告吗？**
年龄、身高、体重是核心必需项，缺少无法继续。体脂率和腰围缺失时会标注"未提供"——不影响核心诊断（强度倒挂），但体成分评估会受限。

**Q："强度倒挂"是什么意思？**
指你大比例时间卡在 Z4 阈值区（健康应 ≤5%），而 Z2 有氧区占比极低（健康应 ≈80%）。这导致"练得多却体脂高"——一直在高强度消耗糖原，而非有氧燃脂。

**Q：我没有功率计/跑步功率，能做有氧能力评估吗？**
可以。无功率设备时不输出功率六区间，改由心率区间 + 可选简易有氧测试（如 3 分钟台阶试验后心率、心率恢复 HRR）估算有氧能力，并在报告中标注"非功率实测"。

**Q：女性用户必须提供月经数据吗？**
不强制。不提供则不含月经周期与训练周期化部分，其余诊断不受影响。

**Q：这是医疗诊断吗？**
不是。这是运动健康评估，旧伤防护属于运动建议。如有身体不适，请及时就医。

## 常见误区（别踩这些坑）

- **把室内热身/冷身算进"有效运动"** → 会拉低平均心率与强度判定，误判强度。应标注记录范围，仅用主运动段。
- **只看平均心率、不看区间分布** → 平均正常也可能大半时间在阈值区硬撑（强度倒挂），必须以区间占比为准。
- **单次体脂秤数据当标准** → BIA 受饮水/进食/时段影响大，取多次空腹均值才稳。
- **用"220−年龄"硬套最大心率** → 个体差异极大，用实测峰值或储备心率法校准。
- **以为"动得越累越减肥"** → 高强度过多反而不燃脂，减脂要拉回 Z2。
- **动作模式不当被忽视** → 跑步跨步过大、力量训练代偿、长期单一姿势，会造成关节慢性劳损——比"强度"更隐蔽。

## 许可证

本项目以 MIT 许可证发布。版权归属：青蓝工作室（Qinglan Studio）。

```
MIT License

Copyright (c) 2026 青蓝工作室 (Qinglan Studio)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
