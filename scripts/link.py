#!/usr/bin/env python3
"""Link exactly the house skills into each harness skill dir.

Dry run by default; pass --apply to change anything. Only symlinks are ever
created or removed; real directories in the harness dirs are left alone.
--replace-from PATH also removes links that point into PATH (an old skill repo).
"""
import argparse, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
TARGETS = [os.path.expanduser("~/.claude/skills"), os.path.expanduser("~/.agents/skills")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--replace-from", action="append", default=[])
    args = ap.parse_args()
    old_roots = [os.path.realpath(os.path.expanduser(p)) for p in args.replace_from]
    house = sorted(d for d in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))
    actions = []

    for target in TARGETS:
        os.makedirs(target, exist_ok=True)
        for name in house:
            link, src = os.path.join(target, name), os.path.join(SKILLS, name)
            if os.path.islink(link):
                if os.readlink(link) == src:
                    continue
                actions.append(("relink", link, src))
            elif os.path.exists(link):
                print(f"SKIP {link}: real directory, not touching")
                continue
            else:
                actions.append(("link", link, src))
        for entry in sorted(os.listdir(target)):
            link = os.path.join(target, entry)
            if not os.path.islink(link) or entry in house:
                continue
            dest = os.path.realpath(link)
            ours = os.readlink(link).startswith(SKILLS + os.sep)
            old = any(dest == r or dest.startswith(r + os.sep) for r in old_roots)
            broken = not os.path.exists(link)
            if ours or old or broken:
                actions.append(("unlink", link, os.readlink(link)))

    for kind, link, src in actions:
        print(f"{kind:7} {link} -> {src}")
        if args.apply:
            if kind in ("relink", "unlink"):
                os.unlink(link)
            if kind in ("link", "relink"):
                os.symlink(src, link)
    print(f"{len(actions)} actions{'' if args.apply else ' (dry run; pass --apply)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
