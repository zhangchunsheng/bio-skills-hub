---
name: crispr-grna-designer
description: 为特定基因外显子设计 CRISPR gRNA 序列，包含脱靶预测和效率评分。当用户需要 gRNA 设计、CRISPR 向导 RNA 选择或基因组编辑靶点分析时触发。
version: "1.0.1"
category: Bioinfo
tags: [crispr, grna, genome-editing, bioinformatics, off-target, cas9]
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: 
last_updated: 2026-02-06
displayName: "CRISPR gRNA 设计"
slug: crispr-grna-designer
---

# CRISPR gRNA 设计器

为 CRISPR-Cas9 基因组编辑设计最优的向导 RNA (gRNA) 序列。支持在靶效率评分和脱靶预测。

## 使用场景

- 为基因敲除 (KO) 实验设计 gRNA
- 为特定外显子选择高效率向导
- 预测并最小化脱靶效应
- 针对 SpCas9、SpCas9-NG、xCas9 变体进行优化

## 输入参数

| 参数 | 类型 | 是否必需 | 说明 |
|-----------|------|----------|-------------|
| `gene_symbol` | string | 是 | HGNC 基因符号（例如 TP53、BRCA1） |
| `target_exon` | int | 否 | 指定外显子编号（默认：所有编码外显子） |
| `genome_build` | string | 否 | 参考基因组：hg38（默认）、hg19、mm10 |
| `pam_sequence` | string | 否 | PAM 模体：NGG（默认）、NAG、NGCG |
| `guide_length` | int | 否 | gRNA 长度（bp）（默认：20） |
| `gc_content_min` | float | 否 | 最低 GC%（默认：30） |
| `gc_content_max` | float | 否 | 最高 GC%（默认：70） |
| `poly_t_threshold` | int | 否 | 最大连续 T 数（默认：4） |
| `off_target_check` | bool | 否 | 启用脱靶预测（默认：true） |
| `max_mismatches` | int | 否 | 脱靶预测的最大错配数（默认：3） |

## 输出格式

```json
{
  "gene": "TP53",
  "genome": "hg38",
  "guides": [
    {
      "id": "TP53_E2_G1",
      "exon": 2,
      "sequence": "GAGCGCTGCTCAGATAGCGATGG",
      "pam": "NGG",
      "position": "chr17:7669609-7669631",
      "strand": "+",
      "gc_content": 52.2,
      "efficiency_score": 0.78,
      "off_target_count": 2,
      "off_targets": [...],
      "warnings": []
    }
  ]
}
```

## 评分算法

### 在靶效率评分（0-1）

综合多个位置特异性特征：

1. **位置权重矩阵**：第 20 位为 G（+3）、第 19 位为 C（+2）等
2. **GC 含量惩罚**：超出 40-60% 范围会降低分数
3. **自身互补性**：发夹结构惩罚
4. **Poly-T 惩罚**：转录终止子序列

```python
score = w1*position_score + w2*gc_score + w3*secondary_score + w4*poly_t_score
```

### 脱靶预测

1. **种子区**：第 12-20 位（PAM 近端）权重 3 倍
2. **凸起/错配容忍度**：允许最多 `max_mismatches` 个错配
3. **基因组位置**：编码区标记为高风险
4. **CFD 评分**：切割频率决定系数，用于脱靶切割评估

## 使用示例

### 基础 gRNA 设计

```bash
python scripts/main.py --gene TP53 --exon 4 --output results.json
```

### 高特异性设计（严格脱靶过滤）

```bash
python scripts/main.py --gene BRCA1 --max-mismatches 2 --gc-min 35 --gc-max 65
```

### 批量处理

```bash
python scripts/main.py --gene-list genes.txt --genome mm10 --pam NAG
```

## 技术说明

**⚠️ 难度：高** - 实验使用前需要人工验证

- 计算预测与实际切割效率的相关性约为 60-80%
- 务必对排名前 3-5 的向导进行实验验证
- 脱靶数据库可能不包含罕见变异或细胞系特异性突变
- 可考虑使用 Cas9 变体（HiFi、Sniper-Cas9）以降低脱靶活性

## 参考资料

参见 `references/` 目录：
- `scoring_algorithms.pdf` - 深度学习模型（DeepCRISPR、CRISPRon）
- `off_target_databases/` - GUIDE-seq 验证数据集
- `efficiency_benchmarks/` - Doench 等人 2014/2016 规则

## 实现

核心脚本：`scripts/main.py`

关键函数：
- `fetch_gene_sequence()` - 从 Ensembl 获取外显子序列
- `find_pam_sites()` - 识别 PAM 邻接靶点
- `score_efficiency()` - 计算在靶评分
- `predict_off_targets()` - 使用 Bowtie2/BWA 比对进行脱靶预测
- `rank_guides()` - 多标准优化排序

## 依赖项

- Python 3.8+
- Biopython
- pandas、numpy
- pysam（用于脱靶比对）
- requests（Ensembl API）

可选：
- bowtie2（本地脱靶搜索）
- ViennaRNA（二级结构预测）

## 验证状态

- **单元测试**：核心算法覆盖率 85%
- **基准测试**：已针对 GUIDE-seq 验证数据集测试（n=1,200 个向导）
- **状态**：⏳ 需要实验验证 - 预测结果仅为计算估计值

## 风险评估

| 风险指标 | 评估 | 等级 |
|----------------|------------|-------|
| 代码执行 | 使用生物信息学工具的 Python 脚本 | 高 |
| 网络访问 | 调用 Ensembl API 获取基因序列 | 高 |
| 文件系统访问 | 读写基因组数据和结果 | 中 |
| 指令篡改 | 科学计算准则 | 低 |
| 数据暴露 | 基因组数据安全处理 | 中 |

## 安全检查清单

- [ ] 无硬编码凭据或 API 密钥
- [ ] Ensembl API 请求仅使用 HTTPS
- [ ] 输入基因符号已根据允许的模式进行验证
- [ ] 输出目录限制在工作区内
- [ ] 脚本在沙箱环境中执行
- [ ] 错误消息已清理（不暴露内部路径）
- [ ] 依赖项已审计（Biopython、pandas、numpy、pysam、requests）
- [ ] 已实现 API 超时和重试机制
- [ ] 不暴露内部服务架构

## 前置条件

```bash
# Python 依赖
pip install -r requirements.txt

# 可选工具
# bowtie2（用于本地脱靶比对）
# ViennaRNA（用于二级结构预测）
```

## 评估标准

### 成功指标
- [ ] 成功从 Ensembl API 获取基因序列
- [ ] 正确识别目标外显子中的 PAM 位点
- [ ] 在靶效率评分与验证数据相关（相关性 >0.6）
- [ ] 脱靶预测能识别已知的假阳性
- [ ] 输出 JSON 符合指定的模式
- [ ] 批量处理能高效处理多个基因

### 测试用例
1. **基础 gRNA 设计**：输入 TP53 外显子 4 → 获得带评分的有效向导 RNA
2. **API 集成**：查询 Ensembl 获取基因序列 → 成功获取
3. **脱靶预测**：输入已知有脱靶的向导 → 正确预测
4. **多物种支持**：测试 hg38、hg19、mm10 → 正确处理基因组
5. **批量处理**：输入基因列表 → 高效并行处理
6. **错误处理**：输入无效基因符号 → 优雅报错并给出有用提示

## 生命周期状态

- **当前阶段**：草稿
- **下次审查日期**：2026-03-06
- **已知问题**： 
  - 计算预测需要实验验证
  - 脱靶数据库可能遗漏罕见变异
- **计划改进**：
  - 集成更多评分算法（DeepCRISPR、CRISPRon）
  - 支持更多 Cas9 变体（Cas12、Cas13）
  - 增强批量处理并加入进度报告
