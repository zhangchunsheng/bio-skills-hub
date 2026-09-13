## 描述： <br>
为特定基因外显子设计 CRISPR gRNA 序列，包含脱靶预测和效率评分。 <br>

该技能仅用于演示目的，不适用于生产环境。 <br>

## 发布者： <br>
[AIPOCH-AI](https://clawhub.ai/user/AIPOCH-AI) <br>

### 许可/使用条款： <br>
MIT-0 <br>


## 用例： <br>
开发者和生物信息学从业者使用此技能生成候选 CRISPR 向导 RNA，评估预测的在靶效率，并查看脱靶摘要以用于基因编辑规划。目前的证据支持仅用于演示和审查，不支持直接用于实验决策。 <br>

### 使用的部署地域： <br>
全球 <br>

## 已知风险及缓解措施： <br>
风险：安全证据表明，该技能将 CRISPR 向导设计呈现为真实结果，但实现中实际使用的是模拟序列数据和模拟脱靶检查。 <br>
缓解措施：在真实的基因和外显子检索、真实的全基因组脱靶分析、明确的模拟模式标注、测试和基准测试经过独立验证之前，应将输出视为仅供演示使用。 <br>
风险：向导 RNA 效率和脱靶预测结果可能对实验室或临床决策产生误导。 <br>
缓解措施：在任何湿实验室使用之前，需要对候选向导进行独立的计算审查和实验验证。 <br>
风险：该工件包含可执行的 Python 代码和未固定版本的科学依赖项。 <br>
缓解措施：在投入使用前，请在沙箱环境中运行、固定并审计依赖项，并限制输出路径。 <br>


## 参考资料： <br>
- [ClawHub 技能页面](https://clawhub.ai/AIPOCH-AI/crispr-grna-designer) <br>
- [评分算法参考](references/scoring_algorithms.md) <br>
- [脱靶数据库参考](references/off_target_databases.md) <br>
- [效率基准参考](references/efficiency_benchmarks.md) <br>
- [GUIDE-seq 数据集参考](https://github.com/tsailabSJ/guideseq) <br>
- [Cas-OFFinder](http://www.rgenome.net/cas-offinder/) <br>
- [CHOPCHOP](https://chopchop.cbu.uib.no/) <br>
- [Ensembl REST API](https://rest.ensembl.org/) <br>


## 技能输出： <br>
**输出类型：** [JSON、Shell 命令、指导说明] <br>
**输出格式：** [包含候选向导、预测评分、脱靶摘要和警告的 JSON 结果；Markdown 指导说明可能包含命令示例。] <br>
**输出参数：** [1D] <br>
**与输出相关的其他属性：** [输出结果为计算预测，根据安全证据，除非实现经过独立验证，否则可能为模拟或仿真数据。] <br>

## 技能版本： <br>
0.1.0（来源：服务器发布元数据） <br>

## 伦理考量： <br>
用户应评估该技能是否适合其环境，在依赖任何生成或修改的文件之前进行审查，并在部署前遵循其所在组织的安全、保密及合规要求。 <br>
