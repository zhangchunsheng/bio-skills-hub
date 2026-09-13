/**
 * ========================================
 * build-shards.js - 题库分片构建脚本
 * ========================================
 * 从 data/questions.json 生成：
 *   1) data/index.json          —— 轻量目录树（科目/章节/试卷元信息 + 题数），首屏秒开
 *   2) data/shards/<sid>__<cid>.json —— 每章一个分片（questions + knowledgePoints）
 *
 * 特性：
 *   - 幂等：可反复运行，先清空 data/shards/ 再重建
 *   - 保留 questions.json 原文件作为整包降级备份（不改动）
 *
 * 用法：
 *   node tools/build-shards.js
 *
 * 题库更新流程：改 questions.json → 跑本脚本 → 提交/部署 data/ 全目录
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DATA_DIR = path.join(ROOT, 'data');
const SRC = path.join(DATA_DIR, 'questions.json');
const INDEX_OUT = path.join(DATA_DIR, 'index.json');
const SHARD_DIR = path.join(DATA_DIR, 'shards');

/** index.json 结构版本；结构变更时 +1，前端 idb.js 的 INDEX_VER 需同步 */
const INDEX_VER = 2;

function shardName(subjectId, chapterId) {
  return subjectId + '__' + chapterId + '.json';
}

function main() {
  if (!fs.existsSync(SRC)) {
    console.error('[build-shards] 找不到源文件:', SRC);
    process.exit(1);
  }
  const raw = fs.readFileSync(SRC, 'utf8');
  let db;
  try {
    db = JSON.parse(raw);
  } catch (e) {
    console.error('[build-shards] questions.json 解析失败:', e.message);
    process.exit(1);
  }

  // 清空并重建 shards 目录
  if (fs.existsSync(SHARD_DIR)) {
    fs.readdirSync(SHARD_DIR).forEach(function (f) {
      if (f.endsWith('.json')) fs.unlinkSync(path.join(SHARD_DIR, f));
    });
  } else {
    fs.mkdirSync(SHARD_DIR, { recursive: true });
  }

  const index = {
    ver: INDEX_VER,
    builtAt: new Date().toISOString(),
    subjects: [],
    mockPapers: [],
    realPapers: []
  };

  let shardCount = 0;
  let questionCount = 0;

  (db.subjects || []).forEach(function (s) {
    const subjEntry = {
      id: s.id,
      name: s.name,
      icon: s.icon || '',
      chapters: []
    };
    (s.chapters || []).forEach(function (c) {
      const questions = c.questions || [];
      const kps = c.knowledgePoints || [];
      questionCount += questions.length;

      // index：仅目录元信息 + 题数/考点数（不含题目本体）
      subjEntry.chapters.push({
        id: c.id,
        name: c.name,
        count: questions.length,
        kpCount: kps.length
      });

      // shard：该章题目本体 + 知识卡
      const shard = { subjectId: s.id, chapterId: c.id, questions: questions, knowledgePoints: kps };
      fs.writeFileSync(
        path.join(SHARD_DIR, shardName(s.id, c.id)),
        JSON.stringify(shard)
      );
      shardCount++;
    });
    index.subjects.push(subjEntry);
  });

  // 试卷：index 保留 questionIds（纯 id 字符串，体积小），startExam 需要它做映射
  function mapPaper(p) {
    return {
      id: p.id,
      name: p.name,
      subjectId: p.subjectId,
      duration: p.duration || 3600,
      totalScore: p.totalScore || 0,
      questionIds: p.questionIds || [],
      count: (p.questionIds || []).length
    };
  }
  index.mockPapers = (db.mockPapers || []).map(mapPaper);
  index.realPapers = (db.realPapers || []).map(mapPaper);

  fs.writeFileSync(INDEX_OUT, JSON.stringify(index));

  // 统计输出
  const indexSize = fs.statSync(INDEX_OUT).size;
  let shardsTotal = 0;
  fs.readdirSync(SHARD_DIR).forEach(function (f) {
    shardsTotal += fs.statSync(path.join(SHARD_DIR, f)).size;
  });

  console.log('[build-shards] 完成');
  console.log('  科目:', index.subjects.length,
    '| 章节分片:', shardCount,
    '| 题目:', questionCount,
    '| 试卷:', index.mockPapers.length + index.realPapers.length);
  console.log('  index.json:', (indexSize / 1024).toFixed(1) + ' KB');
  console.log('  shards 合计:', (shardsTotal / 1024).toFixed(1) + ' KB',
    '（平均', (shardsTotal / Math.max(shardCount, 1) / 1024).toFixed(1) + ' KB/片）');
}

main();
