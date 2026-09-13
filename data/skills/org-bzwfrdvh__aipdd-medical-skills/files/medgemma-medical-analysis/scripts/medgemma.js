import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const DEFAULT_MODEL = "medgemma-1.5-4b-it";
const MAX_IMAGES = 4;
const REQUEST_TIMEOUT_MS = 120000;
const MIME_BY_EXT = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp", gif: "image/gif", bmp: "image/bmp", tif: "image/tiff", tiff: "image/tiff" };

const TASK_LABELS = {
  "cxr": "胸片解读", "cxr-longitudinal": "纵向胸片对比", "radiology-2d": "通用 2D 影像解读",
  "pathology": "病理切片分析", "derm": "皮肤影像分析", "eyefundus": "眼底影像分析",
  "anatomy-loc": "解剖定位", "lab-report": "化验单结构化提取", "ehr": "EHR/病历解读",
  "clinical-reasoning": "临床推理", "report-generation": "医学报告生成"
};

const SYSTEM_PROMPTS = {
  "cxr": "You are an expert radiologist. Analyze the provided chest X-ray image systematically: image quality, cardiomediastinal silhouette, lungs and pleura, bones, and any abnormalities. Report findings and impression in a structured way.",
  "cxr-longitudinal": "You are an expert radiologist. The images are ordered chronologically (first image is the current study, subsequent images are prior studies). Compare them and report changes, progression, improvement, or new findings.",
  "radiology-2d": "You are an expert radiologist. Analyze the provided medical image (CT slice, MRI, ultrasound, or other 2D modality) and describe findings systematically, then give an impression.",
  "pathology": "You are an expert pathologist. Analyze the provided histopathology image(s) (whole-slide patches or stained sections). Describe tissue architecture, cell morphology, grading features if visible, and provide a differential interpretation.",
  "derm": "You are an expert dermatologist. Analyze the skin lesion image(s). Describe morphology, distribution, and provide a differential diagnosis with caution flags for concerning features.",
  "eyefundus": "You are an expert ophthalmologist. Analyze the fundus image(s). Describe optic disc, macula, vessels, and any lesions; assess diabetic retinopathy severity if applicable.",
  "anatomy-loc": "You are an expert radiologist specializing in anatomical localization. Identify anatomical structures and findings in the chest X-ray and output them as bounding boxes in the format: [x1, y1, x2, y2, label] with coordinates normalized to 0-1000. List each finding on its own line.",
  "lab-report": "You are a clinical laboratory expert. Extract structured data from the lab report: test name, value, unit, reference range, and flag (high/low/normal). Output as a structured list, then summarize clinically significant abnormalities.",
  "ehr": "You are a clinician expert in electronic health records. Interpret the provided EHR/medical record text: summarize the patient history, key abnormal findings, and current clinical status. Highlight inconsistencies or missing critical information.",
  "clinical-reasoning": "You are a clinical reasoning expert. Analyze the provided case, discuss differential diagnoses with supporting reasoning, suggest relevant investigations, and note red flags. Do not prescribe treatment.",
  "report-generation": "You are a medical report writer. Generate a structured medical report from the provided image(s) and context, following standard report sections: findings, impression, and recommendations."
};

for (const key of Object.keys(SYSTEM_PROMPTS)) {
  SYSTEM_PROMPTS[key] += " Respond in the same language as the user's question. Always end with the disclaimer: this analysis is for reference, research, and educational purposes only and does not constitute a clinical diagnosis; final diagnosis should be made by a licensed physician.";
}

const args = parseArgs(process.argv.slice(2));
const task = args.task || "clinical-reasoning";
if (!SYSTEM_PROMPTS[task]) fail("unknown task: " + task + " (supported: " + Object.keys(SYSTEM_PROMPTS).join(", ") + ")");

const config = await loadConfig();
let baseUrl = String(config.baseUrl || "").replace(/\/$/, "");
if (!/\/v\d+$/.test(baseUrl)) baseUrl = baseUrl + "/v1";
const apiKey = config.apiKey || process.env.NEWAPI_API_KEY || "";
if (!baseUrl) fail("missing base URL");
if (!apiKey) fail("missing API key");

if (args.ping) {
  const models = await ping(baseUrl, apiKey);
  console.log(JSON.stringify({ success: true, status: "ok", baseUrl, models }));
  process.exit(0);
}

const model = args.model || config.model || process.env.MEDGEMMA_MODEL || DEFAULT_MODEL;
const text = await readTextInput(args);
const images = await resolveImages(args.image);

if (!text && images.length === 0) fail("provide --text, --text-file, or --image");

const userContent = [];
for (const image of images) userContent.push({ type: "image_url", image_url: { url: image } });
const instruction = buildInstruction(task, text, args.question, args.context);
userContent.push({ type: "text", text: instruction });

const body = {
  model,
  messages: [
    { role: "system", content: SYSTEM_PROMPTS[task] },
    { role: "user", content: userContent }
  ],
  max_tokens: Number(args.max_tokens || 2048),
  temperature: Number(args.temperature ?? 0.1)
};

const data = await chat(baseUrl, apiKey, body);
const content = data.choices?.[0]?.message?.content ?? "";
if (!content) fail("empty model response");

const result = { success: true, status: "completed", task, model, content, usage: data.usage || null };
if (args.output) {
  const report = await renderReport(task, content, { model, question: args.question, context: args.context, imageCount: images.length });
  await fs.writeFile(args.output, report, "utf8");
  result.outputPath = args.output;
}
console.log(JSON.stringify(result));

function buildInstruction(kind, text, question, context) {
  const parts = [];
  if (text) parts.push("Input text:\n" + text);
  if (context) parts.push("Clinical context:\n" + context);
  if (question) parts.push("Question: " + question);
  if (parts.length === 0) parts.push("Provide your analysis of the input image(s).");
  return parts.join("\n\n");
}

async function readTextInput(args) {
  if (args.text) return String(args.text);
  if (args.text_file) {
    try { return await fs.readFile(args.text_file, "utf8"); } catch (error) { fail("cannot read text file: " + error.message); }
  }
  return "";
}

async function resolveImages(value) {
  if (!value) return [];
  const items = String(value).split(",").map(item => item.trim()).filter(Boolean);
  if (items.length > MAX_IMAGES) fail("too many images (max " + MAX_IMAGES + ")");
  const resolved = [];
  for (const item of items) {
    if (/^https?:\/\//i.test(item)) {
      if (!item.startsWith("https://")) fail("remote images must use HTTPS URLs");
      resolved.push(item);
    } else {
      resolved.push(await toDataUri(item));
    }
  }
  return resolved;
}

async function toDataUri(filePath) {
  let data;
  try { data = await fs.readFile(filePath); } catch (error) { fail("cannot read image file: " + error.message); }
  const ext = path.extname(filePath).slice(1).toLowerCase();
  const mime = MIME_BY_EXT[ext] || "image/png";
  return "data:" + mime + ";base64," + data.toString("base64");
}

async function chat(baseUrl, key, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(baseUrl + "/chat/completions", {
      method: "POST",
      headers: { "authorization": "Bearer " + key, "content-type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal
    });
  } catch (error) {
    clearTimeout(timer);
    fail("network error: " + (error.name === "AbortError" ? "request timed out after " + REQUEST_TIMEOUT_MS / 1000 + "s" : error.message));
  }
  clearTimeout(timer);
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!response.ok) {
    const hint = response.status === 404 ? " (model not found; run with --ping to list available models)" : "";
    fail("HTTP error: " + response.status + (data.error?.message ? ": " + data.error.message : "") + hint);
  }
  return data;
}

async function ping(baseUrl, key) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(baseUrl + "/models", {
      headers: { "authorization": "Bearer " + key },
      signal: controller.signal
    });
  } catch (error) {
    clearTimeout(timer);
    fail("network error: " + (error.name === "AbortError" ? "request timed out after " + REQUEST_TIMEOUT_MS / 1000 + "s" : error.message));
  }
  clearTimeout(timer);
  const text = await response.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!response.ok) fail("HTTP error: " + response.status + (data.error?.message ? ": " + data.error.message : ""));
  return data;
}

async function renderReport(kind, content, meta) {
  const templatePath = new URL("../assets/medical-report-template.md", import.meta.url);
  let template = "";
  try { template = await fs.readFile(templatePath, "utf8"); } catch (error) { template = "# Medical Analysis Report\n\n"; }
  return template
    .replaceAll("{{TASK}}", TASK_LABELS[kind] || kind)
    .replaceAll("{{MODEL}}", meta.model || DEFAULT_MODEL)
    .replaceAll("{{QUESTION}}", meta.question || "—")
    .replaceAll("{{CONTEXT}}", meta.context || "—")
    .replaceAll("{{IMAGE_COUNT}}", String(meta.imageCount))
    .replaceAll("{{ANALYSIS}}", content);
}

function parseArgs(values) {
  const output = {};
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith("--")) continue;
    const key = value.slice(2).replaceAll("-", "_");
    output[key] = values[index + 1]?.startsWith("--") ? true : values[index + 1] ?? true;
    if (output[key] !== true) index += 1;
  }
  return output;
}

async function loadConfig() {
  const configPath = process.env.NEWAPI_CONFIG || defaultConfigPath("medgemma-medical-analysis");
  let config = {};
  try { config = JSON.parse(await fs.readFile(configPath, "utf8")); } catch (error) {}
  return {
    baseUrl: config.baseUrl || process.env.NEWAPI_BASE_URL,
    apiKey: config.apiKey || process.env.NEWAPI_API_KEY,
    model: config.model,
  };
}

function defaultConfigPath(skillName) {
  const home = process.env.WORKBUDDY_HOME || process.env.OPENCLAW_HOME || path.join(os.homedir(), ".workbuddy");
  const stateDir = process.env.OPENCLAW_STATE_DIR || home;
  return stateDir + "/skills/" + skillName + "/config.json";
}

function fail(message) { console.error(JSON.stringify({ success: false, error: message })); process.exit(1); }
