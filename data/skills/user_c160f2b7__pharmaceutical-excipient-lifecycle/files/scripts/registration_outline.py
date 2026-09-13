#!/usr/bin/env python3
"""
药用辅料登记资料方案大纲生成器 (Registration Outline Generator)

功能：
1. 根据辅料品种信息和分类，生成完整的登记资料方案大纲（8大模块）
2. 输出 Markdown 格式的撰写提纲，可直接用于指导登记资料编写
3. 标注每个模块的撰写重点、法规依据和风险提示

用法：
    python registration_outline.py
    进入交互模式，按提示输入辅料信息，输出完整的大纲文件。
"""

import sys
import os
from datetime import datetime


# ============================= 预设模板 =============================

CLASSIFICATION_TEMPLATES = {
    "1.1": {
        "title": "第1.1类 — 未经化学修饰的天然来源提取物或发酵产物",
        "note": "全新辅料，需全面开展各项研究",
        "module_3_extra": """
### 3.1 原材料控制（重点关注）
- 药材/原料的基原鉴定（拉丁学名、药用部位、产地）
- 采集/收获时间、加工方法、贮存条件
- 指标成分含量范围
- 农残、重金属、黄曲霉毒素等安全性指标
- 如为动物来源：BSE/TSE风险评估 + 动物检疫证明""",
        "module_4_extra": """
### 4.1 结构确证
- 红外光谱（IR）
- 紫外光谱（UV）
- 核磁共振（NMR: ¹H, ¹³C, 2D-NMR如HMBC/HSQC）
- 质谱（MS: HR-MS, MS/MS）
- X射线粉末衍射（XRD，适用于晶体）
- 比旋度/圆二色谱（适用于手性化合物）

### 4.2 杂质研究
- 有关物质（HPLC法）
- 残留溶剂（GC法，如适用）
- 重金属及有害元素（ICP-MS）
- 元素杂质（ICH Q3D）
- 微生物限度/无菌
- 内毒素（如用于注射）""",
        "module_8_extra": """
### 8.1 毒理学研究（全面开展）
- [ ] 急性毒性试验（啮齿类+非啮齿类）
- [ ] 重复给药毒性试验（至少1个月，依给药途径定）
- [ ] 局部耐受性试验（与临床给药途径一致，如适用）
- [ ] 过敏性试验（主动皮肤过敏/被动皮肤过敏）
- [ ] 刺激性试验（皮肤/黏膜/眼）
- [ ] 溶血性试验
- [ ] 遗传毒性试验（Ames + 微核/染色体畸变）
- [ ] 生殖毒性试验（如预期用于育龄人群）""",
    },
    "1.2": {
        "title": "第1.2类 — 通过化学修饰或合成得到的单一实体",
        "note": "全新辅料，需全面开展各项研究",
        "module_3_extra": """
### 3.1 原材料控制
- 起始物料/中间体的质量标准
- 溶剂、试剂、催化剂清单及质量标准
- 反应条件和纯化工艺控制""",
        "module_4_extra": """
### 4.1 结构确证
- 综合光谱解析（IR, UV, NMR, MS, XRD）
- 元素分析
- 晶型研究（如有多晶型）
- 粒度分布

### 4.2 杂质研究
- 工艺杂质
- 降解杂质
- 残留溶剂
- 元素杂质（ICH Q3D）
- 基因毒性杂质（ICH M7）""",
        "module_8_extra": """
### 8.1 毒理学研究（全面开展）
- [ ] 急性毒性试验
- [ ] 重复给药毒性试验
- [ ] 遗传毒性试验（Ames, 微核, 染色体畸变）
- [ ] 生殖毒性试验（视情况）
- [ ] 局部耐受性试验
- [ ] 过敏/刺激/溶血试验""",
    },
    "2.1": {
        "title": "第2.1类 — 在国产上市药品中已使用",
        "note": "已有使用历史，可简化部分研究",
        "module_3_extra": """
### 3.1 生产工艺
- 如工艺与已上市产品一致，可引用已有工艺验证数据
- 如工艺有差异，需提供变更说明及验证数据""",
        "module_4_extra": """
### 4.1 特性鉴定
- 与已有产品质量对比研究
- 杂质谱对比
- 功能特性对比""",
        "module_8_extra": """
### 8.1 安全性资料
- [ ] 已有安全性文献综述（PubMed/WOS/CNKI检索）
- [ ] 如与已有产品质量对比一致，可减免毒理研究
- [ ] 如给药途径不同或剂量显著增加，仍需补充毒理""",
    },
    "2.2": {
        "title": "第2.2类 — 在进口上市药品中已使用",
        "note": "进口药品中使用历史，需提供质量对比",
        "module_3_extra": """
### 3.1 关键提示
- 需与进口药品所用辅料进行质量对比（多批次）
- 如工艺差异较大，仍需工艺验证""",
        "module_4_extra": """
### 4.1 对比研究
- 与进口药品原用辅料进行质量对比
- 杂质谱/粒径/晶型等关键质量属性对比
- 生物等效性相关功能特性对比（如缓释辅料）""",
        "module_8_extra": """
### 8.1 安全性资料
- [ ] 进口药品安全性文献数据
- [ ] 质量对比一致性证明
- [ ] 如有差异，补充必要的毒理研究""",
    },
    "3.1": {
        "title": "第3.1类 — 在食品中已有使用历史",
        "note": "食品级安全性数据可参考",
        "module_3_extra": """
### 3.1 关键提示
- 食品级与药用级纯度/质量要求不同
- 需增加杂质控制（达到药用级标准）
- 生产工艺是否需要变更（纯化步骤）""",
        "module_4_extra": """
### 4.1 重点差异
- 食品级与药用级质量差异分析
- 增加的杂质控制项目
- 药用级纯度验证""",
        "module_8_extra": """
### 8.1 安全性资料
- [ ] 食品毒理学数据（NOAEL, ADI等）
- [ ] 药用级与食品级差异的安全性评估
- [ ] 补充必要的毒理研究（如给药途径为注射/眼用）""",
    },
}


DEFAULT_TEMPLATE = {
    "title": "第[分类]类 — 其他/未明确分类",
    "note": "建议与CDE沟通确定具体分类和资料要求",
    "module_3_extra": "\n### 3.1 注意\n- 按常规提交生产信息\n- 建议与CDE进行沟通交流",
    "module_4_extra": "\n### 4.1 注意\n- 根据辅料特性补充必要的鉴定项目",
    "module_8_extra": "\n### 8.1 注意\n- 建议与CDE沟通确定毒理研究要求",
}


# ============================= 核心功能 =============================


def generate_outline(answers: dict) -> str:
    """
    生成登记资料方案大纲

    answers 应包含：
        - excipient_name: str
        - category: str
        - route_of_admin: str
        - purpose: str 功能类别
        - dosage_form: str 目标制剂剂型
        - source_type: str
        - is_high_risk: bool
        - is_sterile: bool
        - has_pharmacopoeia: bool
        - pharmacopoeia_list: str
    """

    cat = answers.get("category", "1.1")
    template = CLASSIFICATION_TEMPLATES.get(cat, DEFAULT_TEMPLATE)

    high_risk_note = ""
    if answers.get("is_high_risk", False):
        high_risk_note = """
> ⚠️ **高风险辅料警示**
> - 给药途径：[{route}]，属于高风险给药途径
> - 需特别关注：元素杂质（ICH Q3D）、微生物限度/无菌、局部耐受性
> - 建议在正式申报前与CDE进行沟通交流
""".format(route=answers.get("route_of_admin", ""))

    sterile_note = ""
    if answers.get("is_sterile", False):
        sterile_note = """
> 🔬 **无菌要求**
> - 该辅料用于无菌制剂，需提供无菌工艺验证资料
> - 微生物限度：需达到无菌标准
> - 包装：需采用无菌包装系统
"""

    # 药典情况
    pharm_note = ""
    if answers.get("has_pharmacopoeia", False):
        pharm_note = f"""> 📖 **药典收载情况**
> - 该辅料已被以下药典收载：[{answers.get("pharmacopoeia_list", "")}]
> - 需标注与药典标准的对比分析（如有差异需说明）
"""
    else:
        pharm_note = """> 📖 **药典收载情况**
> - 该辅料尚未被主流药典收载
> - 需制定企业内控质量标准，并与类似辅料标准进行对比
"""

    outline = f"""# 药用辅料登记资料方案大纲

## 文档信息

| 项目 | 内容 |
|------|------|
| 辅料名称 | {answers.get("excipient_name", "")} |
| 登记分类 | {cat} — {template["title"]} |
| 功能类别 | {answers.get("purpose", "")} |
| 目标制剂剂型 | {answers.get("dosage_form", "")} |
| 给药途径 | {answers.get("route_of_admin", "")} |
| 来源类型 | {answers.get("source_type", "")} |
| 生成日期 | {datetime.now().strftime("%Y-%m-%d")} |
| 版本 | v1.0（草案） |

---
{high_risk_note}
{sterile_note}
{pharm_note}
## 核心提示

> {template["note"]}
>
> 本大纲仅供参考，具体内容需根据辅料实际情况和CDE反馈意见调整。

---

## 模块1：登记人基本信息

### 必含内容
- [ ] 登记人名称（中文/英文）
- [ ] 注册地址与生产地址（含GMP证照信息）
- [ ] 营业执照（经营范围：辅料生产）
- [ ] 药品生产许可证（如已取得）
- [ ] 联系人与联系方式
- [ ] 授权委托书（如代理申报）

### 特殊关注
- 境外登记人：需提供中国代理机构授权书及公证认证文件
- 生产企业与登记人不一致时：需说明关系并提供生产授权

---

## 模块2：辅料基本信息

### 必含内容
- [ ] 辅料名称（中文名、英文名、化学名、CAS号、EINECS号）
- [ ] 结构信息：化学结构式/分子式/分子量
- [ ] 理化性质：外观/性状、溶解度（水/有机溶剂）、pH值、熔点/沸点/分解温度、pKa、吸湿性
- [ ] 功能类别：{answers.get("purpose", "")}
- [ ] 建议用量范围
- [ ] 给药途径：{answers.get("route_of_admin", "")}
- [ ] 药典收载情况
- [ ] 已有使用历史证据及文献

### 特殊关注
- 如为混合物：提供组分组成及各组分的功能
- 如为天然提取物：提供提取物比例、指标成分含量范围

---

## 模块3：生产信息

### 必含内容
- [ ] 工艺流程图（含关键步骤标识、IPC控制点）
- [ ] 工艺详述（各步骤参数：温度/时间/pH/压力等）
- [ ] 物料控制清单：原料、溶剂、催化剂、工艺助剂的来源与质量标准
- [ ] 关键工艺参数（CPP）及其控制范围
- [ ] 关键质量属性（CQA）及其控制
- [ ] 中间体控制标准
- [ ] 工艺验证方案与报告（至少三批商业或中试规模）
- [ ] 生产设备清单（型号、材质、生产能力）
- [ ] 清洁验证（非专用设备的交叉污染风险评估）
- [ ] 批产量

{template["module_3_extra"]}

---

## 模块4：特性鉴定

### 必含内容
{template["module_4_extra"]}

### 功能特性（与辅料功能类别相关）
- [ ] 流动性 / 可压性
- [ ] 粒径分布 / 比表面积
- [ ] 黏度 / 流变特性
- [ ] 渗透压
- [ ] 溶解行为
- [ ] pH值 / 缓冲容量
- [ ] 其他：根据辅料功能确定

---

## 模块5：质量控制

### 必含内容
- [ ] 质量标准草案（含检验项目、方法、限度）
- [ ] 方法学验证资料：
  - 专属性
  - 线性与范围
  - 精密度（重复性、中间精密度）
  - 准确度（回收率）
  - 检测限/定量限
  - 耐用性
- [ ] 标准制定依据（论述各限度设定的合理性）
- [ ] 对照品来源与标定信息

### 质量标准项目建议
| 项目 | 建议 | 备注 |
|------|------|------|
| 性状 | 外观、颜色、气味 | 通用 |
| 鉴别 | 化学法/光谱法/色谱法 ≥2种 | 通用 |
| 检查 | pH/水分/重金属/微生物/残留溶剂等 | 依品种 |
| 含量测定 | 主成分含量 | 如适用 |
| 功能指标 | 根据辅料功能确定 | 关键项目 |

---

## 模块6：批检验报告

### 必含内容
- [ ] 不少于**连续三批**商业规模或中试规模批次的检验报告（全项检验）
- [ ] 批间一致性评估（RSD或趋势分析）
- [ ] 与质量标准的对比分析
- [ ] 如已有不同批次，提供批间趋势图/表

### 批次信息表模板
| 批次号 | 生产日期 | 批量 | 检验结论 | 备注 |
|--------|----------|------|----------|------|
| XXX-001 | 202X-XX-XX | XX kg | 合格 | |
| XXX-002 | 202X-XX-XX | XX kg | 合格 | |
| XXX-003 | 202X-XX-XX | XX kg | 合格 | |

---

## 模块7：稳定性研究

### 必含内容
- [ ] 稳定性研究方案
- [ ] **长期稳定性**：25°C±2°C / 60%±5%RH（或30°C±2°C / 65%±5%RH）
  - 取样点：0、3、6、9、12、18、24、36个月
- [ ] **加速稳定性**：40°C±2°C / 75%±5%RH
  - 取样点：0、1、2、3、6个月
- [ ] **影响因素试验**：
  - 高温（60°C）
  - 高湿（RH 90%±5%）
  - 强光照射（总照度≥1.2×10⁶ Lux·hr）
- [ ] 内包材相容性
- [ ] 包装完整性验证
- [ ] 如稳定性研究仍在进行中，需提交稳定性研究承诺书

### 稳定性考察项目
- 性状（外观、颜色）
- 鉴别
- 含量/效价
- 有关物质
- 微生物限度
- 功能特性（如适用）
- 水分
- pH值

---

## 模块8：药理毒理研究
{template["module_8_extra"]}

### 文献评估
- [ ] 全面检索PubMed、Web of Science、CNKI等数据库
- [ ] 收集辅料的安全性数据（毒理、不良反应、相互作用）
- [ ] 整理已有使用历史的安全性证据

---

## 风险评估与建议

### 注册风险识别
| 风险因素 | 风险等级 | 应对措施 |
|----------|---------|---------|
| {answers.get("category", "")}类首次申报 | [建议评估] | |
| {answers.get("route_of_admin", "")}给药途径 | [建议评估] | |
| {answers.get("source_type", "")}来源 | [建议评估] | |
| 药典收载情况 | [建议评估] | |

### 沟通交流建议
- [ ] 建议在正式提交前与CDE进行沟通交流（Pre-IND会议）
- [ ] 重点关注：分类确认、资料要求确认、毒理研究方案
- [ ] 如涉及高风险给药途径，建议主动沟通

---

*本大纲由药用辅料登记资料方案生成器自动生成*
*生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    return outline


def interactive_mode():
    """交互式模式"""

    answers = {}

    print("\n" + "=" * 68)
    print("  药用辅料登记资料方案大纲生成器")
    print("  请提供辅料品种信息\n")

    # 基本信息
    print("[信息1/8] 辅料通用名称：", end="")
    answers["excipient_name"] = input().strip() or "（待确认）"

    print("[信息2/8] 登记分类（如 1.1 / 1.2 / 2.1 / 3.1 等）：", end="")
    answers["category"] = input().strip() or "1.1"

    print("[信息3/8] 功能类别（如 填充剂/崩解剂/润滑剂/表面活性剂等）：", end="")
    answers["purpose"] = input().strip() or "（待确认）"

    print("[信息4/8] 目标制剂剂型（如 片剂/注射剂/眼用制剂/外用制剂等）：", end="")
    answers["dosage_form"] = input().strip() or "（待确认）"

    print("[信息5/8] 给药途径（oral/topical/injection/ophthalmic/inhalation/other）：", end="")
    answers["route_of_admin"] = input().strip() or "oral"

    print("[信息6/8] 来源类型（plant/animal/mineral/synthetic/fermentation/recombinant/other）：", end="")
    answers["source_type"] = input().strip() or "synthetic"

    print("[信息7/8] 是否为高风险辅料？(y/n): ", end="")
    answers["is_high_risk"] = input().strip().lower() in ("y", "yes", "是")

    if answers["route_of_admin"] in ("injection", "ophthalmic", "inhalation"):
        print("  → 检测到高风险给药途径，自动标记为高风险")
        answers["is_high_risk"] = True

    print("[信息8/8] 是否需要无菌工艺？(y/n): ", end="")
    answers["is_sterile"] = input().strip().lower() in ("y", "yes", "是")

    print("  该辅料是否被药典收载？(y/n): ", end="")
    has_pharm = input().strip().lower()
    answers["has_pharmacopoeia"] = has_pharm in ("y", "yes", "是")
    if answers["has_pharmacopoeia"]:
        print("  请注明收载药典（如 ChP/USP/EP/JP）：", end="")
        answers["pharmacopoeia_list"] = input().strip() or "待确认"
    else:
        answers["pharmacopoeia_list"] = "未收载"

    # 生成大纲
    outline = generate_outline(answers)

    # 输出文件名
    safe_name = answers["excipient_name"].replace("/", "_").replace("\\", "_")
    filename = f"登记资料方案大纲_{safe_name}_{datetime.now().strftime('%Y%m%d')}.md"

    # 保存文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(outline)

    print(f"\n{'=' * 68}")
    print(f"  大纲已生成并保存至：{os.path.abspath(filename)}")
    print(f"  请使用Markdown阅读器查看")
    print(f"{'=' * 68}")

    # 显示预览
    print("\n【内容预览】")
    # 只显示前20行
    preview_lines = outline.split("\n")[:20]
    for line in preview_lines:
        print(f"  {line}")
    print(f"  ...（完整内容共 {len(outline.split(chr(10)))} 行，见文件）")


if __name__ == "__main__":
    interactive_mode()
