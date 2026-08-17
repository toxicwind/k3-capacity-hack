#!/usr/bin/env python3
"""k3-capacity-hack runner — orchestrates all providers with graceful degradation."""
import sys, os, json, time
from datetime import datetime

# Ensure dashboard dir exists
os.makedirs("dashboard", exist_ok=True)
os.makedirs("src", exist_ok=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'providers'))

def run_all():
    results = {}
    start_time = time.time()

    # USASpending recompetes
    try:
        import usaspending_provider as usp
        naics = ["541511", "541512", "541519", "541330", "541360", "561499", "541690"]
        r = usp.find_recompetes(naics)
        results['usaspending'] = r
        with open('dashboard/recompete_data.json', 'w') as f:
            json.dump(r, f, indent=2, default=str)
        print(f"[USASpending] {r.get('count', 0)} recompete candidates")
    except Exception as e:
        results['usaspending'] = {"error": str(e), "count": 0, "candidates": []}
        print(f"[USASpending] ERR: {e}")

    # Shodan summary (free, key optional)
    try:
        import shodan_provider as sp
        r = sp.free_summary()
        results['shodan'] = r
        with open('dashboard/shodan_summary.json', 'w') as f:
            json.dump(r, f, indent=2, default=str)
        print(f"[Shodan] Summary collected")
    except Exception as e:
        results['shodan'] = {"error": str(e)}
        print(f"[Shodan] ERR: {e}")

    # GitHub search (free)
    try:
        import github_provider as gp
        r = gp.search_repos("exploit language:python stars:>100", per_page=10)
        items = r.get('items', [])
        results['github'] = {
            "count": r.get('total_count', 0),
            "top": [i['full_name'] for i in items[:5]],
            "rate_limit_note": "10 req/min unauthenticated"
        }
        with open('dashboard/github_repos.json', 'w') as f:
            json.dump(results['github'], f, indent=2, default=str)
        print(f"[GitHub] {r.get('total_count', 0)} repos found")
    except Exception as e:
        results['github'] = {"error": str(e), "count": 0, "top": []}
        print(f"[GitHub] ERR: {e}")

    # Generate master summary
    summary = {
        "run_timestamp": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": round(time.time() - start_time, 2),
        "providers": {k: {"status": "ok" if "error" not in v else "error", "count": v.get("count", 0)} for k, v in results.items()},
        "full_results": results,
    }

    with open('dashboard/summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    with open('dashboard/run_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"[DONE] All results written to dashboard/ — duration: {summary['duration_seconds']}s")
    return results

if __name__ == "__main__":
    run_all()
