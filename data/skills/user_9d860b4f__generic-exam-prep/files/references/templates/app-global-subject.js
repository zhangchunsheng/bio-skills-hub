// templates/app-global-subject.js
// 修复 P7（全局科目选择器）+ P1（登录竞态守卫）。
// 复制到 js/app.js，替换对应的科目状态 / 顶部栏 / openLogin 片段。
(function (global) {
  var QuizApp = (global.QuizApp = global.QuizApp || {});
  var Storage = QuizApp.Storage, Auth = QuizApp.Auth, DataStore = QuizApp.DataStore;
  var App = {};
  var SUBJ_KEY = 'qb_subject';

  // ---------- 全局科目（唯一来源） ----------
  App.currentSubject = null;
  App.getSubject = function () {
    var subs = DataStore.Data.subjects || [];
    if (!subs.length) return null;
    if (App.currentSubject && subs.some(function (s) { return s.id === App.currentSubject; }))
      return App.currentSubject;
    App.currentSubject = subs[0].id;            // 默认首个科目
    try { localStorage.setItem(SUBJ_KEY, App.currentSubject); } catch (e) {}
    return App.currentSubject;
  };
  App.setSubject = function (sid) {
    App.currentSubject = sid;
    try { localStorage.setItem(SUBJ_KEY, sid); } catch (e) {}
    if (QuizApp.Knowledge) QuizApp.Knowledge._selSubject = sid; // 知识卡同步
    renderGlobalSubject();
    route();                                     // 重渲染当前页，所有模块按新科目呈现
  };

  // 顶部常驻科目栏（P7）：放在主区顶部 <div id="topwrap"> 内的 #subjbar（系统标题下方、内容上方，桌面+移动端可见）。
  // 不要放进侧栏抽屉（移动端默认隐藏，用户看不见）。多科目才显示；单科目自动隐藏。
  function renderGlobalSubject() {
    var bar = document.getElementById('subjbar');
    if (!bar) return;
    var subs = DataStore.Data.subjects || [];
    if (subs.length <= 1) { bar.hidden = true; bar.innerHTML = ''; return; }
    bar.hidden = false;
    var cur = App.getSubject();
    var html = '<label class="subj-label">科目</label><select id="globalSubjectSel" class="subj-select">';
    subs.forEach(function (s) {
      html += '<option value="' + s.id + '"' + (s.id === cur ? ' selected' : '') + '>' + esc(s.name) + '</option>';
    });
    html += '</select>';
    bar.innerHTML = html;
    var sel = document.getElementById('globalSubjectSel');
    if (sel) sel.onchange = function () { App.setSubject(sel.value); };
  }
  App.renderGlobalSubject = renderGlobalSubject;

  // ---------- 列表页：只做「章节」筛选（科目已在顶部全局选好） ----------
  App.chapterFilterHTML = function (chapters, chapId) {
    if (!chapters || chapters.length <= 1) return '';   // 单章节不显示
    var html = '<div class="kb-filters"><label class="kb-fl">章节<select class="filter-select" data-role="chapter"><option value="all">全部章节</option>';
    chapters.forEach(function (c) {
      html += '<option value="' + c.id + '"' + (c.id === chapId ? ' selected' : '') + '>' + esc(c.name) + '</option>';
    });
    html += '</select></label></div>';
    return html;
  };
  App.wireChapterFilter = function (view, onChange) {
    var cb = view.querySelector('select[data-role="chapter"]');
    if (cb) cb.onchange = function () { onChange(cb.value); };
  };

  // ---------- 登录：白名单未就绪先禁用提交（P1 竞态） ----------
  function openLogin() {
    var mask = document.getElementById('loginMask');
    mask.hidden = false;
    var input = document.getElementById('loginPhone');
    input.value = '';
    var errEl = document.getElementById('loginErr');
    var okBtn = document.getElementById('loginOk');
    errEl.textContent = '';
    if (!Auth.isWhitelistReady()) {
      okBtn.disabled = true;
      okBtn.textContent = '加载中…';
      errEl.textContent = '白名单加载中，请稍候…';
      Auth.loadWhitelist()
        .then(function () {
          okBtn.disabled = false; okBtn.textContent = '登录';
          if (errEl.textContent === '白名单加载中，请稍候…') errEl.textContent = '';
        })
        .catch(function () {
          okBtn.disabled = false; okBtn.textContent = '登录';
          errEl.textContent = '白名单加载失败，请刷新页面后重试';
        });
    } else { okBtn.disabled = false; okBtn.textContent = '登录'; }
    setTimeout(function () { input.focus(); }, 50);
  }

  // dashboard 模块卡 badge 用全局科目限定（P7）
  function renderDashboard() {
    var v = view();
    var html = '';
    // ... 省略无关部分 ...
    var subj = App.getSubject();
    var mN = Storage.activeMistakesForSubject(subj).length;   // 按全局科目
    var fN = Storage.favoritesForSubject(subj).length;
    // ... 用 mN/fN 渲染 badge ...
    v.innerHTML = html;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  QuizApp.App = App;
})(window);
