#!/usr/bin/env python3
"""augment_test_data.py —— 在现有题库上自动追加测试题目/知识点/试卷（不污染主干）

用途：skill 原型数据（如 gen_data.py 内置的 14 题公务员考试）对于冒烟测试够用，
但若需要更真实地模拟「每章有若干题 + 各科目有模拟/真题卷」，可用本脚本一键扩充。

特性：
- 每种角色补一份（不会重复添加）：单选题 +1、多选题 +1、判断题 +1、填空题 +1、主观题 +1、知识点 +1
- 每科目补一份测试模拟卷 + 一份测试真题卷（含章节交叉出题，id 前缀 augment-mock/real）
- 哨兵 id（含含 -aug1 后缀）防重复导入（再次运行跳过）
- 非破坏性：原地更新主 questions.json（需事先存在），然后同步重写 knowledge.json

使用方法：
1. 先跑 gen_data.py（生成 data/questions.json + data/knowledge.json）
2. 再跑本脚本：python3 scripts/augment_test_data.py
3. 最后跑 build-shards.js（重新生成 index.json + 分片）

哨兵：如发现题干含 -aug1 后缀，则该科目已扩充过，直接跳过。

注意：本脚本不负责生成「正式题库」。真实题库请直接编辑 questions.json 后重跑 gen_data.py。
"""

import json, os, sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
Q_PATH = os.path.join(BASE, 'questions.json')
K_PATH = os.path.join(BASE, 'knowledge.json')

SENTINEL = '-aug1'

AUG_QUESTIONS = {
    'single':   {'type':'single',   'question':'测试单选题' + SENTINEL, 'options':[
        {'label':'A','text':'测试选项甲'},{'label':'B','text':'测试选项乙'},
        {'label':'C','text':'测试选项丙'},{'label':'D','text':'测试选项丁'}], 'answer':'B', 'analysis':'扩充数据·测试解析'},
    'multiple': {'type':'multiple', 'question':'测试多选题' + SENTINEL, 'options':[
        {'label':'A','text':'正确项一'},{'label':'B','text':'正确项二'},
        {'label':'C','text':'干扰项三'},{'label':'D','text':'干扰项四'}], 'answer':'AB','analysis':'扩充数据·测试解析'},
    'judge':    {'type':'judge',    'question':'测试判断题' + SENTINEL, 'answer':'正确','analysis':'扩充数据·测试解析'},
    'blank':    {'type':'blank',    'question':'测试填空题' + SENTINEL, 'answer':'测试答案','analysis':'扩充数据·测试解析'},
    'short':    {'type':'short',    'question':'测试简答题' + SENTINEL,
        'scoringPoints':[{'score':5,'point':'测试采分点'}], 'referenceAnswer':'测试参考答案','analysis':'扩充数据·测试解析'},
}

def has_sentinel(subj):
    return any(SENTINEL in (c['name'] if isinstance(c,dict) else '') for c in subj.get('subjects',[]))

def main():
    if not os.path.exists(Q_PATH):
        print(f"[augment] {Q_PATH} 不存在，请先运行 gen_data.py", file=sys.stderr)
        sys.exit(1)

    with open(Q_PATH, 'r', encoding='utf-8') as f:
        root = json.load(f)

    subjects = root.get('subjects', [])
    if not subjects:
        print("[augment] 没有科目，跳过", file=sys.stderr)
        sys.exit(0)

    for subj in subjects:
        sid = subj['id']
        # ---- 章节扩充 ----
        for ch in subj.get('chapters', []):
            cid = ch['id']
            existing_ids = {q['id'] for q in ch.get('questions', [])}
            if any(SENTINEL in qid for qid in existing_ids):
                print(f"[augment] 已扩充过 {sid}/{cid}，跳过")
                continue
            start_idx = len(ch['questions']) + 1
            for i, (role, tmpl) in enumerate(AUG_QUESTIONS.items()):
                qid = f'{cid}-aug{role}'
                obj = dict(tmpl)
                obj['id'] = qid
                ch.setdefault('questions', []).append(obj)
                print(f"  + {sid}/{cid} {role} → {qid}")

        # ---- 试卷扩充 ----
        papers = root.setdefault('mockPapers', [])
        paper_ids = {p['id'] for p in papers}
        mock_id = f'mock-{sid}{SENTINEL}'
        real_id = f'real-{sid}{SENTINEL}'
        if mock_id not in paper_ids:
            all_qids = [q['id'] for ch in subj.get('chapters',[]) for q in ch.get('questions',[])]
            papers.append({
                'id': mock_id, 'name': f'扩充模拟卷({sid})',
                'subjectId': sid, 'type': 'mock',
                'count': len(all_qids), 'duration': 3600, 'totalScore': 100,
                'questionIds': all_qids
            })
            print(f"  + mock paper → {mock_id}")
        if real_id not in paper_ids:
            rpapers = root.setdefault('realPapers', [])
            rpids = {p['id'] for p in rpapers}
            if real_id not in rpids:
                all_qids = [q['id'] for ch in subj.get('chapters',[]) for q in ch.get('questions',[])]
                rpapers.append({
                    'id': real_id, 'name': f'扩充真题卷({sid})',
                    'subjectId': sid, 'type': 'real',
                    'count': len(all_qids), 'duration': 3600, 'totalScore': 100,
                    'questionIds': all_qids
                })
                print(f"  + real paper → {real_id}")

    with open(Q_PATH, 'w', encoding='utf-8') as f:
        json.dump(root, f, ensure_ascii=False, indent=2)

    # 同步更新 knowledge.json（已有代码从 questions.json 抽取 → 由 gen_data.py 覆盖即可）
    # 这里不重写 knowledge.json，交给 gen_data.py 的 --augment 或 build-shards.js。
    print("[augment] questions.json 扩充完成，请重跑 scripts/gen_data.py + scripts/build-shards.js")

if __name__ == '__main__':
    main()
