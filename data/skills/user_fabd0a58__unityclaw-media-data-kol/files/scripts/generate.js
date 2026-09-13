#!/usr/bin/env node
/**
 * UnityClaw Media KOL Profile - CLI Generator
 */

import { mkdirSync, statSync, writeFileSync } from 'fs';
import { isIP } from 'net';
import { join, resolve } from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'util';

const SKILL_VERSION = '1.2.5';
const MIN_SDK_VERSION = '1.2.2';
const DEFAULT_TIMEOUT_MS = 900000;
const DEFAULT_RETRIES = 1;
const ORDERED_KEYS = [
  'user_id', 'username', 'name', 'nickname', 'signature', 'description', 'bio',
  'follower_count', 'following_count', 'like_count', 'post_count', 'note_count',
  'avatar', 'updated',
];
const LABELS = {
  zh: {
    user_id: '用户ID', username: '用户名', name: '名称', nickname: '昵称', signature: '简介',
    description: '描述', bio: '简介', follower_count: '粉丝数', following_count: '关注数',
    like_count: '获赞数', post_count: '作品数', note_count: '笔记数', avatar: '头像', updated: '更新时间',
  },
  en: {
    user_id: 'User ID', username: 'Username', name: 'Name', nickname: 'Nickname', signature: 'Bio',
    description: 'Description', bio: 'Bio', follower_count: 'Followers', following_count: 'Following',
    like_count: 'Likes', post_count: 'Posts', note_count: 'Notes', avatar: 'Avatar', updated: 'Updated',
  },
  ja: {
    user_id: 'ユーザーID', username: 'ユーザー名', name: '名前', nickname: 'ニックネーム', signature: 'プロフィール',
    description: '説明', bio: 'プロフィール', follower_count: 'フォロワー数', following_count: 'フォロー数',
    like_count: 'いいね数', post_count: '投稿数', note_count: 'ノート数', avatar: 'アバター', updated: '更新日時',
  },
};

function printHelp() {
  console.log(`
UnityClaw Media KOL Profile - CLI Generator v${SKILL_VERSION}

Usage:
  node scripts/generate.js --url "https://www.xiaohongshu.com/user/profile/xxxx"
  node scripts/generate.js --url "https://www.tiktok.com/@username" --lang en --json

Parameters:
  --url, -u        Public social media profile URL (required)
  --lang, -l       Output label language: auto, zh, en, ja (default: auto)
  --output-dir     Task output directory (default: "./tasks")
  --timeout        Request timeout in milliseconds (default: ${DEFAULT_TIMEOUT_MS})
  --retries        Retries for transient failures, from 0 to 3 (default: ${DEFAULT_RETRIES})
  --json           Print one machine-readable JSON result
  --help, -h       Show this help message
`);
}

function parseInteger(value, name, minimum, maximum) {
  if (!/^\d+$/.test(value)) throw new Error(`${name} must be an integer between ${minimum} and ${maximum}`);
  const number = Number(value);
  if (number < minimum || number > maximum) throw new Error(`${name} must be between ${minimum} and ${maximum}`);
  return number;
}

function detectLanguage(input) {
  const requested = String(input || 'auto').trim().toLowerCase();
  if (requested !== 'auto') {
    if (/^zh(?:[-_]|$)/.test(requested)) return 'zh';
    if (/^en(?:[-_]|$)/.test(requested)) return 'en';
    if (/^ja(?:[-_]|$)/.test(requested)) return 'ja';
    throw new Error('--lang must be auto, zh, en, or ja');
  }
  const locale = [process.env.OPENCLAW_LOCALE, process.env.LC_ALL, process.env.LANGUAGE, process.env.LANG]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
  if (locale.includes('zh')) return 'zh';
  if (locale.includes('ja')) return 'ja';
  return 'en';
}

function isPrivateHostname(hostname) {
  const host = hostname.toLowerCase().replace(/^\[|\]$/g, '');
  if (host === 'localhost' || host.endsWith('.localhost') || host.endsWith('.local')) return true;
  const ipVersion = isIP(host);
  if (ipVersion === 4) {
    const parts = host.split('.').map(Number);
    return parts[0] === 0
      || parts[0] === 10
      || parts[0] === 127
      || (parts[0] === 169 && parts[1] === 254)
      || (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31)
      || (parts[0] === 192 && parts[1] === 168);
  }
  if (ipVersion === 6) return host === '::1' || /^f[cd]/i.test(host) || /^fe[89ab]/i.test(host);
  return false;
}

function detectPlatform(hostname) {
  const host = hostname.toLowerCase().replace(/^www\./, '');
  if (host === 'xiaohongshu.com' || host.endsWith('.xiaohongshu.com')) return 'xiaohongshu';
  if (host === 'tiktok.com' || host.endsWith('.tiktok.com')) return 'tiktok';
  if (host === 'douyin.com' || host.endsWith('.douyin.com')) return 'douyin';
  if (host === 'instagram.com' || host.endsWith('.instagram.com')) return 'instagram';
  if (host === 'youtube.com' || host.endsWith('.youtube.com')) return 'youtube';
  if (host === 'weibo.com' || host.endsWith('.weibo.com')) return 'weibo';
  if (host === 'bilibili.com' || host.endsWith('.bilibili.com')) return 'bilibili';
  return 'other';
}

function normalizeProfileUrl(input) {
  const value = String(input || '').trim();
  if (!value) throw new Error('--url is required and cannot be blank');

  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error('Invalid profile URL format');
  }
  if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('Profile URL must use HTTP or HTTPS');
  if (parsed.username || parsed.password) throw new Error('Profile URL must not contain credentials');
  if (isPrivateHostname(parsed.hostname)) throw new Error('Profile URL must use a public hostname');

  const platform = detectPlatform(parsed.hostname);
  if (platform === 'xiaohongshu' && !parsed.pathname.includes('/user/profile/')) {
    throw new Error('Xiaohongshu URL must be a user profile URL containing /user/profile/');
  }
  if (platform === 'tiktok' && (!/^\/@[^/]+\/?$/.test(parsed.pathname) || parsed.pathname.includes('/video/'))) {
    throw new Error('TikTok URL must be a user profile URL such as https://www.tiktok.com/@username');
  }
  parsed.hash = '';
  return { url: parsed.href, platform };
}

function hasValue(value) {
  if (value === undefined || value === null) return false;
  if (typeof value === 'string') return value.trim() !== '';
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return true;
}

function validateProfileData(data, platform) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('The profile response is not an object');
  if (!Object.values(data).some(hasValue)) throw new Error('The profile response contains no fields');

  const missingCoreFields = [];
  if (!hasValue(data.user_id) && !hasValue(data.nickname) && !hasValue(data.username) && !hasValue(data.name)) {
    missingCoreFields.push('profile_identity');
  }
  if (!hasValue(data.follower_count)) missingCoreFields.push('follower_count');
  const warnings = [];
  if (missingCoreFields.length) warnings.push(`Profile snapshot is incomplete: missing ${missingCoreFields.join(', ')}`);
  if (platform === 'other') warnings.push('Platform was not recognized; verify that returned fields describe the intended profile');
  return { data, missingCoreFields, warnings };
}

function localizeFields(data, language) {
  const keys = [
    ...ORDERED_KEYS.filter((key) => Object.hasOwn(data, key)),
    ...Object.keys(data).filter((key) => !ORDERED_KEYS.includes(key)),
  ];
  return keys
    .filter((key) => hasValue(data[key]))
    .map((key) => ({ key, label: LABELS[language]?.[key] || LABELS.en[key] || key, value: data[key] }));
}

function saveProfileArtifact(taskFolder, artifact) {
  if (!taskFolder) throw new Error('The SDK result did not provide a task folder');
  const folder = resolve(taskFolder);
  mkdirSync(folder, { recursive: true });
  const resultPath = join(folder, 'kol-profile.json');
  writeFileSync(resultPath, `${JSON.stringify(artifact, null, 2)}\n`, 'utf8');
  const stats = statSync(resultPath);
  if (!stats.isFile() || stats.size === 0) throw new Error(`Failed to save profile result: ${resultPath}`);
  return { resultPath, resultBytes: stats.size };
}

function errorText(value) {
  try {
    return typeof value === 'string' ? value : JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function isRetryable(value) {
  const text = errorText(value);
  return /ECONNRESET|ECONNABORTED|ETIMEDOUT|ENOTFOUND|EAI_AGAIN|socket hang up|network|timed?\s*out|\b429\b|\b502\b|\b503\b|\b504\b|temporar(?:y|ily) unavailable/i.test(text);
}

function getFailureMessage(result) {
  return result?.response?.msg
    || [...(result?.logs || [])].reverse().find((log) => log.level === 'error')?.message
    || 'KOL profile retrieval failed';
}

function sleep(milliseconds) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, milliseconds));
}

function emitFailure({ json, code, message, retryable = false, attempts = 0, outputDir, result }) {
  const payload = {
    success: false,
    error: { code, message, retryable },
    attempts,
    outputDir,
    taskId: result?.taskId,
    taskFolder: result?.taskFolder,
    logs: result?.logs,
  };
  if (json) console.log(JSON.stringify(payload));
  else {
    console.error(`\x1b[31mError: ${message}\x1b[0m`);
    if (result?.taskFolder) console.error(`Task Folder: ${result.taskFolder}`);
  }
  process.exitCode = 1;
}

function printableValue(value) {
  return typeof value === 'object' ? JSON.stringify(value) : String(value);
}

async function main() {
  let values;
  try {
    ({ values } = parseArgs({
      options: {
        url: { type: 'string', short: 'u', default: '' },
        lang: { type: 'string', short: 'l', default: 'auto' },
        'output-dir': { type: 'string', default: './tasks' },
        timeout: { type: 'string', default: String(DEFAULT_TIMEOUT_MS) },
        retries: { type: 'string', default: String(DEFAULT_RETRIES) },
        json: { type: 'boolean', default: false },
        help: { type: 'boolean', short: 'h', default: false },
      },
      allowPositionals: false,
    }));
  } catch (error) {
    emitFailure({ json: process.argv.includes('--json'), code: 'INVALID_ARGUMENTS', message: error.message });
    return;
  }

  if (values.help) {
    printHelp();
    return;
  }

  const json = values.json;
  const rawOutputDir = values['output-dir'].trim();
  let profile;
  let language;
  let timeout;
  let retries;
  try {
    profile = normalizeProfileUrl(values.url);
    language = detectLanguage(values.lang);
    if (!rawOutputDir) throw new Error('--output-dir cannot be blank');
    timeout = parseInteger(values.timeout, '--timeout', 1000, 3600000);
    retries = parseInteger(values.retries, '--retries', 0, 3);
  } catch (error) {
    emitFailure({ json, code: 'VALIDATION_ERROR', message: error.message });
    return;
  }

  const outputDir = resolve(rawOutputDir);
  try {
    mkdirSync(outputDir, { recursive: true });
  } catch (error) {
    emitFailure({ json, code: 'OUTPUT_DIR_ERROR', message: `Cannot create output directory ${outputDir}: ${error.message}`, outputDir });
    return;
  }

  const apiKey = process.env.UNITYCLAW_KEY;
  if (!apiKey) {
    emitFailure({ json, code: 'MISSING_API_KEY', message: 'UNITYCLAW_KEY is not configured. Get an API key at https://unityclaw.com/.', outputDir });
    return;
  }

  let UnityClawClient;
  let SDK_VERSION;
  let checkMinVersion;
  try {
    const sdk = await import('@unityclaw/sdk');
    UnityClawClient = sdk.UnityClawClient;
    SDK_VERSION = sdk.SDK_VERSION;
    checkMinVersion = sdk.checkMinVersion;
  } catch {
    emitFailure({ json, code: 'SDK_NOT_FOUND', message: '@unityclaw/sdk is not installed. Run: npm install @unityclaw/sdk', outputDir });
    return;
  }

  const versionCheck = checkMinVersion(MIN_SDK_VERSION);
  if (!versionCheck.valid) {
    emitFailure({ json, code: 'SDK_VERSION_ERROR', message: versionCheck.message, outputDir });
    return;
  }

  if (!json) {
    console.log(`\x1b[36mUnityClaw Media KOL Profile v${SKILL_VERSION}\x1b[0m\n`);
    console.log(`\x1b[32m✓ SDK version ${SDK_VERSION} (minimum: ${MIN_SDK_VERSION})\x1b[0m`);
    console.log('\x1b[36mParameters:\x1b[0m');
    console.log(`  URL: ${profile.url}`);
    console.log(`  Platform: ${profile.platform}`);
    console.log(`  Output Labels: ${language}`);
    console.log(`  Output Directory: ${outputDir}`);
    console.log(`  Timeout: ${timeout}ms`);
    console.log(`  Retries: ${retries}\n`);
  }

  const client = new UnityClawClient({ apiKey, taskDir: outputDir, timeout });
  const maximumAttempts = retries + 1;
  let lastResult;
  let lastError;

  for (let attempt = 1; attempt <= maximumAttempts; attempt += 1) {
    if (!json) console.log(`\x1b[33mFetching KOL profile (attempt ${attempt}/${maximumAttempts})...\x1b[0m`);
    try {
      const result = await client.media.userInfo({ link: [{ link: profile.url }] });
      lastResult = result;

      if (result.success && result.response?.data) {
        try {
          const validated = validateProfileData(result.response.data, profile.platform);
          const fields = localizeFields(validated.data, language);
          const artifact = {
            sourceUrl: profile.url,
            platform: profile.platform,
            language,
            data: validated.data,
            fields,
            missingCoreFields: validated.missingCoreFields,
            warnings: validated.warnings,
          };
          const saved = saveProfileArtifact(result.taskFolder, artifact);
          const payload = {
            success: true,
            attempts: attempt,
            taskId: result.taskId,
            taskFolder: result.taskFolder,
            duration: result.duration,
            outputDir,
            resultPath: saved.resultPath,
            resultBytes: saved.resultBytes,
            ...artifact,
          };

          if (json) console.log(JSON.stringify(payload));
          else {
            console.log(`\n\x1b[36mTask ID: ${result.taskId}\x1b[0m`);
            console.log(`\x1b[36mTask Folder: ${result.taskFolder}\x1b[0m`);
            console.log(`\x1b[36mDuration: ${result.duration}ms\x1b[0m`);
            console.log(`\x1b[36mResult File: ${saved.resultPath}\x1b[0m`);
            console.log('\n\x1b[32m✓ KOL profile retrieved:\x1b[0m');
            fields.forEach((field) => console.log(`  ${field.label} (${field.key}): ${printableValue(field.value)}`));
            validated.warnings.forEach((warning) => console.warn(`\x1b[33mWarning: ${warning}\x1b[0m`));
          }
          return;
        } catch (error) {
          emitFailure({ json, code: 'OUTPUT_VALIDATION_ERROR', message: error.message, attempts: attempt, outputDir, result });
          return;
        }
      }

      lastError = new Error(getFailureMessage(result));
      lastError.details = result;
    } catch (error) {
      lastError = error;
    }

    const retryable = isRetryable(lastError) || isRetryable(lastResult);
    if (!retryable || attempt === maximumAttempts) {
      emitFailure({
        json,
        code: retryable ? 'TRANSIENT_ERROR' : 'PROFILE_ERROR',
        message: lastError?.message || 'KOL profile retrieval failed',
        retryable,
        attempts: attempt,
        outputDir,
        result: lastResult,
      });
      return;
    }

    const delay = 1000 * attempt;
    if (!json) console.warn(`\x1b[33mTransient failure; retrying in ${delay}ms...\x1b[0m`);
    await sleep(delay);
  }
}

const isDirectExecution = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isDirectExecution) {
  main().catch((error) => {
    emitFailure({ json: process.argv.includes('--json'), code: 'UNEXPECTED_ERROR', message: error.message, retryable: isRetryable(error) });
  });
}

export { detectLanguage, detectPlatform, localizeFields, normalizeProfileUrl, saveProfileArtifact, validateProfileData };
