#!/usr/bin/env python3
"""Shodan provider — zero-credit strategies, key optional."""
import json, urllib.request, urllib.parse, re, os, time

KEY = os.environ.get("SHODAN_KEY", "")

def count(query):
    """FREE with key — validates query without spending credits."""
    if not KEY:
        return {"total": 0, "note": "no SHODAN_KEY set", "query": query}
    url = f"https://api.shodan.io/shodan/host/count?key={KEY}&query={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"total": 0, "error": str(e), "query": query}

def search(query, limit=10):
    """Costs 1 credit per query. Skipped if no key."""
    if not KEY:
        return {"matches": [], "note": "no SHODAN_KEY set", "query": query}
    url = f"https://api.shodan.io/shodan/host/search?key={KEY}&query={urllib.parse.quote(query)}&limit={limit}&minify=True"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"matches": [], "error": str(e), "query": query}

def facet_scrape(query, facet="org"):
    """FREE — uses public facet pages, no API key needed."""
    url = f"https://www.shodan.io/search/facet?query={urllib.parse.quote(query)}&facet={facet}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            html = r.read().decode()
        vals = re.findall(r'facet-name[^>]*>([^<]+)</div>.*?facet-count[^>]*>([^<]+)</div>', html, re.S)
        return {"facet": facet, "query": query, "results": [{"name": v[0].strip(), "count": v[1].strip()} for v in vals[:20]]}
    except Exception as e:
        return {"facet": facet, "query": query, "error": str(e), "results": []}

def free_summary():
    """Run all free methods without key."""
    queries = [
        'http.html:"exploit"',
        'http.html:"CVE-2026"',
        'http.html:"0day"',
        'http.html:"C2"',
        'http.html:"RAT"',
    ]
    out = {}
    for q in queries:
        out[q] = count(q)
        time.sleep(0.3)
    out["facets"] = facet_scrape("apache", "org")
    return out

if __name__ == "__main__":
    print(json.dumps(free_summary(), indent=2))
