"""Fetch public GitHub contribution calendar data - no token needed."""
import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "volkantutuncu")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch():
    resp = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    days = []
    for td in soup.select("td.ContributionCalendar-day, td[data-date]"):
        date = td.get("data-date")
        if not date:
            continue
        level = td.get("data-level")
        if level is None:
            cls = " ".join(td.get("class", []))
            m = re.search(r"L(\d)", cls)
            level = m.group(1) if m else "0"
        count_attr = td.get("data-count")
        days.append({
            "date": date,
            "level": int(level),
            "count": int(count_attr) if count_attr else None,
        })

    days.sort(key=lambda d: d["date"])
    total = sum(d["count"] or 0 for d in days)

    streak = 0
    longest = 0
    for d in days:
        if (d["count"] or 0) > 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0

    current = 0
    for d in reversed(days):
        if (d["count"] or 0) > 0:
            current += 1
        else:
            break

    data = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total_contributions": total,
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Fetched {len(days)} days, total={total}, current_streak={current}")


if __name__ == "__main__":
    fetch()
