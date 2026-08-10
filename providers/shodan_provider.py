#!/usr/bin/env python3
"""Shodan provider — zero-credit strategies."""
import json, urllib.request, urllib.parse, re, os

KEY = os.environ.get("SHODAN_KEY", "")
OUT = os.environ.get("SHODAN_OUT", "/mnt/agents/output/shodan_greyblack")

def count(query):
    """FREE — validates query without spending credits."""
    if not KEY:
        return {"error": "no key"}
    url = f"https://api.shodan.io/shodan/host/count?key={KEY}&query={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def search(query, limit=10):
    """Costs 1 credit per query. Use sparingly."""
    if not KEY:
        return {"error": "no key"}
    url = f"https://api.shodan.io/shodan/host/search?key={KEY}&query={urllib.parse.quote(query)}&limit={limit}&minify=True"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def facet_scrape(query, facet="org"):
    """FREE — uses public facet pages, no API key needed."""
    url = f"https://www.shodan.io/search/facet?query={urllib.parse.quote(query)}&facet={facet}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            html = r.read().decode()
        # Extract facet values from HTML
        vals = re.findall(r'<div class="facet-name">([^<]+)</div>.*?<div class="facet-count">(\d+)</div>', html, re.DOTALL)
        return {"facet": facet, "values": [{"name": v[0].strip(), "count": int(v[1])} for v in vals[:50]]}
    except Exception as e:
        return {"error": str(e)}

def extract_github_repos(matches):
    """Extract GitHub repos from Shodan match banners."""
    repos = {}
    for m in matches:
        banner = json.dumps(m)
        found = re.findall(r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', banner)
        for r in found:
            if r not in repos:
                repos[r] = {"ips": set(), "queries": set(), "ports": set()}
            repos[r]["ips"].add(m.get("ip_str", ""))
            repos[r]["ports"].add(str(m.get("port", "")))
    return {k: {**v, "ips": list(v["ips"]), "ports": list(v["ports"])} for k, v in repos.items()}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 shodan_provider.py <query>")
        exit(1)
    q = sys.argv[1]
    c = count(q)
    print(json.dumps(c, indent=2))
