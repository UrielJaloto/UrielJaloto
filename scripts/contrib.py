import datetime, json, os, sys, urllib.request

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
THEMES = {
    "dark": {"cells": ["#161b22", "#3b1f5c", "#6b21a8", "#8a2be2", "#c084fc"], "text": "#c9d1d9", "muted": "#8b949e"},
    "light": {"cells": ["#ebedf0", "#e9d5ff", "#c084fc", "#a855f7", "#7e22ce"], "text": "#24292f", "muted": "#57606a"},
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CELL, GAP, LEFT, TOP = 11, 3, 30, 40


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def render(cal, theme):
    weeks = cal["weeks"]
    width = LEFT + len(weeks) * (CELL + GAP) + 10
    height = TOP + 7 * (CELL + GAP) + 10
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">']
    out.append(f'<text x="{LEFT}" y="16" font-size="13" font-weight="600" fill="{theme["text"]}">{cal["totalContributions"]:,} contributions in the last year</text>')
    last_month = None
    for i, week in enumerate(weeks):
        x = LEFT + i * (CELL + GAP)
        month = int(week["contributionDays"][0]["date"][5:7])
        if month != last_month and i < len(weeks) - 2:
            out.append(f'<text x="{x}" y="{TOP - 6}" font-size="10" fill="{theme["muted"]}">{MONTHS[month - 1]}</text>')
            last_month = month
        for day in week["contributionDays"]:
            weekday = datetime.date.fromisoformat(day["date"]).isoweekday() % 7
            y = TOP + weekday * (CELL + GAP)
            color = theme["cells"][LEVELS.index(day["contributionLevel"])]
            out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"><title>{day["date"]}: {day["contributionCount"]}</title></rect>')
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="0" y="{TOP + row * (CELL + GAP) + 9}" font-size="9" fill="{theme["muted"]}">{label}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    login, out_dir = sys.argv[1], sys.argv[2]
    cal = fetch(login, os.environ["GITHUB_TOKEN"])
    os.makedirs(out_dir, exist_ok=True)
    for name, theme in THEMES.items():
        with open(os.path.join(out_dir, f"contributions-{name}.svg"), "w", encoding="utf-8") as f:
            f.write(render(cal, theme))


if __name__ == "__main__":
    main()
