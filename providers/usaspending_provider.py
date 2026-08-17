#!/usr/bin/env python3
"""USASpending provider — completely free, no auth."""
import json, urllib.request
from datetime import datetime, timedelta

URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def search_awards(naics_codes, days_back=180, limit=100, page=1):
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "filters": {
            "time_period": [{"start_date": from_date, "end_date": to_date}],
            "award_type_codes": ["A", "B", "C", "D"],
            "naics_codes": {"require": ["ALL_OF"], "exclude": [], "require": naics_codes},
        },
        "fields": [
            "Award ID", "Recipient Name", "Start Date", "End Date",
            "Award Amount", "Awarding Agency", "Awarding Sub Agency",
            "Contract Award Type", "NAICS", "Description",
        ],
        "sort": "Award Amount", "order": "desc", "limit": limit, "page": page,
    }
    # Fix: USASpending uses slightly different filter format
    payload["filters"]["naics_codes"] = naics_codes
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e), "results": []}

def find_recompetes(naics_codes, target_states=None):
    """Find contracts ending soon = recompete candidates."""
    data = search_awards(naics_codes, days_back=365, limit=50)
    if "error" in data and not data.get("results"):
        return {"count": 0, "error": data["error"], "candidates": []}

    results = data.get("results", [])
    candidates = []
    for award in results:
        end_date = award.get("End Date", "")
        amount = award.get("Award Amount", 0)
        try:
            if end_date and datetime.strptime(end_date, "%Y-%m-%d") < datetime.now() + timedelta(days=180):
                candidates.append({
                    "award_id": award.get("Award ID"),
                    "recipient": award.get("Recipient Name"),
                    "end_date": end_date,
                    "amount": amount,
                    "agency": award.get("Awarding Agency"),
                    "naics": award.get("NAICS"),
                    "description": award.get("Description", "")[:200],
                })
        except:
            pass

    return {
        "count": len(candidates),
        "total_results": len(results),
        "candidates": candidates[:20],
    }

if __name__ == "__main__":
    import sys
    naics = sys.argv[1:] if len(sys.argv) > 1 else ["541511", "541512"]
    print(json.dumps(find_recompetes(naics), indent=2))
