// Run: node pi/house-guard/test.ts  (Node >= 23 strips the types). Exits 1 on any wrong verdict.
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { check } from "./index.ts";

const repo = mkdtempSync(join(process.env.TMPDIR ?? tmpdir(), "house-guard-"));
const git = (...a: string[]) => execFileSync("git", ["-C", repo, ...a], { stdio: "pipe" });
git("init", "-q");
git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base");
const stage = (name: string, body: string) => {
	git("reset", "-q");
	writeFileSync(join(repo, name), body);
	git("add", name);
};

let failed = 0;
const expect = (want: "block" | "allow", command: string, cwd = "/") => {
	const got = check(command, cwd) ? "block" : "allow";
	if (got !== want) failed++;
	console.log(`${got === want ? "ok  " : "FAIL"} ${want.padEnd(5)} ${command}`);
};

expect("block", "git push origin main");
expect("block", "cd /tmp && git push");
expect("block", "git reset --hard HEAD~1");
expect("block", "git clean -fdx");
expect("block", "git branch -D topic");
expect("block", "rm -rf build");
expect("allow", "/usr/bin/rm -f build/x.o");
expect("allow", "git status && ls -la");

stage("ok.txt", "hello\n");
expect("allow", `cd ${repo} && git commit -m ok`);
// Planted values are split so this file itself passes the commit guard.
stage("key.pem", "-----BEGIN OPENSSH PRIVATE" + " KEY-----\nabc\n");
expect("block", `cd ${repo} && git commit -m key`);
expect("block", `git -C ${repo} commit -m key`);
expect("block", "git commit -m key", repo);
stage("conf.env", "API" + "_KEY=" + "x".repeat(24) + "\n");
expect("block", `cd ${repo} && git commit -m secret`);
stage("notes.md", "see ~/" + ".ssh/github_key\n");
expect("block", `cd ${repo} && git commit -m ssh`);
stage("notes.md", "copy from /mnt/c/" + "Users/someone/Desktop\n");
expect("block", `cd ${repo} && git commit -m winpath`);

const closed = spawnSync(process.execPath, ["-e", `import("${join(import.meta.dirname, "index.ts")}").then(m => process.exit(m.check("ls", "/") ? 0 : 1))`], {
	env: { ...process.env, HOUSE_GUARD_HOOKS_DIR: "/nonexistent" },
});
if (closed.status !== 0) failed++;
console.log(`${closed.status === 0 ? "ok  " : "FAIL"} block ls with hooks missing (fail closed)`);

execFileSync("/usr/bin/rm", ["-rf", repo]);
console.log(failed ? `${failed} FAILED` : "all ok");
process.exit(failed ? 1 : 0);
