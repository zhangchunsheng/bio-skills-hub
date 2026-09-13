#!/usr/bin/env node
import { existsSync, mkdirSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const SKILL_NAME = "unityclaw-image2-medical-education-poster";
const SKILL_VERSION = '1.0.0';
const REQUIRED_SDK_VERSION = '1.1.0';
const MODEL_NAME = "Image2";
const DEFAULT_ASPECT_RATIO = "4:5";
const DEFAULT_SIZE = "2K";
const DEFAULT_TIMEOUT_MS = 900000;
const DEFAULT_RETRIES = 1;
const SIZE_OPTIONS = ['1K', '2K', '4K'];

const OUTPUT_FORMAT_OPTIONS = ['png', 'jpeg', 'webp'];
const ASPECT_RATIO_OPTIONS = ['1:1', '9:16', '16:9', '4:3', '3:4', '3:2', '2:3', '5:4', '4:5', '21:9'];

function printHelp() {
  console.log(`
Image2 医疗科普海报生成 v${SKILL_VERSION}

Usage:
  node scripts/generate.js --prompt "..." [options]

Options:
  --prompt, -p          Image prompt (required)
  --attachment, -a      Reference image URL or local file; repeat as needed
  --aspect-ratio, -r    Output ratio (default: ${DEFAULT_ASPECT_RATIO})
  --size, -s            1K, 2K, 4K (default: ${DEFAULT_SIZE})

  --output-format, -f   png, jpeg, webp (default: png)
  --output-dir          Download directory (default: ./tasks)
  --timeout             Timeout in milliseconds (default: ${DEFAULT_TIMEOUT_MS})
  --retries             Transient retry count, 0-3 (default: ${DEFAULT_RETRIES})
  --json                Emit one JSON object
  --help, -h            Show help
`);
}

function parseInteger(value, name, minimum, maximum) {
  if (!/^\d+$/.test(value)) throw new Error(`${name} must be an integer`);
  const number = Number(value);
  if (number < minimum || number > maximum) throw new Error(`${name} must be between ${minimum} and ${maximum}`);
  return number;
}

function normalizeAttachments(inputs) {
  return inputs.flatMap((input) => String(input).split(',')).map((item) => item.trim()).filter(Boolean).map((value) => {
    if (/^https?:\/\//i.test(value)) return { tmp_url: value };
    const path = resolve(value);
    if (!existsSync(path) || !statSync(path).isFile()) throw new Error(`Attachment not found: ${path}`);
    return { path };
  });
}

function errorText(value) {
  try { return typeof value === 'string' ? value : JSON.stringify(value); } catch { return String(value); }
}

function isRetryable(value) {
  return /ECONNRESET|ECONNABORTED|ETIMEDOUT|ENOTFOUND|EAI_AGAIN|socket hang up|network|timed?\s*out|\b429\b|\b502\b|\b503\b|\b504\b|temporar(?:y|ily) unavailable/i.test(errorText(value));
}

function validateFiles(items) {
  if (!Array.isArray(items) || items.length === 0) throw new Error('Generation returned no files');
  return items.map((item, index) => {
    if (!item.localPath) throw new Error(`Generated image ${index + 1} has no localPath`);
    const localPath = resolve(item.localPath);
    if (!existsSync(localPath) || !statSync(localPath).isFile()) throw new Error(`Generated image was not downloaded: ${localPath}`);
    const bytes = statSync(localPath).size;
    if (bytes <= 0) throw new Error(`Generated image is empty: ${localPath}`);
    return { name: item.name, contentType: item.contentType, localPath, bytes, temporaryUrl: item.content };
  });
}

function emitFailure({ json, code, message, retryable = false, attempts = 0, outputDir, result }) {
  const payload = { success: false, error: { code, message, retryable }, attempts, outputDir, taskId: result?.taskId, taskFolder: result?.taskFolder, logs: result?.logs };
  if (json) console.log(JSON.stringify(payload));
  else console.error(`Error: ${message}`);
  process.exitCode = 1;
}

function sleep(ms) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, ms));
}

async function main() {
  let values;
  try {
    ({ values } = parseArgs({
      options: {
        prompt: { type: 'string', short: 'p', default: '' },
        attachment: { type: 'string', short: 'a', multiple: true, default: [] },
        'aspect-ratio': { type: 'string', short: 'r', default: DEFAULT_ASPECT_RATIO },
        size: { type: 'string', short: 's', default: DEFAULT_SIZE },

        'output-format': { type: 'string', short: 'f', default: 'png' },
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

  if (values.help) { printHelp(); return; }
  const json = values.json;
  const prompt = values.prompt.trim();
  const aspectRatio = values['aspect-ratio'].trim();
  const size = values.size.trim();

  const outputFormat = values['output-format'].trim();
  const outputDir = resolve(values['output-dir'].trim());
  let timeout;
  let retries;
  let attachments;
  try {
    if (!prompt) throw new Error('--prompt is required and cannot be blank');
    if (!ASPECT_RATIO_OPTIONS.includes(aspectRatio)) throw new Error(`Invalid aspect ratio "${aspectRatio}"`);
    if (!SIZE_OPTIONS.includes(size)) throw new Error(`Invalid size "${size}"`);

    if (!OUTPUT_FORMAT_OPTIONS.includes(outputFormat)) throw new Error(`Invalid output format "${outputFormat}"`);
    timeout = parseInteger(values.timeout, '--timeout', 1000, 3600000);
    retries = parseInteger(values.retries, '--retries', 0, 3);
    attachments = normalizeAttachments(values.attachment);
    mkdirSync(outputDir, { recursive: true });
  } catch (error) {
    emitFailure({ json, code: 'VALIDATION_ERROR', message: error.message, outputDir });
    return;
  }

  const apiKey = process.env.UNITYCLAW_KEY;
  if (!apiKey) {
    emitFailure({ json, code: 'MISSING_API_KEY', message: `UNITYCLAW_KEY is not configured. Get an API key at https://unityclaw.com?utm_source=${SKILL_NAME}. Then set UNITYCLAW_KEY and retry.`, outputDir });
    return;
  }

  let UnityClawClient;
  let SDK_VERSION;
  try {
    const sdk = await import('fieldkit-sdk');
    UnityClawClient = sdk.UnityClawClient;
    SDK_VERSION = sdk.SDK_VERSION;
  } catch {
    emitFailure({ json, code: 'SDK_NOT_FOUND', message: 'fieldkit-sdk is not installed. Run: npm install fieldkit-sdk@1.1.0', outputDir });
    return;
  }
  if (SDK_VERSION !== REQUIRED_SDK_VERSION) {
    emitFailure({ json, code: 'SDK_VERSION_ERROR', message: `Installed SDK version ${SDK_VERSION} does not match required ${REQUIRED_SDK_VERSION}. Run: npm install fieldkit-sdk@${REQUIRED_SDK_VERSION}`, outputDir });
    return;
  }

  const client = new UnityClawClient({ apiKey, taskDir: outputDir, timeout, source: "unityclaw-image2-medical-education-poster" });
  const common = { prompt, attachment: attachments.length ? attachments : undefined, aspect_ratio: aspectRatio, size };
  let lastResult;
  let lastError;
  const maximumAttempts = retries + 1;
  for (let attempt = 1; attempt <= maximumAttempts; attempt += 1) {
    try {
      const result = await client.image.gptImage({ ...common, output_format: outputFormat });
      lastResult = result;
      const data = result.response?.data;
      if (result.success && Array.isArray(data) && data.length > 0) {
        let files;
        try { files = validateFiles(data); }
        catch (error) {
          emitFailure({ json, code: 'OUTPUT_VALIDATION_ERROR', message: error.message, attempts: attempt, outputDir, result });
          return;
        }
        const payload = { success: true, model: MODEL_NAME, aspectRatio, size, outputFormat, attempts: attempt, taskId: result.taskId, taskFolder: result.taskFolder, duration: result.duration, outputDir, files };
        if (json) console.log(JSON.stringify(payload));
        else {
          console.log(`Generated ${files.length} image(s) with ${MODEL_NAME}`);
          files.forEach((file) => console.log(file.localPath));
        }
        return;
      }
      lastError = new Error(result.response?.msg || 'Image generation failed');
    } catch (error) {
      lastError = error;
    }
    const retryable = isRetryable(lastError) || isRetryable(lastResult);
    if (!retryable || attempt === maximumAttempts) {
      emitFailure({ json, code: retryable ? 'TRANSIENT_ERROR' : 'GENERATION_ERROR', message: lastError?.message || 'Image generation failed', retryable, attempts: attempt, outputDir, result: lastResult });
      return;
    }
    await sleep(1000 * attempt);
  }
}

const isDirectExecution = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isDirectExecution) {
  main().catch((error) => emitFailure({ json: process.argv.includes('--json'), code: 'UNEXPECTED_ERROR', message: error.message, retryable: isRetryable(error) }));
}
