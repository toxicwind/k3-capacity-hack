#!/usr/bin/env python3
"""GitHub provider — free tier, no auth needed for search."""
import json, urllib.request, urllib.parse, os

def search_repos(query, per_page=30):
    """Search GitHub repos — no auth needed, rate limit 10/min."""
    enc = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={enc}&sort=updated&order=desc&per_page={per_page}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "k3-capacity-hack"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_repo_files(owner, repo, path=""):
    """List files in a repo directory."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "k3-capacity-hack"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_raw_file(url):
    """Fetch raw file content from GitHub raw."""
    req = urllib.request.Request(url, headers={"User-Agent": "k3-capacity-hack"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode()
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "exploit"
    r = search_repos(q)
    items = r.get("items", [])
    print(f"Found {r.get('total_count', 0)} repos for '{q}'")
    for item in items[:5]:
        print(f"  {item['full_name']} | {item['html_url']} | {item.get('description','')[:60]}")
