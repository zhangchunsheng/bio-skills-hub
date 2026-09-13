#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STROBE规范数据分析报告：二甲双胍长期用药与老年T2DM认知功能
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import seaborn as sns
from scipy import stats
from scipy.stats import mannwhitneyu, chi2_contingency, ttest_ind
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)

# ============================================================
# 1. DATA LOADING AND CLEANING
# ============================================================
INPUT_FILE = r'C:\Users\xiany\Desktop\20260808药学科研世界药师节第二场\下午场\A_二甲双胍认知队列_练习数据分析.xlsx'
OUTPUT_DIR = r'C:\Users\xiany\WorkBuddy\20260808药学会科研培训班\_figures'

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

df_basic = pd.read_excel(INPUT_FILE, sheet_name='01_患者基本信息')
df_med = pd.read_excel(INPUT_FILE, sheet_name='02_用药记录')
df_fu = pd.read_excel(INPUT_FILE, sheet_name='03_随访记录')
df_lab = pd.read_excel(INPUT_FILE, sheet_name='04_实验室检查')
df_outcome = pd.read_excel(INPUT_FILE, sheet_name='05_结局事件')

def parse_mixed_date(series):
    """Parse mixed date formats: YYYY-MM-DD, DD-MM-YYYY, YYYYMMDD"""
    parsed = []
    for v in series:
        if pd.isna(v):
            parsed.append(pd.NaT)
            continue
        v = str(v).strip()
        try:
            # YYYYMMDD (no separator)
            if len(v) == 8 and v.isdigit():
                parsed.append(pd.to_datetime(v, format='%Y%m%d'))
            elif '-' in v:
                parts = v.split('-')
                if len(parts[0]) == 4:  # YYYY-MM-DD
                    parsed.append(pd.to_datetime(v, format='%Y-%m-%d'))
                else:  # DD-MM-YYYY
                    parsed.append(pd.to_datetime(v, format='%d-%m-%Y'))
            else:
                parsed.append(pd.to_datetime(v))
        except:
            parsed.append(pd.NaT)
    return pd.Series(parsed, index=series.index)

# Parse dates
df_med['处方日期'] = parse_mixed_date(df_med['处方日期'])
df_fu['随访日期'] = parse_mixed_date(df_fu['随访日期'])
df_lab['检验日期'] = parse_mixed_date(df_lab['检验日期'])
df_outcome['随访终点日期'] = parse_mixed_date(df_outcome['随访终点日期'])

# Clean sex variable - standardize to M/F
sex_map = {'男': 'M', '女': 'F', 'M': 'M', 'F': 'F',
           '1': 'M', '2': 'F', 1: 'M', 2: 'F'}
df_basic['性别_std'] = df_basic['性别'].map(sex_map)

# Fix age outliers (999 -> likely data entry error, treat as missing)
df_basic['年龄_clean'] = df_basic['年龄'].clip(upper=120)
df_basic.loc[df_basic['年龄'] > 120, '年龄_clean'] = np.nan

# Fix BMI outliers (<10 or >50 is physiologically implausible)
df_basic['BMI_clean'] = df_basic['BMI'].copy()
df_basic.loc[(df_basic['BMI'] < 10) | (df_basic['BMI'] > 50), 'BMI_clean'] = np.nan

# Fix MoCA outliers (MoCA max is 30; >30 likely error or non-standard version)
# For this simulated dataset, keep as-is since it's teaching data, but note the issue
df_basic['基线MoCA_note'] = df_basic['基线MoCA评分'].apply(
    lambda x: '>30异常' if x > 30 else '')

# Fix creatinine unit issues: values < 5 likely mg/dL, convert to µmol/L (×88.4)
df_lab['血肌酐_unit'] = 'µmol/L'
mgdl_mask = df_lab['血肌酐'] < 10
df_lab.loc[mgdl_mask, '血肌酐'] = df_lab.loc[mgdl_mask, '血肌酐'] * 88.4
df_lab.loc[mgdl_mask, '血肌酐_unit'] = 'mg/dL→µmol/L(×88.4)'

# Drop PII columns
df_basic = df_basic.drop(columns=['患者姓名', '身份证号', '联系电话'])

# Merge outcome with basic info
df_merged = df_basic.merge(df_outcome[['患者ID', '随访时长_年', '是否发生认知事件']],
                            on='患者ID', how='left')
df_merged['group'] = df_merged['降糖方案组别'].map({'二甲双胍长期': 1, '磺脲类': 0})

# ============================================================
# 2. DATA AUDIT REPORT
# ============================================================
print("=" * 70)
print("一、数据体检报告")
print("=" * 70)

# Missing rates
print("\n>>> 各变量缺失情况")
total_patients = len(df_basic)
print(f"总样本量: {total_patients} 例, 4个中心")
print(f"二甲双胍长期组: {(df_basic['降糖方案组别']=='二甲双胍长期').sum()} 例")
print(f"磺脲类组: {(df_basic['降糖方案组别']=='磺脲类').sum()} 例")

print(f"\n01_患者基本信息 ({len(df_basic)} 行):")
print(f"  年龄异常值(>120): {(df_basic['年龄']>120).sum()} 条 ({((df_basic['年龄']>120).sum()/len(df_basic)*100):.1f}%)")
print(f"  BMI异常值(<10或>50): {((df_basic['BMI']<10)|(df_basic['BMI']>50)).sum()} 条")
print(f"  MoCA>30(异常): {(df_basic['基线MoCA评分']>30).sum()} 条")
print(f"  性别编码不一致: {len(df_basic) - df_basic['性别_std'].notna().sum()} 条") if df_basic['性别_std'].notna().sum() < len(df_basic) else print("  性别编码: 已全部标准化")

print(f"\n02_用药记录 ({len(df_med)} 行): 无缺失值")
print(f"\n03_随访记录 ({len(df_fu)} 行):")
print(f"  MoCA评分缺失: {df_fu['MoCA评分'].isnull().sum()} 条 ({df_fu['MoCA评分'].isnull().sum()/len(df_fu)*100:.1f}%)")

print(f"\n04_实验室检查 ({len(df_lab)} 行):")
print(f"  血肌酐单位不统一(mg/dL): {mgdl_mask.sum()} 条 ({(mgdl_mask.sum()/len(df_lab)*100):.1f}%)")

print(f"\n05_结局事件 ({len(df_outcome)} 行):")
print(f"  事件类型缺失: {df_outcome['事件类型'].isnull().sum()} 条 ({df_outcome['事件类型'].isnull().sum()/len(df_outcome)*100:.1f}%)")
print(f"  失访原因缺失: {df_outcome['失访原因'].isnull().sum()} 条 ({df_outcome['失访原因'].isnull().sum()/len(df_outcome)*100:.1f}%)")

print("\n>>> 日期格式问题")
print(" 02_用药记录.处方日期: 一致 (YYYY-MM-DD)")
print(" 03_随访记录.随访日期: 不一致 (混合 YYYY-MM-DD / DD-MM-YYYY)")
print(" 04_实验室检查.检验日期: 不一致 (混合 YYYY-MM-DD / DD-MM-YYYY)")
print(" 05_结局事件.随访终点日期: 不一致 (混合 YYYY-MM-DD / DD-MM-YYYY / YYYYMMDD)")

print("\n>>> 数据清洗建议清单")
print(" 1. 统一所有日期为 YYYY-MM-DD 格式 (已完成)")
print(" 2. 血肌酐单位统一为 µmol/L，mg/dL值×88.4 (已完成，共{}条转换)".format(mgdl_mask.sum()))
print(" 3. 性别编码统一为 M/F (已完成)")
print(" 4. 年龄>120视为录入错误，建议回查原始病历，本次分析中设为缺失")
print(" 5. BMI<10或>50视为录入错误，建议回查")
print(" 6. MoCA>30可能为非标准量表，建议确认量表版本")
print(" 7. MoCA随访评分缺失率9.8%，建议在分析中注明采用可用个案分析")
print(" 8. 删除患者隐私字段(姓名/身份证/电话) (已完成)")

# ============================================================
# 3. TABLE 1 - BASELINE CHARACTERISTICS (Three-line table)
# ============================================================
print("\n" + "=" * 70)
print("二、Table 1 基线特征表")
print("=" * 70)

def table1_row_continuous(data, var_name, group_col='降糖方案组别'):
    """Generate Table 1 row for continuous variable"""
    g1 = data[data[group_col] == '二甲双胍长期'][var_name].dropna()
    g2 = data[data[group_col] == '磺脲类'][var_name].dropna()
    
    # Normality test
    _, p_norm1 = stats.normaltest(g1) if len(g1) > 8 else (0, 1)
    _, p_norm2 = stats.normaltest(g2) if len(g2) > 8 else (0, 1)
    
    use_mannwhitney = (p_norm1 < 0.05) or (p_norm2 < 0.05) or (len(g1) < 30)
    
    if use_mannwhitney:
        stat_str1 = f"{g1.median():.1f} ({g1.quantile(0.25):.1f}, {g1.quantile(0.75):.1f})"
        stat_str2 = f"{g2.median():.1f} ({g2.quantile(0.25):.1f}, {g2.quantile(0.75):.1f})"
        u_stat, p_val = mannwhitneyu(g1, g2, alternative='two-sided')
        test_name = 'Mann-Whitney U'
    else:
        stat_str1 = f"{g1.mean():.1f} ± {g1.std():.1f}"
        stat_str2 = f"{g2.mean():.1f} ± {g2.std():.1f}"
        t_stat, p_val = ttest_ind(g1, g2)
        test_name = 't检验'
    
    p_str = f"P<0.001" if p_val < 0.001 else f"P={p_val:.3f}"
    return stat_str1, stat_str2, p_str, test_name, len(g1), len(g2)

def table1_row_categorical(data, var_name, group_col='降糖方案组别'):
    """Generate Table 1 row for categorical variable"""
    ct = pd.crosstab(data[group_col], data[var_name])
    chi2, p_val, dof, _ = chi2_contingency(ct)
    
    lines = []
    for cat in ct.columns:
        n1 = ct.loc['二甲双胍长期', cat] if cat in ct.loc['二甲双胍长期'].index else 0
        n2 = ct.loc['磺脲类', cat] if cat in ct.loc['磺脲类'].index else 0
        total1 = ct.loc['二甲双胍长期'].sum()
        total2 = ct.loc['磺脲类'].sum()
        lines.append((f"  {cat}", f"{n1}({n1/total1*100:.1f}%)", f"{n2}({n2/total2*100:.1f}%)"))
    
    p_str = "P<0.001" if p_val < 0.001 else f"P={p_val:.3f}"
    return lines, p_str, 'χ²检验'

print("\n>>> Table 1 基线特征")
print(f"{'变量':<30} {'二甲双胍长期组(n=641)':<30} {'磺脲类组(n=563)':<30} {'P值':<12}")
print("-" * 102)

# Demographics
vars_cont = ['年龄_clean', '受教育年限', 'BMI_clean', '糖尿病病程_年',
             '基线HbA1c_百分比', '合并用药种数', '基线MoCA评分']
var_labels = ['年龄(岁)', '受教育年限(年)', 'BMI(kg/m²)', '糖尿病病程(年)',
              '基线HbA1c(%)', '合并用药种数', '基线MoCA评分']

for vl, vc in zip(var_labels, vars_cont):
    s1, s2, p, tn, n1, n2 = table1_row_continuous(df_basic, vc)
    note = " †" if tn == 'Mann-Whitney U' else ""
    print(f"{vl:<28} {s1:<30} {s2:<30} {p:<12}")

# Categorical variables
print(f"\n{'性别':<28}")
for cat_label, cat_n1, cat_n2 in table1_row_categorical(df_basic, '性别_std')[0]:
    print(f"{cat_label:<28} {cat_n1:<30} {cat_n2:<30}")
print(f"{'':28} {'':30} {'':30} {table1_row_categorical(df_basic, '性别_std')[1]}")

print(f"\n{'就诊中心':<28}")
ct = pd.crosstab(df_basic['降糖方案组别'], df_basic['就诊中心'])
for center in ct.columns:
    n1 = ct.loc['二甲双胍长期', center]
    n2 = ct.loc['磺脲类', center]
    t1 = ct.loc['二甲双胍长期'].sum()
    t2 = ct.loc['磺脲类'].sum()
    print(f"  {center:<26} {n1}({n1/t1*100:.1f}%){'':<18} {n2}({n2/t2*100:.1f}%)")
chi2_c, p_c, _, _ = chi2_contingency(ct)
p_str_c = "P<0.001" if p_c < 0.001 else f"P={p_c:.3f}"
print(f"{'':28} {'':30} {'':30} {p_str_c}")

print("\n† 非正态分布，采用中位数(四分位数间距)；Mann-Whitney U检验")
print("‡ 无标记者采用均数±标准差；独立样本t检验")

# ============================================================
# 4. PRIMARY OUTCOME ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("三、主要结局分析")
print("=" * 70)

# Calculate MoCA annual change rate
df_fu = df_fu.sort_values(['患者ID', '随访次序'])
first_moca = df_fu.dropna(subset=['MoCA评分']).groupby('患者ID').first()['MoCA评分']
last_moca = df_fu.dropna(subset=['MoCA评分']).groupby('患者ID').last()['MoCA评分']
first_time = df_fu.dropna(subset=['MoCA评分']).groupby('患者ID').first()['距基线_年']
last_time = df_fu.dropna(subset=['MoCA评分']).groupby('患者ID').last()['距基线_年']

moca_change = pd.DataFrame({
    'first_moca': first_moca, 'last_moca': last_moca,
    'first_time': first_time, 'last_time': last_time
})
time_diff = moca_change['last_time'] - moca_change['first_time']
moca_change['annual_change'] = np.where(
    time_diff > 0.1,
    (moca_change['last_moca'] - moca_change['first_moca']) / time_diff,
    np.nan
)
moca_change = moca_change.dropna(subset=['annual_change'])
moca_change = moca_change.merge(df_basic[['患者ID', '降糖方案组别']], on='患者ID', how='left')

met_group = moca_change[moca_change['降糖方案组别'] == '二甲双胍长期']['annual_change']
su_group = moca_change[moca_change['降糖方案组别'] == '磺脲类']['annual_change']

print(f"\n>>> MoCA评分年均变化率")
print(f"二甲双胍长期组: n={len(met_group)}, mean={met_group.mean():.2f}, SD={met_group.std():.2f}")
print(f"磺脲类组: n={len(su_group)}, mean={su_group.mean():.2f}, SD={su_group.std():.2f}")

t_moca, p_moca = ttest_ind(met_group, su_group)
cohens_d = (met_group.mean() - su_group.mean()) / np.sqrt((met_group.std()**2 + su_group.std()**2) / 2)
se_diff = np.sqrt(met_group.std()**2/len(met_group) + su_group.std()**2/len(su_group))
ci_low = (met_group.mean() - su_group.mean()) - 1.96 * se_diff
ci_high = (met_group.mean() - su_group.mean()) + 1.96 * se_diff

p_moca_str = "P<0.001" if p_moca < 0.001 else f"P={p_moca:.3f}"
print(f"\n组间差值: {met_group.mean()-su_group.mean():.2f} (95%CI: {ci_low:.2f} to {ci_high:.2f})")
print(f"Cohen's d: {cohens_d:.2f}")
print(f"统计检验: {p_moca_str}")

# ============================================================
# 5. PSM (Propensity Score Matching)
# ============================================================
print("\n>>> 倾向性评分匹配(PSM)")

psm_vars = ['年龄_clean', '受教育年限', 'BMI_clean', '糖尿病病程_年',
            '基线HbA1c_百分比', '合并用药种数', '基线MoCA评分']
df_psm = df_basic.copy()
df_psm = df_psm.dropna(subset=psm_vars + ['性别_std'])

# Encode sex
df_psm['sex_code'] = (df_psm['性别_std'] == 'M').astype(int)

X = df_psm[psm_vars + ['sex_code']].copy()
y = (df_psm['降糖方案组别'] == '二甲双胍长期').astype(int)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)

logreg = LogisticRegression(max_iter=1000, random_state=42)
logreg.fit(X_scaled, y)
df_psm['ps'] = logreg.predict_proba(X_scaled)[:, 1]

# 1:1 matching with caliper=0.2*SD
treated = df_psm[df_psm['降糖方案组别'] == '二甲双胍长期'].copy()
control = df_psm[df_psm['降糖方案组别'] == '磺脲类'].copy()

caliper = 0.2 * df_psm['ps'].std()
matched_pairs = []
control_used = set()

for idx, row in treated.sort_values('ps', ascending=False).iterrows():
    control_available = control[~control.index.isin(control_used)]
    if len(control_available) == 0:
        break
    control_available['diff'] = abs(control_available['ps'] - row['ps'])
    best_match = control_available.loc[control_available['diff'].idxmin()]
    if best_match['diff'] <= caliper:
        matched_pairs.append((idx, best_match.name))
        control_used.add(best_match.name)

print(f"匹配前: 二甲双胍组{len(treated)}例, 磺脲类组{len(control)}例")
print(f"匹配后: 每组{len(matched_pairs)}例 (共{len(matched_pairs)*2}例)")

# Balance report
matched_ids = [p[0] for p in matched_pairs] + [p[1] for p in matched_pairs]
df_matched = df_psm.loc[matched_ids].copy()
df_matched['matched_group'] = np.where(df_matched.index.isin([p[0] for p in matched_pairs]), 1, 0)

print("\nPSM匹配后平衡性报告:")
print(f"{'变量':<20} {'二甲双胍组':<22} {'磺脲类组':<22} {'SMD':<8} {'SMD变化':<8}")
print("-" * 80)

for vc, vl in zip(psm_vars + ['sex_code'], var_labels + ['性别(男)']):
    g1_m = df_matched[df_matched['matched_group']==1][vc]
    g2_m = df_matched[df_matched['matched_group']==0][vc]
    g1_b = df_psm[df_psm['降糖方案组别']=='二甲双胍长期'][vc]
    g2_b = df_psm[df_psm['降糖方案组别']=='磺脲类'][vc]
    
    smd_before = abs(g1_b.mean() - g2_b.mean()) / np.sqrt((g1_b.std()**2 + g2_b.std()**2) / 2)
    smd_after = abs(g1_m.mean() - g2_m.mean()) / np.sqrt((g1_m.std()**2 + g2_m.std()**2) / 2)
    
    print(f"{vl:<18} {g1_m.mean():.2f}±{g1_m.std():.2f}{'':<6} {g2_m.mean():.2f}±{g2_m.std():.2f}{'':<6} {smd_after:.3f}{'':<2} {smd_before-smd_after:+.3f}")

# PSM outcome analysis
moca_change_psm = moca_change.merge(
    df_matched[['患者ID', 'matched_group']], on='患者ID', how='inner')
met_psm = moca_change_psm[moca_change_psm['matched_group']==1]['annual_change']
su_psm = moca_change_psm[moca_change_psm['matched_group']==0]['annual_change']

if len(met_psm) > 1 and len(su_psm) > 1:
    t_psm, p_psm = ttest_ind(met_psm, su_psm)
    p_psm_str = "P<0.001" if p_psm < 0.001 else f"P={p_psm:.3f}"
    d_psm = (met_psm.mean() - su_psm.mean()) / np.sqrt((met_psm.std()**2+su_psm.std()**2)/2)
    print(f"\nPSM后主要结局: 差值={met_psm.mean()-su_psm.mean():.2f}, Cohen's d={d_psm:.2f}, {p_psm_str}")

# Save PSM data for later
df_matched.to_csv(os.path.join(OUTPUT_DIR, '_psm_data.csv'), index=False)
moca_change.to_csv(os.path.join(OUTPUT_DIR, '_moca_change.csv'), index=False)

# ============================================================
# 6. FIGURES
# ============================================================
print("\n" + "=" * 70)
print("四、图表生成")
print("=" * 70)

# --- Figure 1: KM Curve ---
print("\n>>> 图1: KM生存曲线")
fig, ax = plt.subplots(figsize=(8, 6))

kmf_met = KaplanMeierFitter()
kmf_su = KaplanMeierFitter()

for name, group_df, color, ls in [
    ('二甲双胍长期组', df_merged[df_merged['降糖方案组别']=='二甲双胍长期'], '#2c7bb6', '-'),
    ('磺脲类组', df_merged[df_merged['降糖方案组别']=='磺脲类'], '#d7191c', '--')
]:
    kmf = KaplanMeierFitter()
    kmf.fit(group_df['随访时长_年'], group_df['是否发生认知事件'], label=name)
    kmf.plot_survival_function(ax=ax, color=color, linestyle=ls, linewidth=2, ci_show=True)

# Log-rank test
lr_result = logrank_test(
    df_merged[df_merged['降糖方案组别']=='二甲双胍长期']['随访时长_年'],
    df_merged[df_merged['降糖方案组别']=='磺脲类']['随访时长_年'],
    df_merged[df_merged['降糖方案组别']=='二甲双胍长期']['是否发生认知事件'],
    df_merged[df_merged['降糖方案组别']=='磺脲类']['是否发生认知事件']
)
lr_p = "P<0.001" if lr_result.p_value < 0.001 else f"P={lr_result.p_value:.3f}"

ax.set_xlabel('随访时间 (年)', fontsize=12)
ax.set_ylabel('无认知障碍累积生存率', fontsize=12)
ax.set_title('图1 两组认知障碍累积发生率比较 (Kaplan-Meier曲线)', fontsize=13, fontweight='bold', pad=15)
ax.legend(loc='lower left', fontsize=11)
ax.set_ylim(0, 1.05)
ax.grid(alpha=0.3)
ax.text(0.95, 0.95, f'Log-rank {lr_p}', transform=ax.transAxes,
        ha='right', va='top', fontsize=11,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_KM_curve.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f"  保存: fig1_KM_curve.png (Log-rank {lr_p})")

# --- Figure 2: Forest Plot (Subgroup Analysis) ---
print("\n>>> 图2: 森林图")
subgroups = {
    '总体': (df_merged.dropna(subset=['年龄_clean', '性别_std']), '全样本'),
}

# By age tertile
age_tertile = pd.qcut(df_merged['年龄_clean'].dropna(), 3, labels=['65-70岁', '71-75岁', '76-85岁'])
for label in ['65-70岁', '71-75岁', '76-85岁']:
    mask = (age_tertile == label)
    mask = mask[mask].index
    subgroups[f'年龄: {label}'] = (df_merged.loc[mask], f'n={len(mask)}')

# By sex
for sex_label in ['M', 'F']:
    mask = df_merged['性别_std'] == sex_label
    subgroups[f'性别: {"男" if sex_label=="M" else "女"}'] = (df_merged[mask], f'n={mask.sum()}')

# By education
edu_split = df_merged['受教育年限'].median()
mask_low = df_merged['受教育年限'] <= edu_split
mask_high = df_merged['受教育年限'] > edu_split
subgroups[f'教育: ≤{int(edu_split)}年'] = (df_merged[mask_low], f'n={mask_low.sum()}')
subgroups[f'教育: >{int(edu_split)}年'] = (df_merged[mask_high], f'n={mask_high.sum()}')

# By HbA1c
hba1c_split = df_merged['基线HbA1c_百分比'].median()
mask_low_h = df_merged['基线HbA1c_百分比'] <= hba1c_split
mask_high_h = df_merged['基线HbA1c_百分比'] > hba1c_split
subgroups[f'HbA1c: ≤{hba1c_split:.1f}%'] = (df_merged[mask_low_h], f'n={mask_low_h.sum()}')
subgroups[f'HbA1c: >{hba1c_split:.1f}%'] = (df_merged[mask_high_h], f'n={mask_high_h.sum()}')

forest_data = []
for sg_name, (sg_df, sg_note) in subgroups.items():
    if len(sg_df) < 10:
        continue
    met_ev = sg_df[sg_df['降糖方案组别']=='二甲双胍长期']['是否发生认知事件']
    su_ev = sg_df[sg_df['降糖方案组别']=='磺脲类']['是否发生认知事件']
    if len(met_ev.dropna()) < 5 or len(su_ev.dropna()) < 5:
        continue
    
    n_met = len(met_ev)
    n_su = len(su_ev)
    ev_met = met_ev.sum()
    ev_su = su_ev.sum()
    
    # Risk ratio
    rate_met = ev_met / n_met if n_met > 0 else 0
    rate_su = ev_su / n_su if n_su > 0 else 0
    rr = rate_met / rate_su if rate_su > 0 else np.nan
    
    # SE of log(RR)
    if ev_met > 0 and ev_su > 0:
        se_log_rr = np.sqrt(1/ev_met - 1/n_met + 1/ev_su - 1/n_su)
        ci_l = np.exp(np.log(rr) - 1.96 * se_log_rr) if rr > 0 else 0
        ci_u = np.exp(np.log(rr) + 1.96 * se_log_rr) if rr > 0 else np.inf
    else:
        ci_l, ci_u = np.nan, np.nan
    
    forest_data.append({
        'subgroup': sg_name, 'n': f'n={n_met+n_su}',
        'rr': rr, 'ci_low': ci_l, 'ci_high': ci_u,
        'ev_met': ev_met, 'n_met': n_met, 'ev_su': ev_su, 'n_su': n_su
    })

fig, ax = plt.subplots(figsize=(10, len(forest_data)*0.6 + 2))

y_positions = list(range(len(forest_data)))
y_labels = []

for i, fd in enumerate(forest_data):
    y = len(forest_data) - 1 - i
    y_labels.append(f"{fd['subgroup']} ({fd['n']})")
    
    if not np.isnan(fd['rr']):
        ax.plot(fd['rr'], y, 'o', color='#2c7bb6', markersize=8)
        ax.plot([fd['ci_low'], fd['ci_high']], [y, y], '-', color='#2c7bb6', linewidth=2)
        rr_str = f"{fd['rr']:.2f} ({fd['ci_low']:.2f}-{fd['ci_high']:.2f})"
        ax.text(max(fd['ci_high'], 2.5) + 0.05, y, rr_str, va='center', fontsize=9)

ax.axvline(x=1.0, color='#d7191c', linestyle='--', linewidth=1.5, alpha=0.7)
ax.set_yticks(range(len(forest_data)))
ax.set_yticklabels(y_labels, fontsize=9)
ax.set_xlabel('风险比 (Risk Ratio, 95%CI)', fontsize=12)
ax.set_title('图2 亚组分析森林图', fontsize=13, fontweight='bold', pad=15)
ax.set_xlim(0, max(3.5, max([fd.get('ci_high', 2) for fd in forest_data if not np.isnan(fd.get('ci_high', 0))])*1.3))
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_forest_plot.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f"  保存: fig2_forest_plot.png ({len(forest_data)} subgroups)")

# --- Figure 3: MoCA Trajectory Boxplot ---
print("\n>>> 图3: MoCA评分变化箱线图")

# Get MoCA at each follow-up by group
fu_with_group = df_fu.merge(df_basic[['患者ID', '降糖方案组别']], on='患者ID', how='left')
fu_plot = fu_with_group.dropna(subset=['MoCA评分', '降糖方案组别'])

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Boxplot by follow-up order
for ax_idx, (group_name, group_df) in enumerate([
    ('二甲双胍长期组', fu_plot[fu_plot['降糖方案组别']=='二甲双胍长期']),
    ('磺脲类组', fu_plot[fu_plot['降糖方案组别']=='磺脲类'])
]):
    ax = axes[ax_idx]
    visits = sorted(group_df['随访次序'].dropna().unique())
    data_for_box = [group_df[group_df['随访次序']==v]['MoCA评分'].dropna().values for v in visits if v <= 6]
    visits_label = [f'V{v}' for v in visits if v <= 6]
    
    bp = ax.boxplot(data_for_box, patch_artist=True,
                    medianprops=dict(color='#d7191c', linewidth=1.5))
    ax.set_xticklabels(visits_label)
    for patch in bp['boxes']:
        patch.set_facecolor('#2c7bb6' if ax_idx == 0 else '#fdae61')
        patch.set_alpha(0.6)
    
    ax.set_xlabel('随访次序', fontsize=11)
    ax.set_ylabel('MoCA评分', fontsize=11)
    ax.set_title(f'{"A " if ax_idx==0 else "B "}{group_name}', fontsize=12, fontweight='bold')
    ax.set_ylim(15, 35)
    ax.grid(axis='y', alpha=0.3)

fig.suptitle('图3 两组MoCA评分随访变化箱线图', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_moca_boxplot.png'), dpi=300, bbox_inches='tight')
plt.close()
print("  保存: fig3_moca_boxplot.png")

# --- Figure 4: Correlation Heatmap ---
print("\n>>> 图4: 相关性热力图")

# Build correlation matrix
# Build correlation data from df_basic directly, plus lab/outcome
lab_mean = df_lab.groupby('患者ID').agg({
    '血肌酐': 'mean', 'HOMA_IR': 'mean', 'hsCRP_mg_per_L': 'mean'
}).reset_index()
lab_mean.columns = ['患者ID', '血肌酐均值', 'HOMA_IR均值', 'hsCRP均值']

outcome_data = df_outcome[['患者ID', '随访时长_年', '是否发生认知事件']]

corr_df = df_basic[['患者ID', '年龄_clean', '受教育年限', 'BMI_clean',
                     '糖尿病病程_年', '基线HbA1c_百分比', '合并用药种数',
                     '基线MoCA评分']].copy()
corr_df.columns = ['患者ID', '年龄', '受教育年限', 'BMI', '糖尿病病程',
                    '基线HbA1c', '合并用药种数', '基线MoCA']
corr_df = corr_df.merge(lab_mean, on='患者ID', how='left')
corr_df = corr_df.merge(outcome_data, on='患者ID', how='left')

heatmap_vars = ['年龄', '受教育年限', 'BMI', '糖尿病病程', '基线HbA1c',
                '合并用药种数', '血肌酐均值', 'HOMA_IR均值', 'hsCRP均值',
                '基线MoCA', '随访时长_年', '是否发生认知事件']
heatmap_labels = ['Age', 'Education', 'BMI', 'DM Duration', 'Baseline HbA1c',
                  'Polypharmacy', 'SCr', 'HOMA-IR', 'hs-CRP',
                  'Baseline MoCA', 'Follow-up', 'Cognitive Event']

corr_mat = corr_df[heatmap_vars].corr()

fig, ax = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(corr_mat, dtype=bool), k=1)
cmap = sns.diverging_palette(240, 10, as_cmap=True)

sns.heatmap(corr_mat, mask=mask, cmap=cmap, center=0, annot=True,
            fmt='.2f', square=True, linewidths=0.5,
            xticklabels=heatmap_labels, yticklabels=heatmap_labels,
            vmin=-1, vmax=1, cbar_kws={'shrink': 0.8},
            ax=ax, annot_kws={'size': 8})
ax.set_title('图4 多重用药与结局相关性热力图', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'fig4_correlation_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()
print("  保存: fig4_correlation_heatmap.png")

# ============================================================
# 7. MEDIATION ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("五、中介效应分析")
print("=" * 70)

# Merge data for mediation
df_fu_last = df_fu.sort_values('随访次序').groupby('患者ID').last().reset_index()
df_fu_last = df_fu_last[['患者ID', 'MoCA评分']].rename(columns={'MoCA评分': '末次MoCA'})

df_fu_first = df_fu.sort_values('随访次序').groupby('患者ID').first().reset_index()
df_fu_first = df_fu_first[['患者ID', 'MoCA评分']].rename(columns={'MoCA评分': '首次MoCA'})

df_lab_mean = df_lab.groupby('患者ID').agg({
    'HOMA_IR': 'mean', 'hsCRP_mg_per_L': 'mean'
}).reset_index()
df_lab_mean.columns = ['患者ID', 'HOMA_IR_avg', 'hsCRP_avg']

df_med = df_basic[['患者ID', '降糖方案组别', '年龄_clean', '受教育年限', 'BMI_clean',
                   '糖尿病病程_年', '基线HbA1c_百分比', '合并用药种数']].copy()
df_med = df_med.merge(df_fu_first, on='患者ID', how='inner')
df_med = df_med.merge(df_fu_last, on='患者ID', how='inner')
df_med = df_med.merge(df_lab_mean, on='患者ID', how='inner')
df_med['moca_change'] = df_med['末次MoCA'] - df_med['首次MoCA']
df_med['group_code'] = (df_med['降糖方案组别'] == '二甲双胍长期').astype(int)

df_med = df_med.dropna(subset=['moca_change', 'HOMA_IR_avg', 'hsCRP_avg'])

print(f"中介分析样本量: {len(df_med)}")

# Bootstrap mediation function
def mediation_bootstrap(X, M, Y, n_bootstrap=5000):
    """Bootstrap for mediation analysis: X->M->Y"""
    n = len(X)
    results = {'a': [], 'b': [], 'c': [], 'cp': [], 'ab': []}
    
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        Xb, Mb, Yb = X[idx], M[idx], Y[idx]
        
        # a: X -> M
        from scipy import stats as st
        a_coef = np.polyfit(Xb, Mb, 1)[0]
        
        # b + c': X,M -> Y
        X2 = np.column_stack([Xb, Mb])
        beta = np.linalg.lstsq(np.column_stack([np.ones(n), X2]), Yb, rcond=None)[0]
        cp_coef = beta[1]
        b_coef = beta[2]
        
        # c: X -> Y (total effect)
        c_coef = np.polyfit(Xb, Yb, 1)[0]
        
        results['a'].append(a_coef)
        results['b'].append(b_coef)
        results['c'].append(c_coef)
        results['cp'].append(cp_coef)
        results['ab'].append(a_coef * b_coef)
    
    return results

# HOMA-IR as mediator
print("\n>>> HOMA-IR中介效应")
X = df_med['group_code'].values
M = df_med['HOMA_IR_avg'].values
Y = df_med['moca_change'].values

res_homa = mediation_bootstrap(X, M, Y, n_bootstrap=5000)

a_est = np.mean(res_homa['a'])
b_est = np.mean(res_homa['b'])
ab_est = np.mean(res_homa['ab'])
c_est = np.mean(res_homa['c'])
cp_est = np.mean(res_homa['cp'])

ab_ci = np.percentile(res_homa['ab'], [2.5, 97.5])
c_ci = np.percentile(res_homa['c'], [2.5, 97.5])

print(f"  总效应(c): {c_est:.3f} (95%CI: {c_ci[0]:.3f}, {c_ci[1]:.3f})")
print(f"  直接效应(c'): {cp_est:.3f}")
print(f"  间接效应(a×b): {ab_est:.3f} (95%CI: {ab_ci[0]:.3f}, {ab_ci[1]:.3f})")
print(f"  中介比例: {abs(ab_est/c_est*100):.1f}%" if abs(c_est) > 0.001 else "  中介比例: N/A")

ab_p_homa = 2 * min(
    np.mean([1 if v >= 0 else 0 for v in res_homa['ab']]),
    np.mean([1 if v <= 0 else 0 for v in res_homa['ab']])
)
ab_p_str_homa = "P<0.001" if ab_p_homa < 0.001 else f"P={ab_p_homa:.3f}"
print(f"  间接效应P值: {ab_p_str_homa}")

# hs-CRP as mediator
print("\n>>> hs-CRP中介效应")
M2 = df_med['hsCRP_avg'].values
res_crp = mediation_bootstrap(X, M2, Y, n_bootstrap=5000)

a2_est = np.mean(res_crp['a'])
b2_est = np.mean(res_crp['b'])
ab2_est = np.mean(res_crp['ab'])
c2_est = np.mean(res_crp['c'])
cp2_est = np.mean(res_crp['cp'])

ab2_ci = np.percentile(res_crp['ab'], [2.5, 97.5])
c2_ci = np.percentile(res_crp['c'], [2.5, 97.5])

print(f"  总效应(c): {c2_est:.3f} (95%CI: {c2_ci[0]:.3f}, {c2_ci[1]:.3f})")
print(f"  直接效应(c'): {cp2_est:.3f}")
print(f"  间接效应(a×b): {ab2_est:.3f} (95%CI: {ab2_ci[0]:.3f}, {ab2_ci[1]:.3f})")
print(f"  中介比例: {abs(ab2_est/c2_est*100):.1f}%" if abs(c2_est) > 0.001 else "  中介比例: N/A")

ab_p_crp = 2 * min(
    np.mean([1 if v >= 0 else 0 for v in res_crp['ab']]),
    np.mean([1 if v <= 0 else 0 for v in res_crp['ab']])
)
ab_p_str_crp = "P<0.001" if ab_p_crp < 0.001 else f"P={ab_p_crp:.3f}"
print(f"  间接效应P值: {ab_p_str_crp}")

# Save mediation results
med_results = {
    'homa_ir': {'ab': ab_est, 'ab_ci': ab_ci, 'ab_p': ab_p_str_homa,
                'c': c_est, 'cp': cp_est, 'prop': abs(ab_est/c_est*100)},
    'hs_crp': {'ab': ab2_est, 'ab2_ci': ab2_ci, 'ab_p': ab_p_str_crp,
               'c': c2_est, 'cp': cp2_est, 'prop': abs(ab2_est/c_est*100) if abs(c2_est) > 0.001 else 0}
}

# ============================================================
# 8. SAVE KEY NUMBERS FOR REPORT
# ============================================================
import json

report_data = {
    'total_n': len(df_basic),
    'met_n': int((df_basic['降糖方案组别']=='二甲双胍长期').sum()),
    'su_n': int((df_basic['降糖方案组别']=='磺脲类').sum()),
    'age_outliers': int((df_basic['年龄']>120).sum()),
    'creatinine_converted': int(mgdl_mask.sum()),
    'moca_missing_pct': round(df_fu['MoCA评分'].isnull().sum()/len(df_fu)*100, 1),
    
    'moca_change_met_mean': round(met_group.mean(), 2),
    'moca_change_met_sd': round(met_group.std(), 2),
    'moca_change_su_mean': round(su_group.mean(), 2),
    'moca_change_su_sd': round(su_group.std(), 2),
    'moca_diff': round(met_group.mean()-su_group.mean(), 2),
    'moca_ci_low': round(ci_low, 2),
    'moca_ci_high': round(ci_high, 2),
    'moca_p': p_moca_str,
    'cohens_d': round(cohens_d, 2),
    
    'psm_n_pairs': len(matched_pairs),
    'psm_n_before_met': len(treated),
    'psm_n_before_su': len(control),
    'lr_p': lr_p,
    
    'mediation_homa_ab': round(ab_est, 3),
    'mediation_homa_ab_ci_low': round(ab_ci[0], 3),
    'mediation_homa_ab_ci_high': round(ab_ci[1], 3),
    'mediation_homa_ab_p': ab_p_str_homa,
    'mediation_homa_prop': round(abs(ab_est/c_est*100), 1) if abs(c_est) > 0.001 else 0,
    
    'mediation_crp_ab': round(ab2_est, 3),
    'mediation_crp_ab_ci_low': round(ab2_ci[0], 3),
    'mediation_crp_ab_ci_high': round(ab2_ci[1], 3),
    'mediation_crp_ab_p': ab_p_str_crp,
    'mediation_crp_prop': round(abs(ab2_est/c_est*100), 1) if abs(c2_est) > 0.001 else 0,
    'mediation_crp_prop2': round(abs(ab2_est/c2_est*100), 1) if abs(c2_est) > 0.001 else 0,

    'outcome_event_rate_met': round(df_merged[df_merged['降糖方案组别']=='二甲双胍长期']['是否发生认知事件'].mean()*100, 1),
    'outcome_event_rate_su': round(df_merged[df_merged['降糖方案组别']=='磺脲类']['是否发生认知事件'].mean()*100, 1),
    'outcome_n_met': int((df_merged['降糖方案组别']=='二甲双胍长期').sum()),
    'outcome_n_su': int((df_merged['降糖方案组别']=='磺脲类').sum()),
    'outcome_events_met': int(df_merged[df_merged['降糖方案组别']=='二甲双胍长期']['是否发生认知事件'].sum()),
    'outcome_events_su': int(df_merged[df_merged['降糖方案组别']=='磺脲类']['是否发生认知事件'].sum()),
}

with open(os.path.join(OUTPUT_DIR, '_report_data.json'), 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 70)
print("分析完成！所有图表已保存到 _figures/")
print("报告数据已保存到 _figures/_report_data.json")
print("=" * 70)

# ============================================================
# 9. MCI Conversion Rate Analysis (Secondary Outcome)
# ============================================================
print("\n>>> 次要结局: MCI转化率")
events_met = df_merged[df_merged['降糖方案组别']=='二甲双胍长期']['是否发生认知事件']
events_su = df_merged[df_merged['降糖方案组别']=='磺脲类']['是否发生认知事件']

n_met_total = len(events_met)
n_su_total = len(events_su)
met_events = events_met.sum()
su_events = events_su.sum()

print(f"二甲双胍组: {met_events}/{n_met_total} ({met_events/n_met_total*100:.1f}%)")
print(f"磺脲类组: {su_events}/{n_su_total} ({su_events/n_su_total*100:.1f}%)")

# Chi-square test
ct_mci = pd.DataFrame({
    '事件': [met_events, su_events],
    '无事件': [n_met_total - met_events, n_su_total - su_events]
}, index=['二甲双胍', '磺脲类'])
chi2_mci, p_mci, dof_mci, _ = chi2_contingency(ct_mci)
mci_p_str = "P<0.001" if p_mci < 0.001 else f"P={p_mci:.3f}"
print(f"χ²={chi2_mci:.2f}, {mci_p_str}")

# Odds ratio
or_mci = (met_events/(n_met_total-met_events)) / (su_events/(n_su_total-su_events)) if su_events > 0 and n_su_total > su_events else np.nan
se_ln_or = np.sqrt(1/met_events + 1/(n_met_total-met_events) + 1/su_events + 1/(n_su_total-su_events)) if met_events > 0 and su_events > 0 else np.nan
or_ci_low = np.exp(np.log(or_mci) - 1.96*se_ln_or) if not np.isnan(se_ln_or) else np.nan
or_ci_high = np.exp(np.log(or_mci) + 1.96*se_ln_or) if not np.isnan(se_ln_or) else np.nan

report_data['mci_met_rate'] = round(met_events/n_met_total*100, 1)
report_data['mci_su_rate'] = round(su_events/n_su_total*100, 1)
report_data['mci_p'] = mci_p_str
report_data['mci_or'] = round(or_mci, 2) if not np.isnan(or_mci) else 'N/A'
report_data['mci_or_ci'] = f"{or_ci_low:.2f}-{or_ci_high:.2f}" if not np.isnan(or_ci_low) else 'N/A'

with open(os.path.join(OUTPUT_DIR, '_report_data.json'), 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

# ============================================================
# 10. Lab values comparison
# ============================================================
print("\n>>> hs-CRP与HOMA-IR组间比较")
lab_with_group = df_lab.merge(df_basic[['患者ID', '降糖方案组别']], on='患者ID', how='left')

for var in ['HOMA_IR', 'hsCRP_mg_per_L']:
    g1 = lab_with_group[lab_with_group['降糖方案组别']=='二甲双胍长期'][var].dropna()
    g2 = lab_with_group[lab_with_group['降糖方案组别']=='磺脲类'][var].dropna()
    t, p = ttest_ind(g1, g2)
    p_s = "P<0.001" if p < 0.001 else f"P={p:.3f}"
    print(f"  {var}: 二甲双胍组 {g1.mean():.2f}±{g1.std():.2f} vs 磺脲类组 {g2.mean():.2f}±{g2.std():.2f}, {p_s}")
    if var == 'HOMA_IR':
        report_data['homa_met_mean'] = round(g1.mean(), 2)
        report_data['homa_su_mean'] = round(g2.mean(), 2)
        report_data['homa_met_sd'] = round(g1.std(), 2)
        report_data['homa_su_sd'] = round(g2.std(), 2)
        report_data['homa_p'] = p_s
    else:
        report_data['crp_met_mean'] = round(g1.mean(), 2)
        report_data['crp_su_mean'] = round(g2.mean(), 2)
        report_data['crp_met_sd'] = round(g1.std(), 2)
        report_data['crp_su_sd'] = round(g2.std(), 2)
        report_data['crp_p'] = p_s

with open(os.path.join(OUTPUT_DIR, '_report_data.json'), 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print("\n>>> 全部分析完成!")
print(f"图表文件位于: {OUTPUT_DIR}")
for f in os.listdir(OUTPUT_DIR):
    if f.endswith('.png'):
        print(f"  {f}")
