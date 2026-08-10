#!/usr/bin/env python3
"""USASpending provider — completely free, no auth."""
import json, urllib.request

URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def search_awards(naics_codes, days_back=180, limit=100, page=1):
    from datetime import datetime, timedelta
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    payload = {
        "filters": {
            "time_period": [{"start_date": from_date, "end_date": datetime.now().strftime("%Y-%m-%d")}],
            "award_type_codes": ["A", "B", "C", "D"],
            "naics_codes": naics_codes,
        },
        "fields": [
            "Award ID", "Recipient Name", "Start Date", "End Date",
            "Award Amount", "Awarding Agency", "Awarding Sub Agency",
            "Contract Award Type", "NAICS", "PSC", "Place of Performance State Code",
            "Place of Performance City", "Description", "recipient_id",
        ],
        "sort": "Award Amount", "order": "desc", "limit": limit, "page": page,
    }
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def find_recompetes(naics_codes, target_states=None):
    """Find contracts ending soon = recompete candidates."""
    from datetime import datetime
    data = search_awards(naics_codes, days_back=730, limit=100)
    if "error" in data:
        return data
    results = data.get("results", [])
    candidates = []
    now = datetime.now()
    for r in results:
        end = r.get("End Date", "")
        if not end:
            continue
        try:
            ed = datetime.strptime(end, "%Y-%m-%d")
            days = (ed - now).days
            naics = r.get("NAICS", {})
            naics_code = naics.get("code", "") if isinstance(naics, dict) else naics
            state = r.get("Place of Performance State Code", "")
            if target_states and state not in target_states:
                continue
            if -365 <= days <= 730:
                candidates.append({
                    "award_id": r.get("Award ID", ""),
                    "recipient": r.get("Recipient Name", ""),
                    "amount": r.get("Award Amount", 0),
                    "agency": r.get("Awarding Agency", ""),
                    "naics": naics_code,
                    "state": state,
                    "end_date": end,
                    "days_to_end": days,
                    "description": r.get("Description", "")[:200],
                })
        except:
            pass
    candidates.sort(key=lambda x: x["days_to_end"])
    return {"count": len(candidates), "candidates": candidates}

if __name__ == "__main__":
    naics = ["541511", "541512", "541519", "541330", "541360", "561499", "541690"]
    r = find_recompetes(naics, target_states=["CO", "UT", "AZ", "NM", "TX", "CA", "WA", "NV", "FL", "VA", "MD", "DC"])
    print(json.dumps(r, indent=2, default=str))
