import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { spawnSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";

// The Claude Code hooks are the one source of truth for what is blocked; this feeds them the same
// PreToolUse JSON so pi sessions get the same rules without a second copy of the patterns.
const hooksDir = process.env.HOUSE_GUARD_HOOKS_DIR ?? join(homedir(), ".claude", "hooks");
const hooks = ["block-dangerous-shell.sh", "block-sensitive-commit.sh"].map((f) => join(hooksDir, f));

export function check(command: string, cwd: string): string | undefined {
	const input = JSON.stringify({ tool_name: "Bash", tool_input: { command }, cwd });
	for (const hook of hooks) {
		const r = spawnSync(hook, { input, encoding: "utf8", timeout: 15_000 });
		if (r.status === 0) continue;
		if (r.status === 2) return r.stderr.trim();
		// Fail closed: a guard that cannot run must not wave commands through.
		const why = r.error?.message ?? (r.stderr.trim() || `exit ${r.status ?? r.signal}`);
		return `BLOCKED: house-guard could not run ${hook} (${why}).\nCommand: ${command}`;
	}
	return undefined;
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		if (event.toolName !== "bash") return undefined;
		const reason = check(String(event.input.command ?? ""), ctx.cwd);
		return reason ? { block: true, reason } : undefined;
	});
}
