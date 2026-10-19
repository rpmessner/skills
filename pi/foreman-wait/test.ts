import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { execFileSync, spawn } from "node:child_process";
import { join } from "node:path";
import extension from "./index.ts";

const root = mkdtempSync(join(import.meta.dirname, ".test-"));
const bin = join(root, "bin");
mkdirSync(bin);
const log = join(root, "calls.jsonl");
writeFileSync(join(bin, "foreman"), `#!${process.execPath}\nimport {appendFileSync} from 'node:fs';\nappendFileSync(${JSON.stringify(log)}, JSON.stringify(process.argv.slice(2))+'\\n');\n`, { mode: 0o755 });
process.env.PATH = `${bin}:${process.env.PATH}`;
process.env.FOREMAN_TICKETS = "fm-1";
process.env.FOREMAN_SESSION = "test-window";
process.env.FOREMAN_ACTOR = "pi";
const calls = () => { try { return readFileSync(log, "utf8").trim().split("\n").filter(Boolean).map(JSON.parse); } catch { return []; } };
async function until(predicate: () => boolean, timeout = 2000) {
 const deadline = Date.now() + timeout;
 while (!predicate() && Date.now() < deadline) await new Promise(r => setTimeout(r, 10));
 assert.ok(predicate(), `condition not met; calls: ${JSON.stringify(calls())}`);
}
function harness() {
 const handlers = new Map<string, Function>();
 const warnings: string[] = [];
 extension({ on: (name, fn) => handlers.set(name, fn) } as any);
 const ctx = { cwd: root, ui: { notify: (text: string) => warnings.push(text) }, model: { provider: "test-provider" } };
 return { warnings, emit: (type: string, event = {}) => handlers.get(type)?.({ type, ...event }, ctx) };
}

test("settled question posts once and resumed activity clears through the CLI", async () => {
 const h = harness();
 h.emit("agent_start");
 h.emit("message_end", { message: { role: "assistant", stopReason: "stop", content: [{ type: "text", text: "Which option?" }] } });
 h.emit("agent_settled", { aborted: false });
 await until(() => calls().length === 1);
 assert.deepEqual(calls()[0], ["ask", "session_waiting", "fm-1", "--reason", "input", "--session", "test-window", "--window", "test-window", "--actor", "pi"]);
 h.emit("agent_settled", { aborted: false });
 h.emit("agent_start");
 await until(() => calls().length === 2);
 assert.deepEqual(calls()[1], ["session-hook", "UserPromptSubmit", "fm-1", "--session", "test-window", "--window", "test-window", "--actor", "pi"]);
});

test("confirmation stays pending during sibling tool activity and clears when answered", async () => {
 const start = calls().length;
 const h = harness();
 h.emit("ui_prompt_start", { kind: "confirm", reason: "ui_prompt" });
 await until(() => calls().length === start + 1);
 assert.equal(calls()[start][4], "permission");
 h.emit("tool_execution_start");
 h.emit("tool_execution_end");
 h.emit("agent_start");
 assert.equal(calls().length, start + 1);
 h.emit("ui_prompt_end", { kind: "confirm", reason: "ui_prompt" });
 await until(() => calls().length === start + 2);
 assert.equal(calls()[start + 1][1], "UserPromptSubmit");
});

test("input dialogs map to input without leaking question text", async () => {
 const start = calls().length;
 const h = harness();
 h.emit("ui_prompt_start", { kind: "input", title: "private question" });
 await until(() => calls().length === start + 1);
 assert.equal(calls()[start][4], "input");
 assert.ok(!JSON.stringify(calls()).includes("private question"));
 h.emit("ui_prompt_end", { kind: "input" });
 await until(() => calls().length === start + 2);
});

test("provider limit posts only after settlement and clears on the next turn", async () => {
 const start = calls().length;
 const h = harness();
 h.emit("message_end", { message: { role: "assistant", stopReason: "error", errorMessage: "Usage limit reached; resets 14:00", provider: "openai-codex" } });
 assert.equal(calls().length, start);
 h.emit("agent_settled", { aborted: false });
 await until(() => calls().length === start + 1);
 assert.equal(calls()[start][4], "usage_limit");
 assert.deepEqual(calls()[start].slice(-2), ["--provider", "openai-codex"]);
 h.emit("turn_start");
 await until(() => calls().length === start + 2);
 assert.equal(calls()[start + 1][1], "UserPromptSubmit");
});

test("shutdown clears pending waits", async () => {
 const start = calls().length;
 const h = harness();
 h.emit("ui_prompt_start", { kind: "select" });
 await until(() => calls().length === start + 1);
 h.emit("session_shutdown");
 await until(() => calls().length === start + 2);
 assert.equal(calls()[start + 1][1], "UserPromptSubmit");
});

test("ordinary completion, aborted runs and recovered limits do not post waits", async () => {
 const start = calls().length;
 const h = harness();
 h.emit("message_end", { message: { role: "assistant", stopReason: "error", errorMessage: "429 quota", provider: "test" } });
 h.emit("turn_start");
 h.emit("message_end", { message: { role: "assistant", stopReason: "stop", content: [{ type: "text", text: "Finished." }] } });
 h.emit("agent_settled", { aborted: false });
 h.emit("message_end", { message: { role: "assistant", stopReason: "error", errorMessage: "network disconnected" } });
 h.emit("agent_settled", { aborted: false });
 h.emit("message_end", { message: { role: "assistant", stopReason: "stop", content: [{ type: "text", text: "Question?" }] } });
 h.emit("agent_settled", { aborted: true });
 assert.equal(calls().length, start);
});

test("untracked sessions are inert and duplicate ticket IDs are delivered only once", async () => {
 const start = calls().length;
 process.env.FOREMAN_TICKETS = "";
 const inert = harness();
 inert.emit("ui_prompt_start", { kind: "confirm" });
 assert.equal(calls().length, start);
 assert.deepEqual(inert.warnings, []);
 process.env.FOREMAN_TICKETS = "fm-1 fm-2 fm-1";
 const h = harness();
 process.env.FOREMAN_TICKETS = "fm-1";
 h.emit("ui_prompt_start", { kind: "confirm" });
 await until(() => calls().length === start + 2);
 assert.deepEqual(calls().slice(start).map(c => c[2]), ["fm-1", "fm-2"]);
 h.emit("ui_prompt_end", { kind: "confirm" });
 await until(() => calls().length === start + 4);
 assert.deepEqual(calls().slice(start + 2).map(c => c.slice(0, 3)), [
  ["session-hook", "UserPromptSubmit", "fm-1"], ["session-hook", "UserPromptSubmit", "fm-2"],
 ]);
});

test("missing foreman warns once and never rejects a pi handler", async () => {
 const path = process.env.PATH;
 process.env.PATH = "/usr/bin:/bin";
 try {
  const h = harness();
  assert.equal(h.emit("ui_prompt_start", { kind: "confirm" }), undefined);
  await until(() => h.warnings.length === 1);
  h.emit("ui_prompt_end", { kind: "confirm" });
  h.emit("ui_prompt_start", { kind: "confirm" });
  h.emit("ui_prompt_end", { kind: "confirm" });
  await new Promise(r => setTimeout(r, 100));
  assert.equal(h.warnings.length, 1);
 } finally { process.env.PATH = path; }
});

test("hung CLI cannot block handlers and is killed within the bound", async () => {
 const original = readFileSync(join(bin, "foreman"), "utf8");
 const pidFile = join(root, "hung.pid");
 writeFileSync(join(bin, "foreman"), `#!${process.execPath}\nimport {writeFileSync} from 'node:fs';\nwriteFileSync(${JSON.stringify(pidFile)}, String(process.pid));\nsetInterval(()=>{},1000);\n`);
 try {
  const h = harness();
  const start = performance.now();
  assert.equal(h.emit("ui_prompt_start", { kind: "confirm" }), undefined);
  assert.ok(performance.now() - start < 100, "handler blocked on foreman");
  await until(() => h.warnings.length === 1, 6500);
  const pid = Number(readFileSync(pidFile, "utf8"));
  await until(() => { try { process.kill(pid, 0); return false; } catch { return true; } });
 } finally { writeFileSync(join(bin, "foreman"), original); }
});

test("CLI remains bounded even when pi exits during delivery", async () => {
 const original = readFileSync(join(bin, "foreman"), "utf8");
 const pidFile = join(root, "orphan.pid");
 writeFileSync(join(bin, "foreman"), `#!${process.execPath}\nimport {writeFileSync} from 'node:fs';\nwriteFileSync(${JSON.stringify(pidFile)}, String(process.pid));\nprocess.on('SIGTERM',()=>{}); setInterval(()=>{},1000);\n`);
 let pid: number | undefined;
 try {
  const child = spawn(process.execPath, ["--input-type=module", "-e", `
   import extension from ${JSON.stringify(join(import.meta.dirname, "index.ts"))};
   import {existsSync} from 'node:fs';
   const handlers = new Map();
   extension({on:(name,fn)=>handlers.set(name,fn)});
   handlers.get('ui_prompt_start')({kind:'confirm'}, {cwd:${JSON.stringify(root)}, ui:{notify(){}}});
   const timer = setInterval(()=>{if(existsSync(${JSON.stringify(pidFile)})) process.exit(0);}, 10);
  `], { stdio: "ignore" });
  await new Promise<void>((resolve, reject) => { child.on("exit", code => code === 0 ? resolve() : reject(new Error(`child exit ${code}`))); child.on("error", reject); });
  pid = Number(readFileSync(pidFile, "utf8"));
  await until(() => { try { process.kill(pid!, 0); return readFileSync(`/proc/${pid}/stat`, "utf8").includes(") Z "); } catch { return true; } }, 7500);
 } finally {
  if (pid) { try { process.kill(pid, "SIGKILL"); } catch {} }
  writeFileSync(join(bin, "foreman"), original);
 }
});

process.on("exit", () => execFileSync("/usr/bin/rm", ["-rf", root]));
