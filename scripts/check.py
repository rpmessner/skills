#!/usr/bin/env python3
"""Gate for the house skill set: manifest coverage, names, collisions, source refs, always-on budget."""
import fnmatch, glob, os, re, sys, tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MODES = {"own", "adopt", "adapt", "merge"}


def front_matter(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fm = {}
    key = None
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fm[key] = m.group(2).strip().strip('"').strip("'")
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def resolve_ref(ref, sources):
    """Return an error string if `source:path` (globs allowed) matches nothing under the source's path."""
    name, _, rel = ref.partition(":")
    if name not in sources:
        return f"unknown source in '{ref}'"
    root = os.path.expanduser(sources[name].get("path", ""))
    if not os.path.isdir(root):
        return f"source path {sources[name].get('path')} missing for '{ref}'"
    if not rel or not glob.glob(os.path.join(root, rel)):
        return f"'{ref}' matches nothing under {sources[name].get('path')}"
    return None


def upstream_skill_dirs(source, files=None):
    """Repo-relative dirs holding a SKILL.md under the source's `scope` prefix.

    files: repo-relative file paths (e.g. `git ls-tree` of a commit); default walks the checkout.
    """
    scope = source.get("scope", "").strip("/")
    if files is None:
        root = os.path.expanduser(source.get("path", ""))
        files = []
        for dirpath, dirnames, filenames in os.walk(os.path.join(root, scope) if scope else root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            if "SKILL.md" in filenames:
                files.append(os.path.relpath(os.path.join(dirpath, "SKILL.md"), root))
    return sorted(
        os.path.dirname(f) for f in files
        if os.path.basename(f) == "SKILL.md" and (not scope or f.startswith(scope + "/"))
    )


def ref_covers(pattern, path):
    """True if a ref path pattern (globs allowed) matches `path` or one of its ancestor dirs."""
    parts = path.split("/")
    pattern = pattern.rstrip("/")
    return any(fnmatch.fnmatchcase("/".join(parts[:i]), pattern) for i in range(1, len(parts) + 1))


def unmapped(catalog, source_name, dirs):
    """Dirs not covered by any [[skill]]/[[drop]] ref of this source."""
    refs = [r for e in catalog.get("skill", []) for r in e.get("from", [])]
    refs += [d.get("from", "") for d in catalog.get("drop", [])]
    pats = [r.partition(":")[2] for r in refs if r.partition(":")[0] == source_name]
    return [d for d in dirs if not any(ref_covers(p, d) for p in pats)]


def main():
    errors = []
    catalog = tomllib.load(open(os.path.join(ROOT, "catalog.toml"), "rb"))
    sources = catalog.get("sources", {})
    entries = catalog.get("skill", [])
    names = [e.get("name") for e in entries]

    for dup in sorted({n for n in names if names.count(n) > 1}):
        errors.append(f"catalog: skill '{dup}' listed more than once")
    for e in entries:
        n = e.get("name", "?")
        if e.get("mode") not in MODES:
            errors.append(f"catalog: '{n}' mode must be one of {sorted(MODES)}")
        if not e.get("job"):
            errors.append(f"catalog: '{n}' has no job")
        if e.get("mode") != "own" and not e.get("from"):
            errors.append(f"catalog: '{n}' is {e.get('mode')} but lists no 'from'")
        for ref in e.get("from", []):
            err = resolve_ref(ref, sources)
            if err:
                errors.append(f"catalog: '{n}' from: {err}")
    for d in catalog.get("drop", []):
        if not d.get("reason"):
            errors.append(f"catalog: drop '{d.get('from')}' has no reason")
        err = resolve_ref(d.get("from", ""), sources)
        if err:
            errors.append(f"catalog: drop from: {err}")
    for sname, src in sources.items():
        if os.path.isdir(os.path.expanduser(src.get("path", ""))):
            for d in unmapped(catalog, sname, upstream_skill_dirs(src)):
                errors.append(f"upstream: {sname}:{d} has no [[skill]] or [[drop]] entry")

    skills_dir = os.path.join(ROOT, "skills")
    dirs = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
    for d in sorted(set(dirs) - set(names)):
        errors.append(f"skills/{d}: no catalog entry")
    for n in sorted(set(names) - set(dirs)):
        errors.append(f"catalog: '{n}' has no skills/{n}/ directory")

    always_on = 0
    for d in dirs:
        path = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(path):
            errors.append(f"skills/{d}: missing SKILL.md")
            continue
        fm = front_matter(path)
        if fm is None:
            errors.append(f"skills/{d}/SKILL.md: missing front matter")
            continue
        if fm.get("name") != d:
            errors.append(f"skills/{d}/SKILL.md: name '{fm.get('name')}' must equal directory name")
        if not NAME_RE.match(d):
            errors.append(f"skills/{d}: name must be lowercase words joined by hyphens")
        if not fm.get("description"):
            errors.append(f"skills/{d}/SKILL.md: missing description")
        if fm.get("disable-model-invocation", "").lower() != "true":
            always_on += (len(d) + len(fm.get("description", ""))) // 4

    budget = catalog.get("budget", {}).get("always_on_tokens", 0)
    if budget and always_on > budget:
        errors.append(f"budget: always-on ~{always_on} tokens exceeds {budget}")

    for e in errors:
        print("FAIL", e)
    print(f"{len(dirs)} skills, always-on ~{always_on}/{budget} tokens, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
