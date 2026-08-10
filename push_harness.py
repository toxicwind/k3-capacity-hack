#!/usr/bin/env python3
"""
K3-CAPACITY-HACK PUSH HARNESS v1.0
Handles upstream drift, merge without clobber, branch sync.
Zero dependencies — uses only stdlib + subprocess.
Usage: python3 push_harness.py <<PAT_PLACEHOLDER>>
"""
import subprocess, sys, json, urllib.request, urllib.parse, os

REPO = "toxicwind/k3-capacity-hack"
LOCAL = "/mnt/agents/output/k3-capacity-hack"
UPSTREAM_URL = "https://github.com/" + REPO + ".git"

def run(cmd, cwd=LOCAL, check=False):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}")
        print(f"  {r.stderr[:500]}")
        sys.exit(1)
    return r

def api(method, path, data=None, pat=None):
    url = f"https://api.github.com/{path}"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "k3-harness"}
    if pat:
        headers["Authorization"] = f"token {pat}"
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode()) if e.code != 204 else {}, e.code
    except Exception as e:
        return {"error": str(e)}, 0

def main():
    pat = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("<PAT_ENV>", "")
    if not pat:
        print("Usage: python3 push_harness.py <<PAT_PLACEHOLDER>>")
        print("   or: <PAT_ENV>=<pat> python3 push_harness.py")
        sys.exit(1)

    os.chdir(LOCAL)

    # Verify PAT
    user, code = api("GET", "user", pat=pat)
    if code != 200:
        print(f"PAT invalid: {user}")
        sys.exit(1)
    print(f"Authenticated as: {user.get('login', '?')}")

    # Check if repo exists upstream
    repo, code = api("GET", f"repos/{REPO}", pat=pat)
    exists = code == 200

    if not exists:
        print(f"Repo {REPO} does not exist. Creating...")
        repo, code = api("POST", "user/repos", {
            "name": "k3-capacity-hack",
            "private": True,
            "description": "K3 capacity hack — private internal",
            "auto_init": False
        }, pat=pat)
        if code not in (200, 201):
            print(f"Create failed: {repo}")
            sys.exit(1)
        print(f"Created: {repo.get('html_url', '?')}")
    else:
        print(f"Repo exists: {repo.get('html_url', '?')}")
        print(f"  Default branch: {repo.get('default_branch', 'main')}")

    # Configure remote with PAT
    remote_url = f"https://{pat}@github.com/{REPO}.git"
    run("git remote remove origin 2>/dev/null; true")
    run(f"git remote add origin {remote_url}")
    print("Remote configured.")

    # Fetch upstream to detect drift
    print("Fetching upstream...")
    fetch = run("git fetch origin --quiet 2>&1")
    if fetch.returncode != 0:
        # First push — no upstream yet
        print("No upstream history (first push).")
    else:
        # Check if upstream has commits we don't have
        local_head = run("git rev-parse HEAD").stdout.strip()
        upstream_head = run("git rev-parse origin/main 2>/dev/null || echo ''").stdout.strip()

        if upstream_head and upstream_head != local_head:
            print(f"UPSTREAM DRIFT DETECTED:")
            print(f"  Local:  {local_head[:8]}")
            print(f"  Origin: {upstream_head[:8]}")

            # Check if upstream is ancestor of local (fast-forward)
            merge_base = run(f"git merge-base {local_head} {upstream_head}").stdout.strip()
            if merge_base == upstream_head:
                print("  Upstream is ancestor — fast-forward push possible.")
            elif merge_base == local_head:
                print("  Local is ancestor — need to merge upstream changes.")
                # Merge upstream into local without clobber
                merge = run("git merge origin/main --no-edit --quiet 2>&1", check=False)
                if merge.returncode != 0:
                    print("  Merge conflict! Aborting to prevent clobber.")
                    run("git merge --abort")
                    print("  Merge aborted. Manual resolution required.")
                    sys.exit(1)
                print("  Merged upstream successfully.")
            else:
                print("  Divergent histories — need rebase or merge.")
                # Prefer merge over rebase to preserve history
                merge = run("git merge origin/main --no-edit --quiet 2>&1", check=False)
                if merge.returncode != 0:
                    print("  Merge conflict! Aborting.")
                    run("git merge --abort")
                    sys.exit(1)
                print("  Merged successfully.")
        else:
            print("  No drift — local and origin in sync.")

    # Push
    print("Pushing to origin/main...")
    push = run("git push -u origin main --force-with-lease 2>&1")
    if push.returncode != 0:
        print(f"Push failed: {push.stderr[:500]}")
        # Fallback: try without force-with-lease
        push2 = run("git push -u origin main 2>&1")
        if push2.returncode != 0:
            print(f"Fallback push failed: {push2.stderr[:500]}")
            sys.exit(1)

    print("SUCCESS: Pushed to origin/main.")

    # Verify
    verify, code = api("GET", f"repos/{REPO}/commits/main", pat=pat)
    if code == 200:
        print(f"Verified: {verify.get('sha', '?')[:8]} on GitHub")

if __name__ == "__main__":
    main()
