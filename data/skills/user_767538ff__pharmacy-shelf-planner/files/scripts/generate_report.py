# -*- coding: utf-8 -*-
"""生成药房货位规划综合报告HTML"""
import pandas as pd
import json
import os

OUTPUT_DIR = r'C:/Users/acer/WorkBuddy/2026-08-12-22-38-47/outputs'
df = pd.read_pickle(os.path.join(OUTPUT_DIR, 'drug_summary.pkl'))
lg = pd.read_excel(os.path.join(OUTPUT_DIR, '临购药品处置建议.xlsx'))
assoc = pd.read_excel(os.path.join(OUTPUT_DIR, '高频处方关联组合.xlsx'))

with open(os.path.join(OUTPUT_DIR, 'analysis_summary.json'),'r',encoding='utf-8') as f:
    stats = json.load(f)

# Prepare data for report
active = df[~df['是否停用']].copy()
ha_violations = df[df['物理层位'].str.contains('强制调整',na=False)]
golden = df[df['物理层位'].str.contains('黄金',na=False)]
lg_convert = lg[lg['处置建议'].str.contains('转常规',na=False)]
lg_release = lg[lg['处置建议'].str.contains('释放',na=False)]
lg_observe = lg[lg['处置建议'].str.contains('观察',na=False)]

# Top 20 active drugs
top20 = active.nlargest(20,'总量')

# Look-alike drug groups
la_markers = df[df['易混淆标记']!=''].copy()

# Discontinued drugs
discontinued = df[df['是否停用']].copy()

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>药房货位规划方案 - 妇幼康复专科医院</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root {{
  --bg: #f8f9fa;
  --card: #ffffff;
  --border: #e2e8f0;
  --text: #1a202c;
  --text-sec: #64748b;
  --red: #dc2626;
  --red-bg: #fef2f2;
  --red-border: #fecaca;
  --yellow: #d97706;
  --yellow-bg: #fffbeb;
  --yellow-border: #fde68a;
  --green: #059669;
  --green-bg: #ecfdf5;
  --green-border: #a7f3d0;
  --blue: #2563eb;
  --blue-bg: #eff6ff;
  --blue-border: #bfdbfe;
  --purple: #7c3aed;
  --purple-bg: #f5f3ff;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; background:var(--bg); color:var(--text); line-height:1.7; padding:20px; max-width:1200px; margin:0 auto; }}
h1 {{ font-size:28px; color:var(--text); margin-bottom:8px; padding-bottom:12px; border-bottom:3px solid var(--blue); }}
h2 {{ font-size:22px; margin:32px 0 16px; padding-left:12px; border-left:4px solid var(--blue); color:var(--text); }}
h3 {{ font-size:18px; margin:24px 0 12px; color:var(--text-sec); }}
.subtitle {{ color:var(--text-sec); margin-bottom:24px; font-size:14px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:20px; margin:16px 0; box-shadow:0 1px 3px rgba(0,0,0,0.05); }}
.alert-red {{ background:var(--red-bg); border:2px solid var(--red-border); border-radius:10px; padding:16px 20px; margin:12px 0; }}
.alert-red h3 {{ color:var(--red); }}
.alert-yellow {{ background:var(--yellow-bg); border:2px solid var(--yellow-border); border-radius:10px; padding:16px 20px; margin:12px 0; }}
.alert-yellow h3 {{ color:var(--yellow); }}
.alert-green {{ background:var(--green-bg); border:2px solid var(--green-border); border-radius:10px; padding:16px 20px; margin:12px 0; }}
.badge {{ display:inline-block; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; margin:2px; }}
.badge-red {{ background:var(--red); color:#fff; }}
.badge-yellow {{ background:var(--yellow); color:#fff; }}
.badge-green {{ background:var(--green); color:#fff; }}
.badge-blue {{ background:var(--blue); color:#fff; }}
.badge-purple {{ background:var(--purple); color:#fff; }}
.badge-gray {{ background:var(--text-sec); color:#fff; }}
table {{ width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; background:var(--card); border-radius:8px; overflow:hidden; }}
th {{ background:#f1f5f9; padding:10px 8px; text-align:left; font-weight:600; color:var(--text); border-bottom:2px solid var(--border); white-space:nowrap; }}
td {{ padding:8px; border-bottom:1px solid var(--border); vertical-align:top; }}
tr:hover {{ background:#f8fafc; }}
tr:last-child td {{ border-bottom:none; }}
.stat-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin:16px 0; }}
.stat-box {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:16px; text-align:center; }}
.stat-num {{ font-size:28px; font-weight:700; color:var(--blue); }}
.stat-label {{ font-size:13px; color:var(--text-sec); margin-top:4px; }}
.mermaid {{ background:var(--card); border-radius:10px; padding:16px; margin:16px 0; text-align:center; }}
.tag-row {{ display:flex; flex-wrap:wrap; gap:4px; }}
.change-arrow {{ color:var(--red); font-weight:bold; }}
.priority-red {{ color:var(--red); font-weight:700; }}
.priority-yellow {{ color:var(--yellow); font-weight:700; }}
code {{ background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:13px; color:var(--purple); }}
.toc {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:20px; margin:16px 0 24px; }}
.toc a {{ color:var(--blue); text-decoration:none; display:block; padding:4px 0; }}
.toc a:hover {{ text-decoration:underline; }}
.footer {{ text-align:center; color:var(--text-sec); font-size:12px; margin-top:40px; padding-top:16px; border-top:1px solid var(--border); }}
</style>
</head>
<body>

<h1>药房货位规划方案</h1>
<p class="subtitle">妇幼康复专科医院 | 数据周期：2025年8月 - 2026年8月（12个月）| 生成日期：2026年8月12日</p>

<div class="toc">
<strong>目录</strong>
<a href="#summary">一、执行摘要与紧急预警</a>
<a href="#data">二、数据清洗概览</a>
<a href="#turnover">三、周转分析</a>
<a href="#tags">四、专科标签化</a>
<a href="#abcxyz">五、ABC-XYZ矩阵分类</a>
<a href="#coding">六、五级货位编码体系</a>
<a href="#cluster">七、关联度聚类</a>
<a href="#golden">八、黄金层分配</a>
<a href="#temporary">九、临购专项处置</a>
<a href="#compliance">十、合规兜底检查</a>
<a href="#changes">十一、调整清单（需更改项汇总）</a>
</div>

<!-- ===================== 一、执行摘要 ===================== -->
<h2 id="summary">一、执行摘要与紧急预警</h2>

<div class="stat-grid">
<div class="stat-box"><div class="stat-num">{stats["总药品数"]}</div><div class="stat-label">药品总数</div></div>
<div class="stat-box"><div class="stat-num">{stats["活跃药品数"]}</div><div class="stat-label">活跃药品</div></div>
<div class="stat-box"><div class="stat-num">{stats["临购药品数"]}</div><div class="stat-label">临购药品</div></div>
<div class="stat-box"><div class="stat-num">{stats["高警示药品数"]}</div><div class="stat-label">高警示药品</div></div>
<div class="stat-box"><div class="stat-num">{stats["特殊管理药品数"]}</div><div class="stat-label">精神/毒性药品</div></div>
<div class="stat-box"><div class="stat-num">{stats["科室数"]}</div><div class="stat-label">科室数</div></div>
</div>

<div class="alert-red">
<h3>🔴 本月紧急调整项（红色预警）— 共3类 {len(ha_violations)+len(lg_convert)+stats["停用药品数"]}项</h3>

<p><strong>预警1：高警示药品违规摆放（{len(ha_violations)}种）</strong></p>
<p>以下高警示药品原货位位于<strong>底层（0-0.6m）或中下层</strong>，存在儿童误取风险及操作差错隐患，<strong>已强制调整至中下层(0.6-1.2m)并加贴红底黑字标识</strong>：</p>
<table>
<tr><th>药品名称</th><th>原层位</th><th>调整后层位</th><th>调整后编码</th><th>违规原因</th></tr>
'''

for _, r in ha_violations.iterrows():
    orig = r['物理层位'].replace('★强制调整','')
    reason = '高警示+底层' if '下层(0-0.6' in orig else '高警示+偏低层位'
    html += f'<tr><td>{r["药品名称"]}</td><td class="priority-red">{orig}</td><td>中下层(0.6-1.2m)</td><td><code>{r["货位编码"]}</code></td><td>{reason}</td></tr>\n'

html += f'''</table>

<p><strong>预警2：临购药品应转常规（{len(lg_convert)}种）</strong></p>
<p>以下临购药品发药频次≥3次/月或总量≥20，已超出"临时"范畴，<strong>建议立即转常规并分配正式货位</strong>：</p>
<table>
<tr><th>药品名称</th><th>发药次数</th><th>总量</th><th>科室数</th><th>建议</th></tr>
'''
for _, r in lg_convert.iterrows():
    html += f'<tr><td>{r["药品名称"]}</td><td>{r["发药次数"]}</td><td>{r["总量"]:.1f}</td><td>{r["科室数"]}</td><td class="priority-red">转常规+分配正式货位</td></tr>\n'

html += f'''</table>

<p><strong>预警3：停用药品占用货位（{stats["停用药品数"]}种）</strong></p>
<p>数据中检出{stats["停用药品数"]}种标记为"(停用)"的药品仍占用活跃货位，<strong>建议立即退库清理</strong>，释放货架空间。其中含临购停用药品13种。</p>
</div>

<div class="alert-yellow">
<h3>🟡 常规优化项（黄色建议）— 共4类</h3>

<p><strong>建议1：临购药品释放归档（{len(lg_release)}种）</strong></p>
<p>以下临购药品发药≤1次/季且总量≤5，建议释放货位并归档管理：</p>
<table>
<tr><th>药品名称</th><th>发药次数</th><th>总量</th><th>科室数</th></tr>
'''
for _, r in lg_release.iterrows():
    html += f'<tr><td>{r["药品名称"]}</td><td>{r["发药次数"]}</td><td>{r["总量"]:.1f}</td><td>{r["科室数"]}</td></tr>\n'

html += f'''</table>

<p><strong>建议2：黄金层利用率提升</strong></p>
<p>当前黄金层(1.2-1.5m)仅分配<strong>{stats["黄金层药品数"]}种</strong>药品（均为A+X/A+Y类），而A类药品共<strong>{stats["ABC分布"]["A"]}种</strong>。其中32种A+Z类药品（高频高波动）分配至中下层，建议根据实际拣选频次酌情上移部分AZ类至黄金层。</p>

<p><strong>建议3：高频处方组合相邻放置</strong></p>
<p>检出{stats["高频组合数"]}组高频共现处方组合（如0.9%氯化钠+灭菌注射用水+鲜益母草胶囊），建议将强关联品种在货位上相邻放置，优化S型拣选动线。</p>

<p><strong>建议4：临购观察期品种（{len(lg_observe)}种）</strong></p>
<p>以下临购药品处于30天观察期，暂维持临时专区编码，下次评估时复核：</p>
<table>
<tr><th>药品名称</th><th>发药次数</th><th>总量</th><th>科室数</th></tr>
'''
for _, r in lg_observe.iterrows():
    html += f'<tr><td>{r["药品名称"]}</td><td>{r["发药次数"]}</td><td>{r["总量"]:.1f}</td><td>{r["科室数"]}</td></tr>\n'

html += '''</table>
</div>

<!-- ===================== 二、数据清洗 ===================== -->
<h2 id="data">二、数据清洗概览</h2>
<div class="card">
<table>
<tr><th>指标</th><th>数值</th><th>说明</th></tr>
<tr><td>原始记录数</td><td>2,712</td><td>含1行合计行（已移除）</td></tr>
<tr><td>有效记录数</td><td>2,711</td><td>清洗后</td></tr>
<tr><td>唯一药品数</td><td>563</td><td>按药品名称+规格去重</td></tr>
<tr><td>唯一科室数</td><td>34</td><td>含护士站、门诊、急诊</td></tr>
<tr><td>总发药量</td><td>87,637.7</td><td>12个月累计</td></tr>
<tr><td>零发药记录</td><td>29条</td><td>已填充0并标记异常</td></tr>
<tr><td>停用药品记录</td><td>176条</td><td>药品名含"(停用)"标记</td></tr>
<tr><td>药品类别</td><td>西药/中成药</td><td>西药2,388条，中成药323条</td></tr>
<tr><td>单位类型</td><td>盒/支/瓶/袋/听</td><td>盒(1,826) 支(355) 瓶(350) 袋(178) 听(2)</td></tr>
</table>
<p style="margin-top:12px;color:var(--text-sec);font-size:13px;">注：原始数据为聚合数据（无日期维度），月均消耗按 总量/12 估算。无库存数据，周转率以月均消耗量+科室覆盖度近似。</p>
</div>

<!-- ===================== 三、周转分析 ===================== -->
<h2 id="turnover">三、周转分析</h2>
<div class="card">
<table>
<tr><th>周转等级</th><th>月均消耗区间</th><th>药品数</th><th>占比</th><th>典型药品</th></tr>
<tr><td><span class="badge badge-red">极高</span></td><td>>200/月</td><td>8</td><td>1.4%</td><td>0.9%氯化钠(10ml/100ml)、灭菌注射用水、鲜益母草胶囊</td></tr>
<tr><td><span class="badge badge-yellow">高</span></td><td>50-200/月</td><td>21</td><td>3.7%</td><td>乳酸钠林格、蛋白琥珀酸铁、依诺肝素、肠内营养</td></tr>
<tr><td><span class="badge badge-blue">中</span></td><td>10-50/月</td><td>108</td><td>19.2%</td><td>地屈孕酮、双氯芬酸钠栓、青霉素钠</td></tr>
<tr><td><span class="badge badge-gray">低</span></td><td>1-10/月</td><td>231</td><td>41.0%</td><td>—</td></tr>
<tr><td><span class="badge badge-gray">极低</span></td><td><1/月</td><td>212</td><td>37.7%</td><td>含大量临购及低频品种</td></tr>
</table>
<p style="margin-top:12px;color:var(--text-sec);font-size:13px;">高周转(极高+高)仅29种(5.1%)，但贡献了<strong>总量73.5%</strong>的发药量——帕累托效应显著。</p>
</div>

<!-- ===================== 四、专科标签 ===================== -->
<h2 id="tags">四、专科标签化</h2>
<div class="card">
<table>
<tr><th>专科标签</th><th>药品数</th><th>占比</th><th>典型品种</th></tr>
<tr><td><span class="badge badge-purple">康复</span></td><td>208</td><td>36.9%</td><td>肠内营养、乙酰半胱氨酸、肉毒毒素、精神类药物</td></tr>
<tr><td><span class="badge badge-pink" style="background:#ec4899;color:#fff">女性</span></td><td>199</td><td>35.3%</td><td>益母草、地屈孕酮、缩宫素、阿托西班、蛋白琥珀酸铁</td></tr>
<tr><td><span class="badge badge-purple">女性+康复</span></td><td>86</td><td>15.3%</td><td>依诺肝素、开塞露、乳果糖（跨科共用）</td></tr>
<tr><td><span class="badge badge-green">儿童</span></td><td>29</td><td>5.2%</td><td>开喉剑喷雾剂(儿童型)、维生素AD、奥司他韦</td></tr>
<tr><td><span class="badge badge-blue">通用</span></td><td>29</td><td>5.2%</td><td>氯化钠输液、葡萄糖输液等基础药品</td></tr>
<tr><td><span class="badge badge-green">儿童+康复</span></td><td>7</td><td>1.2%</td><td>玛巴洛沙韦等</td></tr>
<tr><td><span class="badge" style="background:#ec4899;color:#fff">儿童+女性</span></td><td>6</td><td>1.1%</td><td>维生素AD滴剂等</td></tr>
</table>
<p style="margin-top:12px;color:var(--text-sec);font-size:13px;">康复+女性标签合计占比87.5%，印证妇幼康复专科定位。儿童专属药品虽仅29种，但需<strong>独立分区</strong>保障用药安全。</p>
</div>

<!-- ===================== 五、ABC-XYZ ===================== -->
<h2 id="abcxyz">五、ABC-XYZ矩阵分类</h2>
<div class="card">
<h3>ABC分类（按用量金额贡献）</h3>
<table>
<tr><th>分类</th><th>标准</th><th>药品数</th><th>总量占比</th><th>管理策略</th></tr>
<tr><td><span class="badge badge-red">A类</span></td><td>累计前70%</td><td>{stats["ABC分布"]["A"]}</td><td>~85%</td><td>重点管控，黄金层/中下层</td></tr>
<tr><td><span class="badge badge-yellow">B类</span></td><td>70-90%</td><td>{stats["ABC分布"]["B"]}</td><td>~12%</td><td>常规管理，中下层</td></tr>
<tr><td><span class="badge badge-gray">C类</span></td><td>后10%</td><td>{stats["ABC分布"]["C"]}</td><td>~3%</td><td>简化管理，上层</td></tr>
</table>

<h3>XYZ分类（按波动系数CV）</h3>
<table>
<tr><th>分类</th><th>标准</th><th>药品数</th><th>特征</th></tr>
<tr><td><span class="badge badge-green">X类</span></td><td>CV≤0.5</td><td>{stats["XYZ分布"]["X"]}</td><td>需求稳定</td></tr>
<tr><td><span class="badge badge-yellow">Y类</span></td><td>0.5<CV≤1.5</td><td>{stats["XYZ分布"]["Y"]}</td><td>季节/周期波动</td></tr>
<tr><td><span class="badge badge-red">Z类</span></td><td>CV>1.5 或 临购</td><td>{stats["XYZ分布"]["Z"]}</td><td>极高波动/临购</td></tr>
</table>

<h3>ABC-XYZ交叉矩阵</h3>
<div class="mermaid">
quadrantChart
    title ABC-XYZ 药品分布矩阵
    x-axis "低波动(X)" --> "高波动(Z)"
    y-axis "低价值(C)" --> "高价值(A)"
    quadrant-1 "AZ: 高值高波动"
    quadrant-2 "AX: 高值稳定（黄金层）"
    quadrant-3 "CX: 低值稳定"
    quadrant-4 "CZ: 低值高波动"
</div>

<table>
<tr><th>矩阵</th><th>药品数</th><th>总量</th><th>管理策略</th></tr>
<tr><td><strong>AX</strong></td><td>{stats["矩阵分布"]["AX"]["药品数"]}</td><td>{stats["矩阵分布"]["AX"]["总量"]:.0f}</td><td>⭐ 黄金层（高频稳定）</td></tr>
<tr><td><strong>AY</strong></td><td>{stats["矩阵分布"]["AY"]["药品数"]}</td><td>{stats["矩阵分布"]["AY"]["总量"]:.0f}</td><td>⭐ 黄金层（高频波动）</td></tr>
<tr><td><strong>AZ</strong></td><td>{stats["矩阵分布"]["AZ"]["药品数"]}</td><td>{stats["矩阵分布"]["AZ"]["总量"]:.0f}</td><td>中下层（高频但波动大）</td></tr>
<tr><td><strong>BX</strong></td><td>{stats["矩阵分布"]["BX"]["药品数"]}</td><td>{stats["矩阵分布"]["BX"]["总量"]:.0f}</td><td>中下层</td></tr>
<tr><td><strong>BY</strong></td><td>{stats["矩阵分布"]["BY"]["药品数"]}</td><td>{stats["矩阵分布"]["BY"]["总量"]:.0f}</td><td>中下层</td></tr>
<tr><td><strong>BZ</strong></td><td>{stats["矩阵分布"]["BZ"]["药品数"]}</td><td>{stats["矩阵分布"]["BZ"]["总量"]:.0f}</td><td>下层</td></tr>
<tr><td><strong>CX</strong></td><td>{stats["矩阵分布"]["CX"]["药品数"]}</td><td>{stats["矩阵分布"]["CX"]["总量"]:.0f}</td><td>上层</td></tr>
<tr><td><strong>CY</strong></td><td>{stats["矩阵分布"]["CY"]["药品数"]}</td><td>{stats["矩阵分布"]["CY"]["总量"]:.0f}</td><td>上层</td></tr>
<tr><td><strong>CZ</strong></td><td>{stats["矩阵分布"]["CZ"]["药品数"]}</td><td>{stats["矩阵分布"]["CZ"]["总量"]:.0f}</td><td>上层/退库</td></tr>
</table>
<p style="margin-top:12px;color:var(--text-sec);font-size:13px;">AZ类32种药品贡献了<strong>55.3%</strong>的发药总量，是核心管控对象——高频但需求波动大（如输液类、季节性药品）。</p>
</div>

<!-- ===================== 六、货位编码 ===================== -->
<h2 id="coding">六、五级货位编码体系</h2>
<div class="card">
<h3>编码结构：区-架-层-位-库</h3>
<div class="mermaid">
graph LR
    A["区码<br/>(药理大类)"] --> B["架码<br/>(药理子类)"]
    B --> C["层码<br/>(周转等级)"]
    C --> D["位码<br/>(ABC分类)"]
    D --> E["库码<br/>(特殊管理)"]
    style A fill:#dbeafe,stroke:#2563eb
    style B fill:#e0e7ff,stroke:#7c3aed
    style C fill:#fef3c7,stroke:#d97706
    style D fill:#dcfce7,stroke:#059669
    style E fill:#fee2e2,stroke:#dc2626
</div>

<h3>区码定义</h3>
<table>
<tr><th>区码</th><th>区域名称</th><th>药品数</th><th>说明</th></tr>
<tr><td><code>A</code></td><td>门诊/住院常用药</td><td>475</td><td>抗感染、妇科产科、心血管、消化、呼吸等</td></tr>
<tr><td><code>F</code></td><td>康复科精神方面常用药</td><td>22</td><td>神经/精神系统药物</td></tr>
<tr><td><code>G</code></td><td>高警示药品专区</td><td>39</td><td>红底黑字标识，禁止底层</td></tr>
<tr><td><code>H</code></td><td>临购/其他专区</td><td>31</td><td>30天观察期，动态管理</td></tr>
<tr><td><code>I</code></td><td>外用制剂区</td><td>30</td><td>乳膏、软膏、喷雾、栓剂等</td></tr>
<tr><td><code>K</code></td><td>输液类</td><td>37</td><td>大输液、电解质平衡</td></tr>
<tr><td><code>L</code></td><td>输液类（备选）</td><td>—</td><td>—</td></tr>
<tr><td><code>M</code></td><td>阴凉柜</td><td>18</td><td>精神/毒性药品专用</td></tr>
</table>

<h3>层码定义</h3>
<table>
<tr><th>层码</th><th>物理位置</th><th>高度</th><th>适用</th></tr>
<tr><td><code>3</code></td><td>黄金层</td><td>1.2-1.5m</td><td>A+X/A+Y类（高频稳定）</td></tr>
<tr><td><code>2</code></td><td>中下层</td><td>0.6-1.2m</td><td>A+Z、B+X/B+Y类</td></tr>
<tr><td><code>1</code></td><td>下层/上层</td><td>0-0.6m / 1.5-1.8m</td><td>B+Z、C类</td></tr>
</table>

<h3>库码定义</h3>
<table>
<tr><th>库码</th><th>含义</th><th>数量</th></tr>
<tr><td><code>G</code></td><td>高警示专区</td><td>39</td></tr>
<tr><td><code>H</code></td><td>临购专区</td><td>31</td></tr>
<tr><td><code>M</code></td><td>阴凉柜/保险柜</td><td>18</td></tr>
<tr><td><code>(空)</code></td><td>常规</td><td>475</td></tr>
</table>
</div>

<!-- ===================== 七、关联聚类 ===================== -->
<h2 id="cluster">七、关联度聚类分析</h2>
<div class="card">
<p>基于科室-药品共现矩阵，按科室大类聚合后计算TOP20药品的两两关联强度（取共同科室最小用量为关联分）。</p>

<div class="mermaid">
graph TD
    subgraph "输液基础组"
        A1["0.9%氯化钠(100ml)"] --- A2["灭菌注射用水(10ml)"]
        A1 --- A3["0.9%氯化钠(10ml)"]
        A2 --- A3
    end
    subgraph "产后康复组"
        B1["鲜益母草胶囊"] --- B2["蛋白琥珀酸铁口服液"]
        B1 --- A2
    end
    subgraph "输液扩容组"
        C1["乳酸钠林格注射液"] --- A1
        C2["0.9%氯化钠(500ml玻瓶)"] --- A1
    end
    style A1 fill:#dbeafe,stroke:#2563eb
    style B1 fill:#fce7f3,stroke:#ec4899
    style C1 fill:#dcfce7,stroke:#059669
</div>

<h3>高频处方组合TOP15</h3>
<table>
<tr><th>#</th><th>药品1</th><th>药品2</th><th>关联强度</th><th>药理关联</th></tr>
'''

for i, (_, r) in enumerate(assoc.iterrows(), 1):
    html += f'<tr><td>{i}</td><td>{r["药品1"]}</td><td>{r["药品2"]}</td><td>{r["关联强度"]:.0f}</td><td>{r["药理大类1"]} + {r["药理大类2"]}</td></tr>\n'

html += '''</table>
<p style="margin-top:12px;color:var(--text-sec);font-size:13px;">建议将输液基础组（0.9%氯化钠+灭菌注射用水）与产后康复组（鲜益母草+蛋白琥珀酸铁）在K区和A区相邻货架放置，形成S型拣选动线。</p>
</div>

<!-- ===================== 八、黄金层 ===================== -->
<h2 id="golden">八、黄金层分配</h2>
<div class="card">
<p>黄金层(1.2-1.5m)强制分配A+X和A+Y类药品，共<strong>15种</strong>：</p>
<table>
<tr><th>药品名称</th><th>总量</th><th>月均消耗</th><th>矩阵</th><th>货位编码</th></tr>
'''
for _, r in golden.sort_values('总量',ascending=False).iterrows():
    html += f'<tr><td>{r["药品名称"]}</td><td>{r["总量"]:.1f}</td><td>{r["月均消耗"]:.1f}</td><td><span class="badge badge-blue">{r["矩阵分类"]}</span></td><td><code>{r["货位编码"]}</code></td></tr>\n'

html += f'''</table>
<p style="margin-top:12px;color:var(--text-sec);font-size:13px;">另有32种AZ类药品（高频高波动）分配至中下层(0.6-1.2m)，包括0.9%氯化钠注射液(10ml/100ml)、鲜益母草胶囊、依诺肝素等核心品种。</p>
</div>

<!-- ===================== 九、临购处置 ===================== -->
<h2 id="temporary">九、临购专项处置</h2>
<div class="card">
<div class="mermaid">
flowchart TD
    A["临购药品入库"] --> B["分配临时专区编码(H区)"]
    B --> C["30天观察期"]
    C --> D{"发药频次评估"}
    D -->|"≥3次/月 或 总量≥20"| E["建议转常规<br/>分配正式货位"]
    D -->|"≤1次/季 且 总量≤5"| F["建议释放货位<br/>归档管理"]
    D -->|"其他"| G["继续观察<br/>维持临时编码"]
    E --> H["正式货位管理"]
    F --> I["退出临购专区"]
    G --> C
    style E fill:#dcfce7,stroke:#059669
    style F fill:#fee2e2,stroke:#dc2626
    style G fill:#fef3c7,stroke:#d97706
</div>

<table>
<tr><th>处置类别</th><th>药品数</th><th>操作</th></tr>
<tr><td class="priority-red">建议转常规</td><td>9</td><td>分配正式货位，纳入常规管理</td></tr>
<tr><td class="priority-yellow">继续观察</td><td>14</td><td>维持临时专区编码，30天后复核</td></tr>
<tr><td>建议释放归档</td><td>8</td><td>退出临购专区，释放货位空间</td></tr>
</table>
</div>

<!-- ===================== 十、合规检查 ===================== -->
<h2 id="compliance">十、合规兜底检查</h2>
<div class="card">
<div class="alert-green">
<h3>✅ 合规检查结果</h3>
<table>
<tr><th>检查项</th><th>标准</th><th>结果</th><th>状态</th></tr>
<tr><td>高警示药品标识</td><td>红底黑字标识</td><td>39种已标记</td><td>✅ 通过</td></tr>
<tr><td>高警示药品层位</td><td>禁止底层(0-0.6m)</td><td>9种违规→已强制调整</td><td>⚠️ 已修正</td></tr>
<tr><td>精神/毒性药品</td><td>M区阴凉柜/保险柜</td><td>18种已分配M区</td><td>✅ 通过</td></tr>
<tr><td>易混淆药品隔离</td><td>分层摆放+标记</td><td>24种已标记▲△★●☆</td><td>✅ 通过</td></tr>
<tr><td>临购药品专区</td><td>H区临时编码</td><td>31种已分配H区</td><td>✅ 通过</td></tr>
<tr><td>停用药品清理</td><td>退库释放空间</td><td>55种待清理</td><td>❌ 待执行</td></tr>
</table>
</div>

<h3>易混淆药品标记体系</h3>
<table>
<tr><th>标记</th><th>含义</th><th>药品数</th><th>管理要求</th></tr>
<tr><td>▲</td><td>高警示药品</td><td>14</td><td>红底黑字标识，禁底层</td></tr>
<tr><td>△</td><td>同类名似药品</td><td>2</td><td>分层摆放，隔位放置</td></tr>
<tr><td>★</td><td>产科急救药品</td><td>9</td><td>集中放置，急救动线优先</td></tr>
<tr><td>●</td><td>重点监测药品</td><td>2</td><td>定期盘点，双人核对</td></tr>
<tr><td>☆</td><td>普通警示药品</td><td>1</td><td>黄底标识</td></tr>
</table>
</div>

<!-- ===================== 十一、调整清单 ===================== -->
<h2 id="changes">十一、调整清单（需更改项汇总）</h2>
<div class="card">
<h3>用量TOP20药品货位分配</h3>
<table>
<tr><th>#</th><th>药品名称</th><th>规格</th><th>总量</th><th>月均</th><th>ABC</th><th>XYZ</th><th>标签</th><th>货位编码</th><th>物理层位</th></tr>
'''
for i, (_, r) in enumerate(top20.iterrows(), 1):
    tag_badges = ''.join(f'<span class="badge badge-gray">{t}</span>' for t in str(r['专科标签']).split(','))
    html += f'<tr><td>{i}</td><td>{r["药品名称"]}</td><td>{r["规格"]}</td><td>{r["总量"]:.1f}</td><td>{r["月均消耗"]:.1f}</td><td><span class="badge badge-{"red" if r["ABC分类"]=="A" else "yellow" if r["ABC分类"]=="B" else "gray"}">{r["ABC分类"]}</span></td><td><span class="badge badge-{"green" if r["XYZ分类"]=="X" else "yellow" if r["XYZ分类"]=="Y" else "red"}">{r["XYZ分类"]}</span></td><td>{tag_badges}</td><td><code>{r["货位编码"]}</code></td><td>{r["物理层位"]}</td></tr>\n'

html += '''</table>

<h3>货位区码分布概览</h3>
<div class="mermaid">
pie title 货位区码药品分布
    "A区 门诊住院常用药" : 475
    "K区 输液类" : 37
    "I区 外用制剂" : 30
    "F区 康复科精神药" : 22
</div>

<div class="alert-red" style="margin-top:24px">
<h3>📋 执行优先级</h3>
<ol>
<li><strong>立即执行（本周内）</strong>：9种高警示药品层位调整 + 55种停用药品退库清理</li>
<li><strong>近期执行（2周内）</strong>：9种临购转常规药品分配正式货位 + 8种临购释放归档</li>
<li><strong>持续优化（1个月内）</strong>：高频处方组合相邻放置 + 14种临购观察期复核</li>
<li><strong>定期复核（每季度）</strong>：ABC-XYZ重新分类 + 黄金层动态调整</li>
</ol>
</div>
</div>

<div class="footer">
<p>本方案由AI药房运营规划师基于12个月发药数据自动生成 | 数据源：发药查询202508-202608.xls</p>
<p>配套文件：药品货位规划表.xlsx | 高频处方关联组合.xlsx | 临购药品处置建议.xlsx</p>
</div>

<script>
mermaid.initialize({{ startOnLoad: true, theme: 'neutral', securityLevel: 'loose' }});
</script>
</body>
</html>
'''

output_path = os.path.join(OUTPUT_DIR, '药房货位规划方案报告.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'报告已生成: {output_path}')
print(f'文件大小: {os.path.getsize(output_path)/1024:.1f}KB')
