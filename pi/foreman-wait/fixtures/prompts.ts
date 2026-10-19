import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerCommand("wait-confirm", {
		description: "Live-check fixture: show a confirmation without taking any action.",
		handler: async (_args, ctx) => { await ctx.ui.confirm("Allow fixture?", "No action will be taken."); },
	});
	pi.registerCommand("wait-input", {
		description: "Live-check fixture: show an input dialog.",
		handler: async (_args, ctx) => { await ctx.ui.input("Which fixture value?"); },
	});
}
