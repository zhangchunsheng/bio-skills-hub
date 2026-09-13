#!/usr/bin/env node
// check_ima.cjs — 检测 IMA 凭证是否就绪
// 供 vte-clinical-workflow 的 Step 0 强制前置检查使用。
// 输出单行 JSON 到 stdout：{ "ok": true|false, "source": "env"|"config"|null, "hint": "..." }
// 退出码：0 = 就绪，1 = 未就绪。

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

function main() {
  const envId = process.env.IMA_OPENAPI_CLIENTID;
  const envKey = process.env.IMA_OPENAPI_APIKEY;
  if (envId && envKey) {
    console.log(JSON.stringify({ ok: true, source: 'env', hint: '环境变量 IMA_OPENAPI_CLIENTID / IMA_OPENAPI_APIKEY 已配置' }));
    process.exit(0);
  }

  const dir = path.join(os.homedir(), '.config', 'ima');
  let id = null;
  let key = null;
  try { id = fs.readFileSync(path.join(dir, 'client_id'), 'utf8').trim(); } catch (e) { /* ignore */ }
  try { key = fs.readFileSync(path.join(dir, 'api_key'), 'utf8').trim(); } catch (e) { /* ignore */ }
  if (id && key) {
    console.log(JSON.stringify({ ok: true, source: 'config', hint: '配置文件 ~/.config/ima/ 已就绪' }));
    process.exit(0);
  }

  console.log(JSON.stringify({
    ok: false,
    source: null,
    hint: '未检测到 IMA 凭证。请先连接「ima知识库」(ima-mcp) 连接器，或到 https://ima.qq.com/agent-interface 获取 Client ID / API Key 后写入 ~/.config/ima/（或设置环境变量）。'
  }));
  process.exit(1);
}

main();
