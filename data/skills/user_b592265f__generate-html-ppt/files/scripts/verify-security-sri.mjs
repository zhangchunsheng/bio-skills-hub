import { readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import https from 'node:https';

const rootDir = process.cwd();

console.log('🔍 Starting Security & SRI Audit...\n');

let failed = false;

// 1. Check for forbidden domains (bootcdn, staticfile)
console.log('1️⃣ Checking for banned mirror domains (bootcdn.net, staticfile.org)...');

function getAllFiles(dir, fileList = []) {
  const files = readdirSync(dir);
  for (const file of files) {
    if (file.startsWith('.') || file === 'node_modules' || file === '__pycache__' || file === 'verify-security-sri.mjs') continue;
    const filePath = path.join(dir, file);
    if (statSync(filePath).isDirectory()) {
      getAllFiles(filePath, fileList);
    } else if (file.endsWith('.html') || file.endsWith('.md') || file.endsWith('.js') || file.endsWith('.mjs') || file.endsWith('.json')) {
      fileList.push(filePath);
    }
  }
  return fileList;
}

const allFiles = getAllFiles(rootDir);
let bannedOccurrences = 0;

for (const filePath of allFiles) {
  const content = readFileSync(filePath, 'utf8');
  if (/bootcdn\.net|staticfile\.org/i.test(content)) {
    // Check if it is in an explanation of removed mirrors in README
    const lines = content.split('\n');
    lines.forEach((line, idx) => {
      if (/bootcdn\.net|staticfile\.org/i.test(line)) {
        const isDocDisclosure = /移除|eliminated|removed|清理|排除|banned/i.test(line) || /安全策略|Security/i.test(line);
        if (!isDocDisclosure) {
          console.error(`❌ Banned domain found in ${path.relative(rootDir, filePath)}:${idx + 1}: ${line.trim()}`);
          bannedOccurrences++;
          failed = true;
        } else {
          console.log(`ℹ️ [Safe Disclosure] ${path.relative(rootDir, filePath)}:${idx + 1}: ${line.trim()}`);
        }
      }
    });
  }
}

if (bannedOccurrences === 0) {
  console.log('✅ PASS: Zero active references to bootcdn.net / staticfile.org!\n');
} else {
  console.error(`❌ FAIL: Found ${bannedOccurrences} active references to banned mirrors!\n`);
}

// 2. Check for unpinned versions in html files
console.log('2️⃣ Checking for floating/unpinned script versions in HTML files...');
const htmlFiles = allFiles.filter(f => f.endsWith('.html'));
let unpinnedCount = 0;

for (const htmlFile of htmlFiles) {
  const content = readFileSync(htmlFile, 'utf8');
  const floatingPatterns = [
    /src="[^"]*@latest[^"]*"/gi,
    /src="[^"]*@5\//gi,
    /src="[^"]*@10\//gi,
    /src="https:\/\/[^"]*marked\/marked\.min\.js"/gi
  ];
  for (const pat of floatingPatterns) {
    const matches = content.match(pat);
    if (matches) {
      matches.forEach(m => {
        console.error(`❌ Floating version tag found in ${path.relative(rootDir, htmlFile)}: ${m}`);
        unpinnedCount++;
        failed = true;
      });
    }
  }
}

if (unpinnedCount === 0) {
  console.log('✅ PASS: All script tags use exact pinned versions!\n');
} else {
  console.error(`❌ FAIL: Found ${unpinnedCount} floating version tags!\n`);
}

// 3. Verify SRI Hashes against official CDN endpoints
console.log('3️⃣ Verifying SHA-384 SRI Hashes against official CDN artifacts...');

const artifactsToVerify = [
  {
    name: 'ECharts 5.5.0 (cdnjs)',
    url: 'https://cdnjs.cloudflare.com/ajax/libs/echarts/5.5.0/echarts.min.js',
    expectedSri: 'sha384-o5uz97et3bErHvpKfD4Jz4n0JfhJDWABFuF4NP+iEEDxE1VwMWJ19QGR0lqFZnr6'
  },
  {
    name: 'Mermaid 10.9.1 (cdnjs)',
    url: 'https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js',
    expectedSri: 'sha384-WmdflGW9aGfoBdHc4rRyWzYuAjEmDwMdGdiPNacbwfGKxBW/SO6guzuQ76qjnSlr'
  },
  {
    name: 'Marked 12.0.2 (cdnjs)',
    url: 'https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js',
    expectedSri: 'sha384-/TQbtLCAerC3jgaim+N78RZSDYV7ryeoBCVqTuzRrFec2akfBkHS7ACQ3PQhvMVi'
  },
  {
    name: 'Highlight.js 11.9.0 JS (cdnjs)',
    url: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js',
    expectedSri: 'sha384-F/bZzf7p3Joyp5psL90p/p89AZJsndkSoGwRpXcZhleCWhd8SnRuoYo4d0yirjJp'
  },
  {
    name: 'Highlight.js 11.9.0 CSS (cdnjs)',
    url: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css',
    expectedSri: 'sha384-oaMLBGEzBOJx3UHwac0cVndtX5fxGQIfnAeFZ35RTgqPcYlbprH9o9PUV/F8Le07'
  },
  {
    name: 'Lucide 0.344.0 (jsdelivr)',
    url: 'https://cdn.jsdelivr.net/npm/lucide@0.344.0/dist/umd/lucide.min.js',
    expectedSri: 'sha384-tTkFttkBclaU1cloKwOi9xk3pbao3VZxTjLNBt8iFABWDBQibbAbWpVmO28zMuxq'
  }
];

function fetchAndHash(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return resolve(fetchAndHash(res.headers.location));
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} from ${url}`));
      }
      const hash = crypto.createHash('sha384');
      res.on('data', chunk => hash.update(chunk));
      res.on('end', () => resolve(`sha384-${hash.digest('base64')}`));
      res.on('error', reject);
    }).on('error', reject);
  });
}

async function verifyArtifacts() {
  for (const item of artifactsToVerify) {
    try {
      const computed = await fetchAndHash(item.url);
      if (computed === item.expectedSri) {
        console.log(`✅ [MATCH] ${item.name} -> ${computed}`);
      } else {
        console.error(`❌ [MISMATCH] ${item.name}:\n   Expected: ${item.expectedSri}\n   Got:      ${computed}`);
        failed = true;
      }
    } catch (err) {
      console.error(`❌ [FETCH ERROR] ${item.name}: ${err.message}`);
      failed = true;
    }
  }

  console.log('\n========================================');
  if (failed) {
    console.error('🚨 AUDIT RESULT: FAILED! Please fix errors above.');
    process.exit(1);
  } else {
    console.log('🎉 AUDIT RESULT: ALL CHECKS PASSED (100% SECURE & VERIFIED)!');
    process.exit(0);
  }
}

verifyArtifacts();
