---
name: "tool-cellchat"
description: "CellChat 2.2.0细胞通讯工具方法：data层输入createCellChat、CellChatDB.human、computeCommunProb(k.min=5,truncatedMean)、全图谱估计后再六群子集、subsetCommunication/netVisual_aggregate与2.2.0列名兼容。Invoke when配体受体通讯分析、TGFb等通路可视化或CellChat版本兼容问题。"
---

> **作者 (author)**: LKP <kunpeng.liao@abiosciences.com>
> **Skill 及脚本参数来源**: Chen et al., 2025, *Cancer Cell* 43, 1656–1676, <https://doi.org/10.1016/j.ccell.2025.06.020>


# CellChat 细胞通讯分析

非空间配体-受体通讯推断（版本 2.2.0，列名与旧版有差异）。

## 1. 输入与创建（全图谱策略）

```r
library(CellChat)
set.seed(2023)
# 输入用归一化 data 层（非 counts）
input <- LayerData(tumor, assay = "RNA", layer = "data")
meta <- data.frame(labels = tumor$cellchat_group, row.names = colnames(tumor))
cellchat <- createCellChat(object = input, meta = meta, group.by = "labels")
cellchat@DB <- CellChatDB.human          # 直接人类全库（不做 Secreted 子集）
cellchat <- subsetData(cellchat)          # 剔除DB外基因
```

**关键策略**：先用整个肿瘤图谱估计通讯概率，再保留目标亚群子集（小亚群单独跑会概率不稳）。

## 2. 推断链

```r
future::plan("sequential")                        # Windows 必须 sequential
options(future.globals.maxSize = 12000 * 1024^2)  # 12GB
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)
cellchat <- computeCommunProb(cellchat, k.min = 5, type = "truncatedMean")
cellchat <- computeCommunProbPathway(cellchat)
cellchat <- aggregateNet(cellchat)
saveRDS(cellchat, "objects/xxx_cellchat.rds", compress = FALSE)
```

`k.min=5`：小群(<5细胞/组)截断均值防 0；`truncatedMean`：组内均值修剪极端值。

## 3. 子集提取与可视化

```r
groups <- c("S02_Schwann-TGFBI", "Ductal cells", "M07_Macro-NLRP3",
            "M09_Macro-APOC1", "F01_mCAF-MMP11", "F03_tCAF-MME")  # 论文六群
stopifnot(length(groups) == 6)
# 2.2.0 兼容：通讯表列名 pathway → pathway_name
df <- subsetCommunication(cellchat, sources.use = groups, targets.use = groups)
if ("pathway_name" %in% colnames(df)) names(df)[names(df) == "pathway_name"] <- "pathway"
# 网络图（如 TGFb 通路）
netVisual_aggregate(cellchat, signaling = "TGFb",
                    sources.use = groups, targets.use = "S02_Schwann-TGFBI",
                    edge.width.max = 8)
```

## 4. Sender 表达配体提取（对接 NicheNet）

```r
# 基因在某群细胞中表达比例 >= 10% 视为表达
expr <- cellchat@data
expressed <- rowMeans(expr[, cells_of_group] > 0) >= 0.10
```

## 常见坑

1. **2.2.0 列名变更**：`pathway` → `pathway_name`，subsetCommunication 后处理需兼容
2. **Windows future**：必须 `plan("sequential")`，multisession 在大图谱 computeCommunProb 崩溃
3. **k.min=5**：群内细胞 <5 时 truncatedMean 失败，需设 k.min
4. **先全图谱后子集**：只跑 6 群子集会高估通讯概率
5. **cellchat 对象巨大**（全图谱 2GB+）：saveRDS(compress=FALSE)，中断后从 rds 续跑可视化
