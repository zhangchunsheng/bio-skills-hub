// templates/auth-whitelist-guard.js
// 修复 P1：file:// 直开时 fetch 白名单被拦截、以及登录竞态。
// 用法：复制到项目的 js/auth.js，替换原白名单逻辑。
(function (global) {
  var QuizApp = (global.QuizApp = global.QuizApp || {});
  var Auth = {};
  var KEY = 'qb_current_user';
  var whitelistCache = null;
  var whitelistLoaded = false;

  // 内置兜底白名单：file:// 直开 / 离线 / CORS 拦截导致 fetch 失败时仍能登录。
  // 正式 data/whitelist.json 能读到时以文件为准（便于管理员增删）。
  // 注意：这里的 BUILTIN 仅作离线兜底，正式环境请用 whitelist-nickname.md 的 SHA-256 方案。
  var BUILTIN_WHITELIST = {
    entries: [
      { phone: '13800138000', name: '张三' },
      { phone: '13900139000', name: '李四' }
    ]
  };

  Auth.isLoggedIn = function () { return !!localStorage.getItem(KEY); };
  Auth.getCurrentPhone = function () { return localStorage.getItem(KEY) || null; };
  Auth.getDisplayName = function () {
    var phone = Auth.getCurrentPhone();
    if (!phone) return '备考学员';
    return Auth.getNameByPhone(phone) || '备考学员';
  };
  Auth.getNameByPhone = function (phone) {
    if (!whitelistCache) return null;
    for (var i = 0; i < whitelistCache.entries.length; i++)
      if (whitelistCache.entries[i].phone === phone) return whitelistCache.entries[i].name;
    return null;
  };
  // 守卫：白名单是否就绪（app.js openLogin 据此禁用提交按钮，避免竞态误判）
  Auth.isWhitelistReady = function () { return whitelistLoaded && !!whitelistCache; };
  Auth.loadWhitelist = function () {
    return fetch('data/whitelist.json')
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) {
        if (!d || !d.entries) throw new Error('bad-shape');
        whitelistCache = { entries: d.entries };
        whitelistLoaded = true;
        return whitelistCache;
      })
      .catch(function (e) {
        console.warn('[Auth] 白名单文件读取失败，已用内置快照：', e && e.message);
        whitelistCache = BUILTIN_WHITELIST;   // 兜底
        whitelistLoaded = true;
        return whitelistCache;
      });
  };
  Auth.login = function (phone) {
    phone = (phone || '').trim();
    if (!/^1\d{10}$/.test(phone)) return { ok: false, msg: '请输入11位有效手机号' };
    if (!whitelistCache) return { ok: false, msg: '白名单未加载，请稍候再试' }; // 竞态防护
    var name = Auth.getNameByPhone(phone);
    if (!name) return { ok: false, msg: '该手机号不在白名单中，请联系管理员添加' };
    localStorage.setItem(KEY, phone);
    return { ok: true, name: name };
  };
  Auth.logout = function () { localStorage.removeItem(KEY); };

  QuizApp.Auth = Auth;
})(window);
