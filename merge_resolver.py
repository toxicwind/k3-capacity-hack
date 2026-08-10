#!/usr/bin/env python3
"""
K3-CAPACITY-HACK MERGE RESOLVER
When upstream changes conflict with local, this resolves by:
1. Stashing local changes
2. Fetching upstream
3. Applying stash on top
4. If conflicts: prefer local for src/, prefer upstream for README/docs
"""
import subprocess, sys, os

LOCAL = "/mnt/agents/output/k3-capacity-hack"

def run(cmd, check=False):
    r = subprocess.run(cmd, shell=True, cwd=LOCAL, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}")
        print(r.stderr[:500])
        sys.exit(1)
    return r

os.chdir(LOCAL)

# Stash local
print("Stashing local changes...")
run("git stash push -m 'auto-stash-before-merge'", check=True)

# Fetch
print("Fetching upstream...")
run("git fetch origin", check=True)

# Try merge
print("Merging origin/main...")
merge = run("git merge origin/main --no-edit")
if merge.returncode == 0:
    print("Merge clean. Applying stash...")
    stash = run("git stash pop")
    if stash.returncode != 0:
        print("Stash pop conflict — resolving...")
        # For each conflict, prefer local for code, upstream for docs
        conflicts = run("git diff --name-only --diff-filter=U").stdout.strip().split("\n")
        for f in conflicts:
            f = f.strip()
            if not f:
                continue
            if f.startswith("src/") or f.startswith("providers/"):
                print(f"  {f}: prefer LOCAL (ours)")
                run(f"git checkout --ours {f}")
            else:
                print(f"  {f}: prefer UPSTREAM (theirs)")
                run(f"git checkout --theirs {f}")
            run(f"git add {f}")
        run("git commit -m 'merge: auto-resolve conflicts'", check=True)
    print("Done.")
else:
    print("Merge failed. Aborting.")
    run("git merge --abort")
    run("git stash pop")
    sys.exit(1)
