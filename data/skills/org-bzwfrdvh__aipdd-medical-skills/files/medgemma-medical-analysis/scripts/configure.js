import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";

const text = await readStdin();
let input;
try { input = JSON.parse(text); } catch { fail("stdin must contain valid JSON"); }
if (!input.baseUrl || !input.apiKey) fail("baseUrl and apiKey are required");
const target = process.env.NEWAPI_CONFIG || defaultConfigPath("medgemma-medical-analysis");
await fs.mkdir(path.dirname(target), { recursive: true });
const config = { baseUrl: String(input.baseUrl).replace(/\/$/, ""), apiKey: String(input.apiKey) };
if (input.model !== undefined && input.model !== null) config.model = String(input.model);
await fs.writeFile(target, `${JSON.stringify(config, null, 2)}
`, { encoding: "utf8" });
console.log(JSON.stringify({ success: true, configPath: target, message: "configuration saved" }));

function defaultConfigPath(skillName) {
  const home = process.env.WORKBUDDY_HOME || process.env.OPENCLAW_HOME || path.join(os.homedir(), ".workbuddy");
  const stateDir = process.env.OPENCLAW_STATE_DIR || home;
  return stateDir + "/skills/" + skillName + "/config.json";
}
async function readStdin() { const chunks = []; for await (const chunk of process.stdin) chunks.push(chunk); return Buffer.concat(chunks).toString("utf8"); }
function fail(message) { console.error(JSON.stringify({ success: false, error: message })); process.exit(1); }
