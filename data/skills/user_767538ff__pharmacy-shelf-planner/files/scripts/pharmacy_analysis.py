# -*- coding: utf-8 -*-
"""
医院药房货位规划分析 - 10步流程
妇幼康复专科医院
"""
import pandas as pd
import numpy as np
import json
import re
from collections import defaultdict
from itertools import combinations

INPUT_FILE = r'C:/Users/acer/xwechat_files/wxid_8p6duufjw1fk22_6e60/msg/file/2026-08/发药查询202508-202608.xls'
OUTPUT_DIR = r'C:/Users/acer/WorkBuddy/2026-08-12-22-38-47/outputs'
PERIOD_MONTHS = 12  # 2025-08 ~ 2026-08 约12个月

# ============================================================
# 药理大类关键词映射（按优先级匹配）
# ============================================================
PHARMA_CATEGORY_RULES = [
    # (关键词列表, 药理大类代码, 药理大类名称, 货位区码)
    (['氯化钠注射液','葡萄糖注射液','葡萄糖氯化钠','乳酸钠林格','灭菌注射用水','复方氯化钠','林格液','浓氯化钠','5%葡萄糖','10%葡萄糖','0.9%氯化钠','甘露醇','果糖','转化糖'], 'L01', '大输液类', 'K'),
    (['头孢','青霉素','阿莫西林','克拉维酸','美罗培南','万古霉素','替加环素','阿米卡星','妥布霉素','两性霉素','奥马环素','头孢美唑','头孢呋辛','头孢哌酮','舒巴坦','头孢克肟','亚胺培南','哌拉西林','克林霉素','甲硝唑','替硝唑','奥硝唑','左氧氟沙星','莫西沙星','阿奇霉素','克拉霉素','红霉素','磺胺','呋喃妥因','磷霉素','多西环素','米诺环素','庆大霉素'], 'A01', '抗感染药', 'A'),
    (['缩宫素','阿托西班','利托君','硫酸镁','卡贝缩宫素','卡前列素','米非司酮','米索前列醇','益母草','地屈孕酮','黄体酮','戊酸雌二醇','雌二醇','炔雌醇','乙烯雌酚','促性腺激素','绒促性素','尿促性素','屈螺酮','去氧孕烯','依托孕烯','戈舍瑞林','亮丙瑞林','来曲唑','氯米芬','戊酸雌二醇'], 'A02', '妇科/产科专科药', 'A'),
    (['肝素','依诺肝素','华法林','利伐沙班','阿哌沙班','艾多沙班','达比加群','尿激酶','氨甲环酸','氨基己酸','酚磺乙胺','维生素K','凝血酶','低分子肝素'], 'A03', '抗凝/止血药', 'A'),
    (['蛋白琥珀酸铁','多糖铁','硫酸亚铁','琥珀酸亚铁','富马酸亚铁','维生素B12','叶酸','重组人促红素','重组人血小板生成素','甲钴胺','腺苷钴胺','蔗糖铁','维生素D','碳酸钙','葡萄糖酸钙','氨基酸','脂肪乳','肠内营养','肠外营养','复合维生素','维生素C','维生素B','维生素E','维生素A','多种微量元素'], 'A04', '营养/血液系统药', 'A'),
    (['阿托伐他汀','瑞舒伐他汀','辛伐他汀','普伐他汀','非诺贝特','苯扎贝特','依折麦布','英克司兰','普罗布考','硝苯地平','氨氯地平','非洛地平','美托洛尔','比索洛尔','阿替洛尔','培哚普利','依那普利','贝那普利','缬沙坦','氯沙坦','厄贝沙坦','替米沙坦','坎地沙坦','螺内酯','呋塞米','氢氯噻嗪','托拉塞米','单硝酸异山梨酯','硝酸甘油','地高辛','胺碘酮','普罗帕酮','酒石酸','美西律','多巴胺','多巴酚丁胺','去甲肾上腺素','去氧肾上腺素','肾上腺素','间羟胺','甲磺酸'], 'A05', '心血管系统药', 'A'),
    (['奥美拉唑','兰索拉唑','泮托拉唑','雷贝拉唑','艾司奥美拉唑','伏诺拉生','硫糖铝','铝碳酸镁','复方消化酶','多潘立酮','莫沙必利','伊托必利','甲氧氯普胺','开塞露','乳果糖','聚乙二醇','蒙脱石','双歧杆菌','枯草杆菌','复方谷氨酰胺','美沙拉嗪','匹维溴铵','雷尼替丁','法莫替丁','西咪替丁'], 'A06', '消化系统药', 'A'),
    (['右佐匹克隆','氯硝西泮','阿米替林','曲唑酮','氟西汀','舍曲林','艾司西酞普兰','文拉法辛','度洛西汀','丙戊酸','卡马西平','奥卡西平','左乙拉西坦','拉莫三嗪','苯妥英','苯巴比妥','多奈哌齐','美金刚','吡拉西坦','奥拉西坦','胞磷胆碱','尼莫地平','倍他司汀','氟桂利嗪','丁苯酞','银杏叶'], 'A07', '神经/精神系统药', 'F'),
    (['氨溴索','溴己新','羧甲司坦','乙酰半胱氨酸','氨茶碱','多索茶碱','茶碱','布地奈德','沙丁胺醇','特布他林','异丙托溴铵','噻托溴铵','福莫特罗','沙美特罗','孟鲁司特','酮替芬','氯雷他定','西替利嗪','依巴斯汀','奥司他韦','玛巴洛沙韦','扎那米韦','帕拉米韦','可待因','右美沙芬','喷托维林','妥洛特罗'], 'A08', '呼吸系统药', 'A'),
    (['双氯芬酸','对乙酰氨基酚','布洛芬','萘普生','吲哚美辛','赖氨匹林','塞来昔布','依托考昔','美洛昔康','洛索洛芬','氟比洛芬','帕瑞昔布','酮咯酸','曲马多','吗啡','芬太尼','羟考酮','可待因','氨酚羟考酮','奈福泮','丙泊酚','七氟烷','异氟烷','依托咪酯','氯胺酮','咪达唑仑','右美托咪定','利多卡因','罗哌卡因','布比卡因','丁卡因','普鲁卡因','舒芬太尼','瑞芬太尼'], 'A09', '镇痛/麻醉药', 'A'),
    (['人血白蛋白','免疫球蛋白','胸腺肽','胸腺法新','干扰素','聚乙二醇干扰素','转移因子','卡介菌','细菌溶解产物','匹多莫德','脾氨肽','乌苯美司','来那度胺','硼替佐米','利妥昔单抗','曲妥珠单抗','贝伐珠单抗','地舒单抗','英克司兰','肉毒毒素'], 'A10', '生物制品/免疫调节', 'A'),
    (['胰岛素','甘精胰岛素','门冬胰岛素','赖脯胰岛素','德谷胰岛素','格列美脲','格列齐特','格列吡嗪','二甲双胍','阿卡波糖','伏格列波糖','西格列汀','利格列汀','恩格列净','达格列净','吡格列酮','瑞格列奈','那格列奈'], 'A11', '内分泌/降糖药', 'A'),
    (['甲巯咪唑','丙硫氧嘧啶','左甲状腺素','甲状腺片','泼尼松','泼尼松龙','甲泼尼龙','地塞米松','倍他米松','氢化可的松','曲安奈德','氟轻松','倍氯米松','糠酸莫米松','卤米松','丙酸氯倍他索','氢醌','维A酸','复方氟轻松'], 'A12', '激素/内分泌药', 'A'),
    (['氯化钾','葡萄糖酸钙','碳酸氢钠','乳酸钠','门冬氨酸钾镁','甘油磷酸钠','复合磷酸氢','硫酸镁','浓氯化钠'], 'A13', '电解质/酸碱平衡', 'K'),
    (['碘伏','碘酊','酒精','乙醇','过氧化氢','氯己定','聚维酮碘','苯扎溴铵','硫软膏','碘甘油'], 'I01', '外用消毒/皮肤制剂', 'I'),
    (['乳膏','软膏','凝胶','霜剂','酊','洗剂','搽剂','喷雾剂','贴剂','膜剂','栓剂','滴眼液','眼膏','滴耳液','鼻喷剂','泡沫剂','气雾剂','散剂外用','溶液外用'], 'I02', '外用制剂', 'I'),
    (['益母草','开喉剑','银胡感冒','金黄散','板蓝根','感冒清热','蒲地蓝','蓝芩','肺力咳','小儿','妇炎','康复新','丹参','血栓通','血塞通','银杏','天麻','六味地黄','补中益气','逍遥','归脾','八珍','乌鸡白凤','保妇康','金刚藤','桂枝茯苓','散结镇痛','宫血宁','安坤','女金','定坤','坤泰'], 'C01', '中成药', 'A'),
]

# 专科标签关键词
CHILDREN_KEYWORDS = ['儿童','小儿','婴儿','新生儿','开喉剑']
WOMEN_KEYWORDS = ['缩宫素','阿托西班','利托君','硫酸镁','卡贝缩宫素','卡前列素','米非司酮','米索前列醇',
                  '益母草','地屈孕酮','黄体酮','戊酸雌二醇','雌二醇','炔雌醇','促性腺激素','绒促性素',
                  '尿促性素','屈螺酮','去氧孕烯','依托孕烯','戈舍瑞林','亮丙瑞林','来曲唑','氯米芬',
                  '保妇康','金刚藤','桂枝茯苓','散结镇痛','宫血宁','妇炎','安坤','女金','定坤','坤泰',
                  '乌鸡白凤','八珍','归脾','逍遥','戊酸雌二醇','雌二醇屈螺酮','阿托西班']
REHAB_KEYWORDS = ['右佐匹克隆','氯硝西泮','阿米替林','曲唑酮','氟西汀','舍曲林','艾司西酞普兰','文拉法辛',
                  '度洛西汀','丙戊酸','卡马西平','奥卡西平','左乙拉西坦','拉莫三嗪','多奈哌齐','美金刚',
                  '吡拉西坦','奥拉西坦','胞磷胆碱','尼莫地平','倍他司汀','氟桂利嗪','丁苯酞','巴氯芬',
                  '乙哌立松','替扎尼定','肉毒毒素','肠内营养','甘油果糖']

# 高警示药品关键词（基于药品名中的▲标记和特定药品）
HIGH_ALERT_KEYWORDS = ['人血白蛋白','免疫球蛋白','肉毒毒素','50%葡萄糖','氯化钾','浓氯化钠',
                       '胰岛素','肝素','依诺肝素','硫酸镁','缩宫素','阿托西班','利托君',
                       '肾上腺素','去甲肾上腺素','去氧肾上腺素','多巴胺','多巴酚丁胺','硝普钠',
                       '氨茶碱','甲氨蝶呤','长春新碱','顺铂','高渗']

# 精神/毒性药品
CONTROLLED_KEYWORDS = ['精二','精一','毒性','麻醉','第一类','第二类']

# 科室归大类
DEPT_GROUP = {
    '妇产科': '妇产科',
    '妇科门诊': '妇产科',
    '产房': '妇产科',
    '产康': '康复科',
    '儿科': '儿科',
    '新生儿科': '儿科',
    '康复科': '康复科',
    '医学美容': '康复科',
    '麻醉手术': '手术室',
    '中医科': '其他',
    '全科': '其他',
    '口腔': '其他',
    '外科': '其他',
    '皮肤': '其他',
    '家庭健康': '其他',
    '疼痛管理': '其他',
    '预防保健': '其他',
}

def get_dept_group(dept):
    for k, v in DEPT_GROUP.items():
        if k in dept:
            return v
    return '其他'

def get_pharma_category(drug_name):
    """根据药品名称匹配药理大类"""
    for keywords, code, name, zone in PHARMA_CATEGORY_RULES:
        for kw in keywords:
            if kw in drug_name:
                return code, name, zone
    return 'A99', '其他西药', 'A'

def get_specialty_tags(drug_name, depts):
    """获取专科标签"""
    tags = []
    dept_groups = set(get_dept_group(d) for d in depts)
    
    # 儿科标签：药品名含儿童关键词 或 主要在儿科使用
    is_child_drug = any(kw in drug_name for kw in CHILDREN_KEYWORDS)
    ped_pct = sum(1 for d in depts if get_dept_group(d) == '儿科') / max(len(depts), 1)
    if is_child_drug or ped_pct >= 0.4:
        tags.append('儿童')
    
    # 女性标签
    if any(kw in drug_name for kw in WOMEN_KEYWORDS):
        tags.append('女性')
    elif '妇产科' in str(depts) or '妇科' in str(depts):
        ob_pct = sum(1 for d in depts if get_dept_group(d) == '妇产科') / max(len(depts), 1)
        if ob_pct >= 0.3:
            tags.append('女性')
    
    # 康复标签
    if any(kw in drug_name for kw in REHAB_KEYWORDS):
        tags.append('康复')
    else:
        rehab_pct = sum(1 for d in depts if get_dept_group(d) == '康复科') / max(len(depts), 1)
        if rehab_pct >= 0.4:
            tags.append('康复')
    
    if not tags:
        tags.append('通用')
    
    return tags

def is_high_alert(drug_name):
    """判断是否高警示药品"""
    if '▲' in drug_name or '★' in drug_name:
        return True
    return any(kw in drug_name for kw in HIGH_ALERT_KEYWORDS)

def is_controlled(drug_name):
    """判断是否精神/毒性药品"""
    return any(kw in drug_name for kw in CONTROLLED_KEYWORDS)

def is_temporary(drug_name):
    """判断是否临购药品"""
    return '临购' in drug_name

def is_discontinued(drug_name):
    """判断是否停用药品"""
    return '停用' in drug_name

def get_dosage_form(drug_name, spec):
    """推断剂型"""
    text = drug_name + str(spec)
    if any(k in text for k in ['注射液','注射用']):
        return '注射剂'
    if any(k in text for k in ['输液','氯化钠注射液','葡萄糖注射液']):
        return '大输液'
    if any(k in text for k in ['片','分散片','缓释片','控释片','肠溶片']):
        return '口服固体制剂'
    if any(k in text for k in ['胶囊','软胶囊']):
        return '口服固体制剂'
    if any(k in text for k in ['颗粒','干混悬','散剂']):
        return '口服颗粒/散剂'
    if any(k in text for k in ['口服液','口服溶液','混悬液','糖浆','合剂']):
        return '口服液体制剂'
    if any(k in text for k in ['乳膏','软膏','凝胶','霜','搽剂','洗剂']):
        return '外用半固体制剂'
    if any(k in text for k in ['滴眼液','眼膏','滴耳液','鼻喷','喷雾剂','气雾剂','泡沫剂','贴剂','酊']):
        return '外用液/气雾剂'
    if any(k in text for k in ['栓剂','栓']):
        return '栓剂'
    if any(k in text for k in ['胶囊','泡腾片']):
        return '口服固体制剂'
    return '其他'

def parse_look_alike_markers(drug_name):
    """解析易混淆标记"""
    markers = []
    if '▲' in drug_name:
        markers.append('▲高警示')
    if '△' in drug_name:
        markers.append('△同类名似')
    if '★' in drug_name:
        markers.append('★产科急救')
    if '●' in drug_name:
        markers.append('●重点监测')
    if '☆' in drug_name:
        markers.append('☆普通警示')
    return markers

# ============================================================
# 主分析流程
# ============================================================
def main():
    print("=" * 60)
    print("步骤1: 数据清洗与标准化")
    print("=" * 60)
    
    # 读取数据
    df = pd.read_excel(INPUT_FILE, header=None, skiprows=1)
    df.columns = ['c0','科室','药品代码','药品类别','药品名称','规格','数量','单位']
    df = df.drop(columns=['c0'])
    
    # 移除合计行
    total_qty = df[df['科室'] == '合计：']['数量'].values
    df = df[df['科室'] != '合计：'].copy()
    
    # 标准化数量
    df['数量'] = pd.to_numeric(df['数量'], errors='coerce')
    missing_qty = df['数量'].isnull().sum()
    df['数量'] = df['数量'].fillna(0)
    if missing_qty > 0:
        print(f"  [异常] 数量缺失{missing_qty}条，已填充为0")
    
    # 标准化字段
    df['药品名称'] = df['药品名称'].astype(str).str.strip()
    df['规格'] = df['规格'].astype(str).str.strip()
    df['科室'] = df['科室'].astype(str).str.strip()
    df['药品代码'] = df['药品代码'].astype(str).str.strip().str.replace('.0', '', regex=False)
    df['单位'] = df['单位'].astype(str).str.strip()
    
    # 标记异常
    df['异常标记'] = ''
    df.loc[df['数量'] == 0, '异常标记'] = '零发药'
    df.loc[df['药品名称'].str.contains('停用', na=False), '异常标记'] += '|停用'
    
    print(f"  总记录数: {len(df)}")
    print(f"  唯一药品: {df['药品名称'].nunique()}种")
    print(f"  唯一科室: {df['科室'].nunique()}个")
    print(f"  总发药量: {df['数量'].sum():.1f}")
    print(f"  零发药记录: {(df['数量']==0).sum()}条")
    print(f"  停用药品记录: {df['药品名称'].str.contains('停用',na=False).sum()}条")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤2: 周转计算")
    print("=" * 60)
    
    # 按药品汇总
    drug_summary = df.groupby(['药品名称','药品代码','药品类别','规格','单位']).agg(
        总量=('数量','sum'),
        记录数=('数量','count'),
        科室数=('科室','nunique'),
        零发药次数=('数量', lambda x: (x==0).sum())
    ).reset_index()
    
    # 月均消耗
    drug_summary['月均消耗'] = drug_summary['总量'] / PERIOD_MONTHS
    
    # 周转率（无库存数据，用科室覆盖度近似）
    # 周转率 = 月均消耗 / 月均库存，无库存数据时用月均消耗值本身+科室覆盖度近似
    drug_summary['周转率_近似'] = drug_summary['月均消耗'] / (drug_summary['科室数'].clip(lower=1))
    
    # 周转等级
    drug_summary['周转等级'] = pd.cut(drug_summary['月均消耗'], 
        bins=[-0.01, 1, 10, 50, 200, float('inf')],
        labels=['极低','低','中','高','极高'])
    
    print(f"  月均消耗>100(高周转): {(drug_summary['月均消耗']>100).sum()}种")
    print(f"  月均消耗10-100(中周转): {((drug_summary['月均消耗']>=10)&(drug_summary['月均消耗']<=100)).sum()}种")
    print(f"  月均消耗<10(低周转): {(drug_summary['月均消耗']<10).sum()}种")
    print(f"  月均消耗<1(极低周转): {(drug_summary['月均消耗']<1).sum()}种")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤3: 专科标签化")
    print("=" * 60)
    
    # 为每个药品计算科室分布
    drug_depts = df.groupby('药品名称')['科室'].unique().to_dict()
    drug_dept_counts = df.groupby('药品名称')['科室'].nunique().to_dict()
    
    tags_list = []
    dept_group_list = []
    for _, row in drug_summary.iterrows():
        name = row['药品名称']
        depts = drug_depts.get(name, [])
        tags = get_specialty_tags(name, depts)
        tags_list.append(','.join(tags))
        
        # 主要科室大类
        dept_g = [get_dept_group(d) for d in depts]
        from collections import Counter
        if dept_g:
            main_group = Counter(dept_g).most_common(1)[0][0]
        else:
            main_group = '其他'
        dept_group_list.append(main_group)
    
    drug_summary['专科标签'] = tags_list
    drug_summary['主要科室大类'] = dept_group_list
    
    # 临购标记
    drug_summary['是否临购'] = drug_summary['药品名称'].apply(is_temporary)
    drug_summary['是否停用'] = drug_summary['药品名称'].apply(is_discontinued)
    
    # 临购药品来源科别
    lg_depts = df[df['药品名称'].str.contains('临购', na=False)].groupby('药品名称')['科室'].unique().to_dict()
    drug_summary['临购来源科别'] = drug_summary['药品名称'].apply(
        lambda x: ','.join(lg_depts.get(x, [])) if is_temporary(x) else '')
    
    tag_counts = drug_summary['专科标签'].value_counts()
    print("  专科标签分布:")
    for tag, cnt in tag_counts.items():
        print(f"    {tag}: {cnt}种")
    print(f"  临购药品: {drug_summary['是否临购'].sum()}种")
    print(f"  停用药品: {drug_summary['是否停用'].sum()}种")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤4: ABC-XYZ矩阵分类")
    print("=" * 60)
    
    # ABC分类：按总量（金额代理）累计占比
    # 排除停用药品后做ABC
    active = drug_summary[~drug_summary['是否停用']].copy()
    active_sorted = active.sort_values('总量', ascending=False).reset_index(drop=True)
    total_val = active_sorted['总量'].sum()
    active_sorted['累计占比'] = active_sorted['总量'].cumsum() / total_val * 100
    active_sorted['ABC分类'] = 'C'
    active_sorted.loc[active_sorted['累计占比'] <= 70, 'ABC分类'] = 'A'
    active_sorted.loc[(active_sorted['累计占比'] > 70) & (active_sorted['累计占比'] <= 90), 'ABC分类'] = 'B'
    
    # XYZ分类：用科室间变异系数(CV)作为波动代理
    # 计算每个药品在各科室的发药量变异系数
    cv_dict = {}
    for name in drug_summary['药品名称']:
        sub = df[df['药品名称'] == name]
        if len(sub) > 1:
            vals = sub['数量'].values
            mean_v = vals.mean()
            if mean_v > 0:
                cv = vals.std() / mean_v
            else:
                cv = 1.0
        else:
            cv = 0.0
        cv_dict[name] = cv
    
    drug_summary['波动系数CV'] = drug_summary['药品名称'].map(cv_dict)
    
    def xyz_classify(row):
        if row['是否临购']:
            return 'Z'
        cv = row['波动系数CV']
        if cv <= 0.5:
            return 'X'
        elif cv <= 1.5:
            return 'Y'
        else:
            return 'Z'
    drug_summary['XYZ分类'] = drug_summary.apply(xyz_classify, axis=1)
    
    # 合并ABC（停用的默认C）
    abc_map = dict(zip(active_sorted['药品名称'], active_sorted['ABC分类']))
    drug_summary['ABC分类'] = drug_summary['药品名称'].map(abc_map).fillna('C')
    
    # 矩阵
    drug_summary['矩阵分类'] = drug_summary['ABC分类'] + drug_summary['XYZ分类']
    
    matrix = drug_summary.groupby('矩阵分类').agg(药品数=('药品名称','count'), 总量=('总量','sum')).sort_index()
    print("  ABC-XYZ矩阵分布:")
    print(matrix.to_string())
    
    abc_counts = drug_summary['ABC分类'].value_counts()
    xyz_counts = drug_summary['XYZ分类'].value_counts()
    print(f"\n  ABC: A={abc_counts.get('A',0)} B={abc_counts.get('B',0)} C={abc_counts.get('C',0)}")
    print(f"  XYZ: X={xyz_counts.get('X',0)} Y={xyz_counts.get('Y',0)} Z={xyz_counts.get('Z',0)}")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤5: 五级货位编码编排")
    print("=" * 60)
    
    # 药理大类
    cat_info = drug_summary['药品名称'].apply(get_pharma_category)
    drug_summary['药理大类代码'] = cat_info.apply(lambda x: x[0])
    drug_summary['药理大类'] = cat_info.apply(lambda x: x[1])
    drug_summary['货位区码'] = cat_info.apply(lambda x: x[2])
    
    # 剂型
    drug_summary['剂型'] = drug_summary.apply(lambda x: get_dosage_form(x['药品名称'], x['规格']), axis=1)
    
    # 易混淆标记
    drug_summary['易混淆标记'] = drug_summary['药品名称'].apply(lambda x: ','.join(parse_look_alike_markers(x)))
    
    # 高警示/特殊管理
    drug_summary['是否高警示'] = drug_summary['药品名称'].apply(is_high_alert)
    drug_summary['是否特殊管理'] = drug_summary['药品名称'].apply(is_controlled)
    
    # 五级编码：区-架-层-位-库
    # 区码已确定
    # 架码：按药理大类代码后两位排序
    drug_summary['架码'] = drug_summary['药理大类代码'].str[1:]
    
    # 层码：按周转等级
    layer_map = {'极高':'3','高':'3','中':'2','低':'1','极低':'1'}
    drug_summary['层码'] = drug_summary['周转等级'].astype(str).map(layer_map).fillna('2')
    
    # 位码：按ABC分类排序
    pos_map = {'A':'01','B':'02','C':'03'}
    drug_summary['位码'] = drug_summary['ABC分类'].map(pos_map).fillna('03')
    
    # 库码：特殊管理
    def get_storage(row):
        if row['是否特殊管理']:
            return 'M'  # 阴凉柜/保险柜
        if row['是否临购'] and not row['是否停用']:
            return 'H'  # 临购专区
        if row['是否高警示']:
            return 'G'  # 高警示专区
        return ''
    drug_summary['库码'] = drug_summary.apply(get_storage, axis=1)
    
    # 完整编码
    drug_summary['货位编码'] = drug_summary.apply(
        lambda r: f"{r['货位区码']}-{r['架码']}-{r['层码']}-{r['位码']}-{r['库码']}" if r['库码'] 
        else f"{r['货位区码']}-{r['架码']}-{r['层码']}-{r['位码']}", axis=1)
    
    print("  货位区码分布:")
    zone_dist = drug_summary.groupby('货位区码').agg(药品数=('药品名称','count'), 药理大类=('药理大类','unique'))
    for zone, row in zone_dist.iterrows():
        print(f"    {zone}区: {row['药品数']}种 | {list(row['药理大类'])[:3]}")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤6: 关联度聚类")
    print("=" * 60)
    
    # 构建科室-药品矩阵，找高频共现组合
    # 用科室级别：同一科室同时使用多药 = 处方组合信号
    dept_drug = df[df['数量'] > 0].groupby(['科室','药品名称'])['数量'].sum().reset_index()
    
    # 按科室大类聚合
    dept_drug['科室大类'] = dept_drug['科室'].apply(get_dept_group)
    group_drug = dept_drug.groupby(['科室大类','药品名称'])['数量'].sum().reset_index()
    
    # 找每个科室大类中用量TOP20的药品，做两两共现
    pair_scores = defaultdict(float)
    for grp, sub in group_drug.groupby('科室大类'):
        top_drugs = sub.nlargest(20, '数量')['药品名称'].tolist()
        for d1, d2 in combinations(top_drugs, 2):
            pair_scores[(d1, d2)] += sub[sub['药品名称'].isin([d1,d2])]['数量'].min()
    
    # 取TOP组合
    top_pairs = sorted(pair_scores.items(), key=lambda x: -x[1])[:15]
    print("  高频处方组合TOP15:")
    for (d1, d2), score in top_pairs:
        print(f"    {d1[:15]} + {d2[:15]} => 关联强度={score:.1f}")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤7: 黄金层分配")
    print("=" * 60)
    
    # A+X -> 黄金层(中层, 1.2-1.5m)
    # A+Y -> 中层
    # B+X -> 中层偏下
    # C/Z -> 上下层
    def get_physical_layer(row):
        if row['是否停用']:
            return '退库区'
        abc = row['ABC分类']
        xyz = row['XYZ分类']
        if abc == 'A' and xyz in ('X','Y'):
            return '黄金层(1.2-1.5m)'
        elif abc == 'A' and xyz == 'Z':
            return '中下层(0.6-1.2m)'
        elif abc == 'B' and xyz in ('X','Y'):
            return '中下层(0.6-1.2m)'
        elif abc == 'B' and xyz == 'Z':
            return '下层(0-0.6m)'
        elif abc == 'C' and xyz == 'X':
            return '上层(1.5-1.8m)'
        elif abc == 'C' and xyz in ('Y','Z'):
            return '上层(1.5-1.8m)'
        return '中下层(0.6-1.2m)'
    
    drug_summary['物理层位'] = drug_summary.apply(get_physical_layer, axis=1)
    
    layer_dist = drug_summary['物理层位'].value_counts()
    print("  物理层位分配:")
    for layer, cnt in layer_dist.items():
        print(f"    {layer}: {cnt}种")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤8: 临购专项处置")
    print("=" * 60)
    
    lg_drugs = drug_summary[drug_summary['是否临购'] & ~drug_summary['是否停用']].copy()
    print(f"  活跃临购药品: {len(lg_drugs)}种")
    
    # 临购频次（记录数作为临购次数代理）
    lg_freq = df[df['药品名称'].str.contains('临购', na=False) & ~df['药品名称'].str.contains('停用', na=False)].groupby('药品名称').agg(
        发药次数=('数量','count'),
        总量=('数量','sum'),
        科室数=('科室','nunique')
    ).reset_index()
    
    # 处置建议
    def lg_action(row):
        freq = row['发药次数']
        qty = row['总量']
        if freq >= 3 or qty >= 20:
            return '建议转常规（≥3次/月或总量≥20），分配正式货位'
        elif freq <= 1 and qty <= 5:
            return '建议释放货位并归档（≤1次/季且总量≤5）'
        else:
            return '继续观察（30天观察期内）'
    
    lg_freq['处置建议'] = lg_freq.apply(lg_action, axis=1)
    
    print("  临购处置建议:")
    for _, r in lg_freq.iterrows():
        print(f"    {r['药品名称'][:25]} | 次数={r['发药次数']} 量={r['总量']:.1f} 科室={r['科室数']} => {r['处置建议']}")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤9: 合规兜底检查")
    print("=" * 60)
    
    # 高警示药品检查
    ha_drugs = drug_summary[drug_summary['是否高警示'] & ~drug_summary['是否停用']]
    print(f"  高警示药品: {len(ha_drugs)}种")
    
    # 检查是否有高警示药品被分配到底层
    ha_bottom = ha_drugs[ha_drugs['物理层位'].str.contains('下层|0-0.6')]
    if len(ha_bottom) > 0:
        print(f"  [违规] {len(ha_bottom)}种高警示药品被分配到底层，需调整:")
        for _, r in ha_bottom.iterrows():
            print(f"    {r['药品名称']} => 当前:{r['物理层位']}")
        # 强制调整到中层
        drug_summary.loc[ha_bottom.index, '物理层位'] = '中下层(0.6-1.2m)★强制调整'
        drug_summary.loc[ha_bottom.index, '库码'] = 'G'
        drug_summary.loc[ha_bottom.index, '货位编码'] = drug_summary.loc[ha_bottom.index].apply(
            lambda r: f"{r['货位区码']}-{r['架码']}-{r['层码']}-{r['位码']}-G", axis=1)
    
    # 特殊管理药品检查
    sm_drugs = drug_summary[drug_summary['是否特殊管理'] & ~drug_summary['是否停用']]
    print(f"  精神/毒性药品: {len(sm_drugs)}种")
    for _, r in sm_drugs.iterrows():
        print(f"    {r['药品名称']} => {r['货位编码']} (M区阴凉柜)")
    
    # ========================================================
    print("\n" + "=" * 60)
    print("步骤10: 生成输出物")
    print("=" * 60)
    
    # 生成关联组合列表
    associations = []
    for (d1, d2), score in top_pairs:
        cat1 = drug_summary[drug_summary['药品名称']==d1]['药理大类'].values
        cat2 = drug_summary[drug_summary['药品名称']==d2]['药理大类'].values
        associations.append({
            '药品1': d1, '药品2': d2, '关联强度': round(score, 1),
            '药理大类1': cat1[0] if len(cat1) else '', '药理大类2': cat2[0] if len(cat2) else ''
        })
    
    # 保存结果
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 货位规划表
    output_cols = [
        '药品名称','药品代码','药品类别','规格','单位','总量','月均消耗','周转等级',
        '专科标签','主要科室大类','是否临购','是否停用','临购来源科别',
        '药理大类','药理大类代码','剂型','易混淆标记',
        '是否高警示','是否特殊管理',
        'ABC分类','XYZ分类','矩阵分类','波动系数CV',
        '货位区码','架码','层码','位码','库码','货位编码','物理层位'
    ]
    
    # 停用药品排序到最后
    drug_summary['排序权重'] = drug_summary['是否停用'].apply(lambda x: 1 if x else 0)
    drug_summary = drug_summary.sort_values(['排序权重','总量'], ascending=[True, False])
    
    drug_summary[output_cols].to_excel(
        os.path.join(OUTPUT_DIR, '药品货位规划表.xlsx'), index=False)
    
    # 关联组合
    pd.DataFrame(associations).to_excel(
        os.path.join(OUTPUT_DIR, '高频处方关联组合.xlsx'), index=False)
    
    # 临购处置
    lg_freq.to_excel(
        os.path.join(OUTPUT_DIR, '临购药品处置建议.xlsx'), index=False)
    
    # 汇总统计JSON
    summary_stats = {
        '总药品数': int(drug_summary['药品名称'].nunique()),
        '活跃药品数': int((~drug_summary['是否停用']).sum()),
        '停用药品数': int(drug_summary['是否停用'].sum()),
        '临购药品数': int(drug_summary['是否临购'].sum()),
        '活跃临购药品数': int((drug_summary['是否临购'] & ~drug_summary['是否停用']).sum()),
        '高警示药品数': int((drug_summary['是否高警示'] & ~drug_summary['是否停用']).sum()),
        '特殊管理药品数': int((drug_summary['是否特殊管理'] & ~drug_summary['是否停用']).sum()),
        'ABC分布': {k: int(v) for k, v in abc_counts.items()},
        'XYZ分布': {k: int(v) for k, v in xyz_counts.items()},
        '矩阵分布': {k: {'药品数': int(v['药品数']), '总量': float(v['总量'])} for k, v in matrix.iterrows()},
        '总发药量': float(drug_summary['总量'].sum()),
        '科室数': int(df['科室'].nunique()),
        '黄金层药品数': int(drug_summary['物理层位'].str.contains('黄金').sum()),
        '高频组合数': len(associations),
    }
    
    with open(os.path.join(OUTPUT_DIR, 'analysis_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)
    
    # 保存原始汇总数据供报告使用
    drug_summary.to_pickle(os.path.join(OUTPUT_DIR, 'drug_summary.pkl'))
    
    print(f"\n  输出文件已保存至: {OUTPUT_DIR}")
    print(f"  - 药品货位规划表.xlsx")
    print(f"  - 高频处方关联组合.xlsx")
    print(f"  - 临购药品处置建议.xlsx")
    print(f"  - analysis_summary.json")
    
    return drug_summary, associations, lg_freq, summary_stats

if __name__ == '__main__':
    result = main()
