// templates/quiz-submit-conquer.js
// 修复 P6：共用 submitAnswer —— 客观题答对→markConqueredIfExists，答错→addMistake(幂等)，
// 主观题永不入册，未作答(sel 空)先拦截不入册。复制到 js/quiz.js 的提交函数。
// 注意：所有练习模式（daily/chapter/mock/real）必须复用同一 submit，否则破坏错题/收藏联动。
Quiz._submit = function (item) {
  var q = item.q;
  if (!sess.sel || (Array.isArray(sess.sel) && sess.sel.length === 0)) {
    QuizApp.App.toast('请先选择答案');   // 未作答：拦截，不入错题本
    return;
  }
  var correct = isCorrect(sess.sel, q);
  sess.answers[q.id] = { userAnswer: sess.sel, correct: correct, answered: true };
  sess.sel = null;
  if (q.type !== 'subjective') {                 // 主观题不判分、不入册
    if (correct) {
      Storage.markConqueredIfExists(q.id);       // 答对：标记已攻克（保留记录）
    } else {
      Storage.addMistake({                        // 答错：入册（幂等 by questionId）
        questionId: q.id,
        subjectId: item.subjectId,
        chapterId: item.chapterId,
        questionData: q
      });
    }
    Storage.recordAnswer(correct);
    QuizApp.App.refreshBadges();                  // badge 实时刷新
  }
  Quiz._save();
  Quiz._render();
};

// 收藏按钮（renderQuestion 内）：所有模式统一
Quiz._toggleFav = function (item) {
  var q = item.q;
  var on = Storage.toggleFavorite({
    questionId: q.id, subjectId: item.subjectId, chapterId: item.chapterId, questionData: q
  });
  QuizApp.App.refreshBadges();
  QuizApp.App.toast(on ? '已加入收藏夹' : '已取消收藏');
  Quiz._render();
};

// 考试模式（mock/real）交卷时，批量把客观题错题写入错题本（同样幂等）：
// 在 submitExam 遍历 answers：correct→markConqueredIfExists，wrong→addMistake。
