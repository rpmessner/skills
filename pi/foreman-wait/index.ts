import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import type { AssistantMessage } from "@earendil-works/pi-ai";
import { spawn } from "node:child_process";

type State = "working" | "question" | "input" | "permission" | "usage_limit";
type Event = "question" | "input" | "permission" | "usage_limit" | "activity" | "answered" | "shutdown";
type Reason = "input" | "permission" | "usage_limit";

const transitions: Record<State, Partial<Record<Event, State>>> = {
	working: { question: "question", input: "input", permission: "permission", usage_limit: "usage_limit" },
	question: { activity: "working", shutdown: "working", input: "input", permission: "permission" },
	input: { answered: "working", shutdown: "working" },
	permission: { answered: "working", shutdown: "working" },
	usage_limit: { activity: "working", shutdown: "working", input: "input", permission: "permission" },
};

function step(state: State, event: Event): { state: State; effects: (Reason | undefined)[] } {
	const next = transitions[state][event] ?? state;
	return {
		state: next,
		effects: next === state ? [] : [next === "working" ? undefined : next === "question" ? "input" : next],
	};
}

function deliver(args: string[], cwd: string, warn: () => void): Promise<void> {
	return new Promise(resolve => {
		let finished = false;
		const finish = (failed: boolean) => {
			if (finished) return;
			finished = true;
			if (failed) warn();
			resolve();
		};
		try {
			// GNU timeout owns the deadline even if pi exits before delivery completes.
			const child = spawn("timeout", ["-k", "1", "5", "foreman", ...args], {
				cwd, stdio: ["pipe", "ignore", "ignore"],
			});
			child.on("error", () => finish(true));
			child.on("exit", code => finish(code !== 0));
			child.stdin.on("error", () => {});
			child.stdin.end("{}");
			child.unref();
		} catch { finish(true); }
	});
}

export default function (pi: ExtensionAPI) {
	const tickets = [...new Set((process.env.FOREMAN_TICKETS ?? "").split(/\s+/).filter(Boolean))];
	const session = process.env.FOREMAN_SESSION;
	const actor = process.env.FOREMAN_ACTOR;
	if (!tickets.length || !session || !actor) return;
	const identity = ["--session", session, "--window", session, "--actor", actor];
	let state: State = "working";
	let desired: Reason | undefined;
	let sent: Reason | undefined;
	let sending = false;
	let warned = false;
	let last: AssistantMessage | undefined;
	let provider: string | undefined;

	const change = (event: Event, ctx: ExtensionContext) => {
		const result = step(state, event);
		state = result.state;
		for (const effect of result.effects) desired = effect;
		if (sending || desired === sent) return;
		const warn = () => {
			if (warned) return;
			warned = true;
			try {
				ctx.ui.notify("foreman-wait: foreman unavailable; continuing (pi-wait remains the fallback).", "warning");
			} catch {}
		};
		sending = true;
		void (async () => {
			try {
				while (desired !== sent) {
					const target = desired;
					for (const ticket of tickets) {
						const args = target
							? ["ask", "session_waiting", ticket, "--reason", target, ...identity,
								...(target === "usage_limit" && provider ? ["--provider", provider] : [])]
							: ["session-hook", "UserPromptSubmit", ticket, ...identity];
						await deliver(args, ctx.cwd, warn);
					}
					sent = target;
				}
			} catch { warn(); } finally { sending = false; }
		})();
	};

	pi.on("session_shutdown", (_event, ctx) => change("shutdown", ctx));
	pi.on("ui_prompt_start", (event, ctx) => change(event.kind === "confirm" ? "permission" : "input", ctx));
	pi.on("ui_prompt_end", (_event, ctx) => change("answered", ctx));
	pi.on("agent_start", (_event, ctx) => { last = undefined; change("activity", ctx); });
	pi.on("turn_start", (_event, ctx) => { last = undefined; change("activity", ctx); });
	pi.on("message_end", event => { if (event.message.role === "assistant") last = event.message; });
	pi.on("agent_settled", (event, ctx) => {
		if (event.aborted || !last) return;
		if (last.stopReason === "error") {
			if (/usage.limit|rate.limit|quota|\b429\b|extra.usage/i.test(last.errorMessage ?? "")) {
				provider = last.provider;
				change("usage_limit", ctx);
			}
		} else if (last.stopReason === "stop") {
			const text = last.content.filter(c => c.type === "text").map(c => c.text).join("\n");
			if (/\?["'”’`*_\)\]]*\s*$/.test(text)) change("question", ctx);
		}
	});
}
