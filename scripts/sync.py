#!/usr/bin/env python3
"""Back-import report: what changed upstream since each pin, per house skill.

Fetches each source, diffs pin..origin default branch, and writes reports/YYYY-MM-DD.md:
  adopt        -> changed upstream files and a proposed pin bump (re-vendor, then --bump)
  adapt/merge  -> per-skill digest (diffstat + capped diff of the referenced paths)
  own          -> skipped
  unmapped     -> upstream skill dirs no [[skill]]/[[drop]] covers (check.py's rule, at the new head)
  vanished     -> refs that no longer exist at the new head

--file-beads files one bead per candidate (label `sync`, parent = the open epic labelled `sync`, if any).
--bump SOURCE COMMIT rewrites that source's pin in the catalog and exits.
"""
import argparse, datetime, json, os, re, subprocess, sys, tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import ROOT, ref_covers, unmapped, upstream_skill_dirs  # noqa: E402


def git(root, *args, check=True):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)} in {root} failed: {r.stderr.strip()}")
    return r.stdout


def default_head(root):
    ref = git(root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False).strip()
    if not ref:
        git(root, "remote", "set-head", "origin", "--auto")
        ref = git(root, "symbolic-ref", "refs/remotes/origin/HEAD").strip()
    return ref.removeprefix("refs/remotes/"), git(root, "rev-parse", ref).strip()


def bump(catalog_path, source, commit):
    cat = tomllib.load(open(catalog_path, "rb"))
    if source not in cat.get("sources", {}):
        raise SystemExit(f"unknown source '{source}'")
    root = os.path.expanduser(cat["sources"][source]["path"])
    full = git(root, "rev-parse", "--verify", f"{commit}^{{commit}}").strip()
    text = open(catalog_path, encoding="utf-8").read()
    block = re.search(rf"(?ms)^\[sources\.{re.escape(source)}\]\n.*?(?=^\[|\Z)", text)
    new_block, n = re.subn(r'(?m)^pin = "[0-9a-f]+"', f'pin = "{full}"', block.group(0), count=1)
    if n != 1:
        raise SystemExit(f"no pin line in [sources.{source}]")
    open(catalog_path, "w", encoding="utf-8").write(text[: block.start()] + new_block + text[block.end():])
    print(f"{source}: pin {cat['sources'][source]['pin'][:7]} -> {full[:7]}")


def capped(text, cap):
    lines = text.splitlines()
    if len(lines) <= cap:
        return text.rstrip("\n")
    return "\n".join(lines[:cap]) + f"\n... [truncated: {len(lines) - cap} more lines]"


def scan(catalog, args):
    """Return (report sections, bead candidates)."""
    out, candidates = [], []
    for sname, src in catalog.get("sources", {}).items():
        root = os.path.expanduser(src["path"])
        pin = src["pin"]
        if not args.no_fetch:
            git(root, "fetch", "--quiet", "origin")
        branch, head = default_head(root)
        scope = [src["scope"]] if src.get("scope") else []
        log = git(root, "log", "--oneline", "--no-decorate", f"{pin}..{head}", "--", *scope).strip()
        out.append(f"## {sname}: {pin[:7]}..{head[:7]} ({branch})\n")
        refs = {}  # skill name -> its refs into this source
        for e in catalog.get("skill", []):
            r = [x.partition(":")[2] for x in e.get("from", []) if x.partition(":")[0] == sname]
            if r and e.get("mode") != "own":
                refs[e["name"]] = (e["mode"], r)

        changed = [] if pin == head else git(root, "diff", "--name-only", pin, head, "--", *scope).split()
        if not changed:
            out.append("No upstream changes since the pin.\n")
        else:
            n = len(log.splitlines())
            out.append(f"{n} commits, {len(changed)} files changed.\n\n```\n{capped(log, 40)}\n```\n")
            touched_any = set()
            for name, (mode, pats) in refs.items():
                files = [f for f in changed if any(ref_covers(p, f) for p in pats)]
                if not files:
                    continue
                touched_any.update(files)
                stat = git(root, "diff", "--stat", pin, head, "--", *files).rstrip()
                if mode == "adopt":
                    out.append(f"### {name} (adopt): re-vendor, then `sync.py --bump {sname} {head[:12]}`\n")
                    out.append(f"```\n{stat}\n```\n")
                    candidates.append((f"sync: re-vendor adopted {name} from {sname}@{head[:7]}",
                                       f"Upstream changed {', '.join(files)} ({pin[:7]}..{head[:7]}). "
                                       f"Re-vendor byte-identical, keep the provenance comment, then bump the pin."))
                else:
                    diff = git(root, "diff", pin, head, "--", *files)
                    out.append(f"### {name} ({mode}): digest\n")
                    out.append(f"```\n{stat}\n```\n\n```diff\n{capped(diff, args.cap)}\n```\n")
                    candidates.append((f"sync: review upstream changes for {name} ({mode}, {sname}@{head[:7]})",
                                       f"Upstream changed {', '.join(files)} ({pin[:7]}..{head[:7]}). "
                                       f"Compare against skills/{name}; propose adopt/adapt/drop per idea."))
            rest = [f for f in changed if f not in touched_any]
            if rest:
                out.append(f"{len(rest)} changed file(s) outside any house skill's refs (drops, docs, other).\n")

        tree = git(root, "ls-tree", "-r", "--name-only", head).split("\n")
        um = unmapped(catalog, sname, upstream_skill_dirs(src, files=tree))
        if um:
            out.append("### Unmapped upstream skills\n\n" + "\n".join(f"- `{sname}:{d}`" for d in um) + "\n")
            for d in um:
                candidates.append((f"sync: decide new upstream skill {sname}:{d}",
                                   f"{sname}:{d} at {head[:7]} has no [[skill]] or [[drop]] entry. Decide adopt/adapt/merge/drop."))
        all_refs = [(e.get("name"), x.partition(":")[2]) for e in catalog.get("skill", []) for x in e.get("from", [])
                    if x.partition(":")[0] == sname]
        all_refs += [("drop", d["from"].partition(":")[2]) for d in catalog.get("drop", [])
                     if d.get("from", "").partition(":")[0] == sname]
        gone = [(n, p) for n, p in all_refs if not any(ref_covers(p, f) for f in tree)]
        if gone:
            out.append("### Refs gone at the new head\n\n" + "\n".join(f"- {n}: `{sname}:{p}`" for n, p in gone) + "\n")
            for n, p in gone:
                candidates.append((f"sync: {sname}:{p} removed upstream ({n})",
                                   f"Ref {sname}:{p} used by {n} no longer exists at {head[:7]}; re-point or drop it."))
    return out, candidates


def file_beads(candidates, report):
    epics = json.loads(subprocess.run(["bd", "list", "--type", "epic", "--status", "open", "--label", "sync", "--json"],
                                      cwd=ROOT, capture_output=True, text=True, check=True).stdout or "[]")
    parent = epics[0]["id"] if epics else None
    for title, desc in candidates:
        cmd = ["bd", "create", title, "-d", f"{desc} Report: {report}", "-l", "sync", "--silent"] + (["--parent", parent] if parent else [])
        bead = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        print(f"filed {bead}: {title}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog", default=os.path.join(ROOT, "catalog.toml"))
    ap.add_argument("--out", default=os.path.join(ROOT, "reports"), help="report directory")
    ap.add_argument("--no-fetch", action="store_true", help="use the already-fetched origin refs")
    ap.add_argument("--cap", type=int, default=300, help="max diff lines per skill digest")
    ap.add_argument("--file-beads", action="store_true", help="file one bead per candidate (default off)")
    ap.add_argument("--bump", nargs=2, metavar=("SOURCE", "COMMIT"))
    args = ap.parse_args()

    if args.bump:
        bump(args.catalog, *args.bump)
        return 0
    catalog = tomllib.load(open(args.catalog, "rb"))
    sections, candidates = scan(catalog, args)
    today = datetime.date.today().isoformat()
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{today}.md")
    summary = f"{len(candidates)} candidate(s)." if candidates else "Nothing to do."
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Skills sync {today}\n\nCatalog: `{args.catalog}`. {summary}\n\n" + "\n".join(sections))
    print(f"wrote {path}: {summary}")
    for title, _ in candidates:
        print(f"  - {title}")
    if args.file_beads and candidates:
        file_beads(candidates, path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
