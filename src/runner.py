#!/usr/bin/env python3
"""k3-capacity-hack runner — orchestrates all providers."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'providers'))

def run_all():
    results = {}

    # USASpending recompetes
    try:
        import usaspending_provider as usp
        naics = ["541511", "541512", "541519", "541330", "541360", "561499", "541690"]
        r = usp.find_recompetes(naics)
        results['usaspending'] = r
        with open('/mnt/agents/output/k3-capacity-hack/dashboard/recompete_data.json', 'w') as f:
            json.dump(r, f, default=str)
        print(f"[USASpending] {r.get('count', 0)} recompete candidates")
    except Exception as e:
        results['usaspending'] = {"error": str(e)}
        print(f"[USASpending] ERR: {e}")

    # Shodan count validation (free)
    try:
        import shodan_provider as sp
        queries = [
            'http.html:"exploit"',
            'http.html:"CVE-"',
            'http.html:"0day"',
            'http.html:"C2"',
            'http.html:"RAT"',
        ]
        counts = {}
        for q in queries:
            c = sp.count(q)
            counts[q] = c.get('total', 0)
            time.sleep(0.5)
        results['shodan_counts'] = counts
        print(f"[Shodan] Counts: {counts}")
    except Exception as e:
        results['shodan_counts'] = {"error": str(e)}
        print(f"[Shodan] ERR: {e}")

    # GitHub search (free)
    try:
        import github_provider as gp
        r = gp.search_repos("exploit language:python stars:>100", per_page=10)
        items = r.get('items', [])
        results['github'] = {"count": r.get('total_count', 0), "top": [i['full_name'] for i in items[:5]]}
        print(f"[GitHub] {r.get('total_count', 0)} repos found")
    except Exception as e:
        results['github'] = {"error": str(e)}
        print(f"[GitHub] ERR: {e}")

    with open('/mnt/agents/output/k3-capacity-hack/run_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    return results

if __name__ == "__main__":
    run_all()
