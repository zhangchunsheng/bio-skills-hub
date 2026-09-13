// templates/storage-mistake-conquer.js
// 修复 P6：错题用「攻克」语义（答对标记 conquered 但保留记录，不删除），标题 N 用未攻克数，
// 并提供按科目筛选助手（供全局科目选择器联动）。
// 复制到 js/storage.js，合并进 Storage 对象。
(function (global) {
  var QuizApp = (global.QuizApp = global.QuizApp || {});
  var Storage = {};

  // ---- mistakes（幂等 by questionId + 累计 wrongCount + 攻克状态） ----
  // 记录结构：{ questionId, subjectId, chapterId, questionData,
  //   wrongCount, status('active'|'conquered'), firstWrongAt, lastWrongAt, conqueredAt }
  Storage.getMistakes = function () { return readRaw(userPrefix() + 'mistakes', {}); };
  Storage.addMistake = function (rec) {
    var m = readRaw(userPrefix() + 'mistakes', {});
    var now = Date.now();
    if (m[rec.questionId]) {                       // 重复答错：累加 + 退回 active
      var ex = m[rec.questionId];
      ex.wrongCount = (ex.wrongCount || 1) + 1;
      ex.lastWrongAt = now;
      ex.status = 'active';
      writeRaw(userPrefix() + 'mistakes', m);
      return false;
    }
    m[rec.questionId] = {
      questionId: rec.questionId, subjectId: rec.subjectId, chapterId: rec.chapterId,
      questionData: rec.questionData, wrongCount: 1, status: 'active',
      firstWrongAt: now, lastWrongAt: now, conqueredAt: null
    };
    writeRaw(userPrefix() + 'mistakes', m);
    return true;
  };
  Storage.markConquered = function (qid) {          // 答对 → 标记已攻克（不删）
    var m = readRaw(userPrefix() + 'mistakes', {});
    if (m[qid]) { m[qid].status = 'conquered'; m[qid].conqueredAt = Date.now(); writeRaw(userPrefix() + 'mistakes', m); }
  };
  Storage.markConqueredIfExists = function (qid) { if (readRaw(userPrefix() + 'mistakes', {})[qid]) Storage.markConquered(qid); };
  Storage.removeMistake = function (qid) {
    var m = readRaw(userPrefix() + 'mistakes', {});
    if (m[qid]) { delete m[qid]; writeRaw(userPrefix() + 'mistakes', m); return true; }
    return false;
  };
  Storage.activeMistakeCount = function () {        // 标题 N：未攻克数
    var m = readRaw(userPrefix() + 'mistakes', {}), n = 0;
    Object.keys(m).forEach(function (k) { if (m[k].status !== 'conquered') n++; });
    return n;
  };
  Storage.mistakeCount = function () { return Object.keys(readRaw(userPrefix() + 'mistakes', {})).length; };
  Storage.clearAllMistakes = function () { writeRaw(userPrefix() + 'mistakes', {}); };

  // 按科目筛选（全局科目选择器联动；sid 为空返回全部）
  Storage.mistakesForSubject = function (sid) {
    var m = readRaw(userPrefix() + 'mistakes', {});
    return Object.keys(m).map(function (k) { return m[k]; }).filter(function (r) { return !sid || r.subjectId === sid; });
  };
  Storage.activeMistakesForSubject = function (sid) {
    return Storage.mistakesForSubject(sid).filter(function (r) { return r.status !== 'conquered'; });
  };

  // ---- favorites（同结构） ----
  Storage.getFavorites = function () { return readRaw(userPrefix() + 'favorites', {}); };
  Storage.isFavorite = function (qid) { return !!readRaw(userPrefix() + 'favorites', {})[qid]; };
  Storage.toggleFavorite = function (rec) {
    var f = readRaw(userPrefix() + 'favorites', {});
    if (f[rec.questionId]) { delete f[rec.questionId]; writeRaw(userPrefix() + 'favorites', f); return false; }
    f[rec.questionId] = rec; writeRaw(userPrefix() + 'favorites', f); return true;
  };
  Storage.favoriteCount = function () { return Object.keys(readRaw(userPrefix() + 'favorites', {})).length; };
  Storage.clearAllFavorites = function () { writeRaw(userPrefix() + 'favorites', {}); };
  Storage.favoritesForSubject = function (sid) {
    var f = readRaw(userPrefix() + 'favorites', {});
    return Object.keys(f).map(function (k) { return f[k]; }).filter(function (r) { return !sid || r.subjectId === sid; });
  };

  // ---- 闪卡掌握状态（独立标记，与交卷正确率无关） ----
  // 结构：{ [kpId]: { state:'new'|'learning'|'mastered', chapterId } }
  Storage.getCardState = function (kpId) { var c = readRaw(userPrefix() + 'cards', {})[kpId]; return c ? c.state : 'new'; };
  Storage.setCardState = function (kpId, state, chapterId) {
    var c = readRaw(userPrefix() + 'cards', {});
    c[kpId] = { state: state, chapterId: chapterId };
    writeRaw(userPrefix() + 'cards', c);
  };
  Storage.resetChapterCards = function (chapterId) {   // 重置某章掌握状态
    var c = readRaw(userPrefix() + 'cards', {});
    Object.keys(c).forEach(function (k) { if (c[k].chapterId === chapterId) delete c[k]; });
    writeRaw(userPrefix() + 'cards', c);
  };

  // readRaw/writeRaw/userPrefix 同项目 storage.js
  QuizApp.Storage = Storage;
})(window);
