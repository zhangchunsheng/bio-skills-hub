// templates/app-error-recovery.js —— P10/P12 错误恢复 UI（showError 双按钮 + render 空题恢复）
// 用法：复制 showError 到 app.js，复制 render 空态到 quiz.js

// === app.js: showError（双按钮：重试 + 重置缓存并重试）===
App.showError = function (view, msg, onRetry) {
  view.innerHTML = '<div class="state-box"><span class="ico">⚠️</span>' +
    '<div class="msg">题库加载失败</div>' +
    '<div class="sub">' + esc(msg || '请检查网络后重试') + '</div>' +
    '<div class="state-actions">' +
      '<button class="btn" id="__retry">重新加载</button>' +
      '<button class="btn ghost" id="__wipe">重置缓存并重试</button>' +
    '</div></div>';
  var b = view.querySelector('#__retry'); if (b) b.onclick = onRetry;
  var w = view.querySelector('#__wipe'); if (w) w.onclick = function () {
    try {
      var req = indexedDB.deleteDatabase('exam_prep_db');
      req.onsuccess = req.onerror = req.onblocked = function () {
        setTimeout(function () { location.reload(); }, 200);
      };
      setTimeout(function () { location.reload(); }, 1500); // 兜底
    } catch (e) { location.reload(); }
  };
};

// === quiz.js: render() 空 items 时显示恢复 UI（不显示无操作的「没有可练习的题目」）===
// 替换 render() 里的空态一行：
//   if (!S || !S.items || !S.items.length) { target.innerHTML = '<div class="empty">...</div>'; return; }
// 为下面的 state-box：
function renderEmptyState(target) {
  target.innerHTML = '<div class="state-box">' +
    '<span class="ico">📭</span>' +
    '<div class="msg">题目数据未成功加载</div>' +
    '<div class="sub">缓存或网络异常，请尝试重置后重试</div>' +
    '<div class="state-actions">' +
      '<button class="btn" id="__freshReload">刷新页面</button>' +
      '<button class="btn ghost" id="__wipeReload">重置缓存并刷新</button>' +
    '</div></div>';
  var fr = target.querySelector('#__freshReload');
  if (fr) fr.onclick = function () { location.reload(); };
  var wr = target.querySelector('#__wipeReload');
  if (wr) wr.onclick = function () {
    try {
      var r = indexedDB.deleteDatabase('exam_prep_db');
      r.onsuccess = r.onerror = function () { location.reload(); };
      setTimeout(function () { location.reload(); }, 2000);
    } catch (e) { location.reload(); }
  };
}
