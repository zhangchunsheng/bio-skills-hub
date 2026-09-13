# 临床 ASR 闭环微调

- 唯一标识：`digital-health-clinical-asr-finetune`
- 显示名称：临床 ASR 闭环微调
- 能力摘要：在临床术语错误率满足门槛后，用官方 NeMo 脚本对 Parakeet TDT v2 做术语感知的监督微调，并以独立 cycle N+1 离线 KER 复评确认改进；不把部署可用性当作模型质量证据。

## 案例素材

1. 评测显示优先药物类别 KER 为 0.42，且清单超过 100 行、每类至少五行，才启动三轮 SFT；训练/验证按实体类别分层并保持行级独立。
2. 用户希望微调流式 Nemotron Speech，明确提示该 SFT 路径已知会产生 UNK 崩溃，改用推荐的 Parakeet 基座；训练采用官方 NeMo 容器和 stock 脚本而非自制 adapter。
3. 本地 GPU 不足而考虑按小时云主机时，先说明每小时、闲置和磁盘成本，等待明确确认后创建实例；训练结束立即 stop 或 delete，并用新的离线 KER 对比周期 N 与 N+1。
