"""Render data/contributions.json into an animated contrib-heatmap.svg."""
import json
from datetime import datetime, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BOX, GAP = 12, 3
WEEKS, DAYS = 53, 7
TARGET_W = 860

STYLE_BLOCK = (
    "<style>"
    ".hbg { fill: #0d1117; } "
    ".lbl { font-family:\'SF Mono\',\'Fira Code\',Consolas,monospace; font-size:12px; fill:#8b949e; } "
    ".stat { font-family:\'SF Mono\',\'Fira Code\',Consolas,monospace; font-size:13px; fill:#c9d1d9; }"
    "</style>"
)


def load():
    with open("data/contributions.json") as f:
        return json.load(f)


def build_grid(data):
    days_by_date = {d["date"]: d for d in data["days"]}
    if data["days"]:
        last_date = datetime.strptime(data["days"][-1]["date"], "%Y-%m-%d").date()
    else:
        last_date = datetime.utcnow().date()

    end = last_date
    start = end - timedelta(weeks=WEEKS - 1)
    start -= timedelta(days=(start.weekday() + 1) % 7)

    grid = []
    cur = start
    for _w in range(WEEKS):
        col = []
        for _d in range(DAYS):
            key = cur.strftime("%Y-%m-%d")
            entry = days_by_date.get(key)
            level = entry["level"] if entry else 0
            col.append(level)
            cur += timedelta(days=1)
        grid.append(col)
    return grid


def render(data):
    grid = build_grid(data)
    pad_x = (TARGET_W - WEEKS * (BOX + GAP)) // 2
    h_svg = 40 + DAYS * (BOX + GAP) + 30 + 30

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{TARGET_W}" height="{h_svg}" viewBox="0 0 {TARGET_W} {h_svg}">']
    svg.append(STYLE_BLOCK)
    svg.append(f'<rect class="hbg" width="{TARGET_W}" height="{h_svg}"/>')

    for wi in range(WEEKS):
        for di in range(DAYS):
            level = grid[wi][di]
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = pad_x + wi * (BOX + GAP)
            y = 20 + di * (BOX + GAP)
            delay = (wi + di * 0.3) * 0.012
            svg.append(
                f'<rect x="{x}" y="{y-40}" width="{BOX}" height="{BOX}" rx="2" fill="{color}" opacity="0">'
                f'<animate attributeName="y" from="{y-40}" to="{y}" begin="{delay}s" dur="0.5s" fill="freeze" '
                f'calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.4s" fill="freeze"/></rect>'
            )

    legend_y = h_svg - 30 + 10
    svg.append(f'<text x="{pad_x}" y="{legend_y+10}" class="lbl">Less</text>')
    lx = pad_x + 40
    for i, c in enumerate(PALETTE):
        svg.append(f'<rect x="{lx+i*16}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>')
    svg.append(f'<text x="{lx+len(PALETTE)*16+8}" y="{legend_y+10}" class="lbl">More</text>')

    footer_y = h_svg - 6
    total = data.get("total_contributions", 0)
    svg.append(f'<text x="{pad_x}" y="{footer_y}" class="stat">{total:,} contributions in the last year (auto-refreshed daily)</text>')

    svg.append("</svg>")

    with open("contrib-heatmap.svg", "w") as f:
        f.write("\n".join(svg))
    print(f"Rendered heatmap: total={total}")


if __name__ == "__main__":
    render(load())
