#!/usr/bin/env node
// 以 archive/entries.json + archive/graph.json 为唯一数据源，
// 重建 medical-ai-intel.html（本地看板）与 deploy/index.html（云端部署目录）的内嵌 DEMO_ENTRIES/DEMO_GRAPH。
// 用法：node build.js
// 关键：每个块只替换自身“const X = ...;”，禁止在替换串里拼接下一个声明名，
//      否则会产生“const DEMO_GRAPH = const DEMO_GRAPH = ...”之类的重复声明导致整段脚本语法错误、页面空白。
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const entriesSrc = JSON.parse(fs.readFileSync(path.join(ROOT, 'archive/entries.json'), 'utf8'));
const graphSrc = JSON.parse(fs.readFileSync(path.join(ROOT, 'archive/graph.json'), 'utf8'));
const htmlPath = path.join(ROOT, 'medical-ai-intel.html');

let html = fs.readFileSync(htmlPath, 'utf8');

const entriesBlock = 'const DEMO_ENTRIES = ' + JSON.stringify(entriesSrc.entries, null, 2) + ';';
const graphBlock = 'const DEMO_GRAPH = ' + JSON.stringify(graphSrc, null, 2) + ';';

// 只匹配到本块自己的第一个 ]; / };（块内不会再出现更早的 }; / ];）
const reEntries = /const DEMO_ENTRIES = \[[\s\S]*?\];/;
const reGraph = /const DEMO_GRAPH = \{[\s\S]*?\};/;

if (!reEntries.test(html)) { console.error('未找到 DEMO_ENTRIES 块'); process.exit(1); }
if (!reGraph.test(html)) { console.error('未找到 DEMO_GRAPH 块'); process.exit(1); }

// 仅替换自身声明，不拼接任何后续关键字
html = html.replace(reEntries, entriesBlock);
html = html.replace(reGraph, graphBlock);

fs.writeFileSync(htmlPath, html);
fs.writeFileSync(path.join(ROOT, 'deploy/index.html'), html);

console.log('build ok → entries=' + entriesSrc.entries.length +
  ' graph.nodes=' + graphSrc.nodes.length + ' graph.edges=' + graphSrc.edges.length);
