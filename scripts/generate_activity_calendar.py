#!/usr/bin/env python3
"""
Generate GitHub Activity Calendar SVG matching anilpaneru.com.np
with commit numbers on tiles and the oneko pixel cat mascot.
"""

import urllib.request
import json
from datetime import datetime, timedelta

USERNAME = "jstani7"
API_URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}"

# Oneko alert sprite (32x32 pixels)
SPRITE_PIXELS = """
     .                    .     
      .     .       .    .      
       .   .#.     .#.  .       
        .  .##.   .##.          
 ..       .###.   .###.      .. 
   ..     .####. .####.    ..   
     ..  .#####...#####. ..     
         .#############.        
         .###.#####.###.        
....     .###.#####.###.   .... 
         .###.#####.###.        
         .#############.        
         .#...##.##...#.        
          .###########.         
           .#########.          
            ...###...    .      
              .###.     .#.     
             .#####.   .##.     
            .#######. .##.      
           .#########.##.       
        .. .#########.#..       
       .##..####.####..##.      
      .####..###.###..####.     
      .#####.###.###.#####.     
      ...###.###.###.###...     
     ..#####.##...##.#####..    
     ........... ...........    
""".strip().split("\n")

def get_sprite_paths():
    def to_path(char):
        rects = []
        for y, row in enumerate(SPRITE_PIXELS):
            x = 0
            while x < len(row):
                if row[x] == char:
                    start_x = x
                    while x < len(row) and row[x] == char:
                        x += 1
                    rects.append((start_x, y, x - start_x, 1))
                else:
                    x += 1
        return " ".join([f"M{x},{y}h{w}v1h{-w}z" for x, y, w, h in rects])
    return to_path("."), to_path("#")

def fetch_contributions():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    contribs = {}
    for item in data.get("contributions", []):
        contribs[item["date"]] = {
            "count": item.get("count", 0),
            "level": item.get("level", 0)
        }
    return contribs

def generate_svg():
    contribs = fetch_contributions()
    
    # We want 28 weeks (approx. 6.5 months, matching the portfolio display)
    today = datetime.now()
    # End on current week Saturday
    days_to_sat = (5 - today.weekday()) % 7
    if days_to_sat < 0:
        days_to_sat += 7
    end_date = today + timedelta(days=days_to_sat)
    
    # 28 weeks back starting on Sunday
    num_weeks = 28
    start_date = end_date - timedelta(days=num_weeks * 7 - 1)
    
    # Organize into weeks: list of 28 weeks, each week is list of 7 days
    weeks = []
    curr = start_date
    for _ in range(num_weeks):
        week = []
        for _ in range(7):
            date_str = curr.strftime("%Y-%m-%d")
            data = contribs.get(date_str, {"count": 0, "level": 0})
            week.append({
                "date": date_str,
                "dt": curr,
                "count": data["count"],
                "level": data["level"]
            })
            curr += timedelta(days=1)
        weeks.append(week)
    
    # Theme colors from anilpaneru.com.np dark theme
    COLORS = ["#242424", "#0e4429", "#006d32", "#26a641", "#39d353"]
    BLOCK_SIZE = 16
    BLOCK_MARGIN = 4
    BLOCK_RADIUS = 3
    
    # Dimensions
    GRID_WIDTH = num_weeks * (BLOCK_SIZE + BLOCK_MARGIN) - BLOCK_MARGIN
    GRID_HEIGHT = 7 * (BLOCK_SIZE + BLOCK_MARGIN) - BLOCK_MARGIN
    
    PADDING_X = 28
    PADDING_TOP = 28
    PADDING_BOTTOM = 24
    HEADER_HEIGHT = 46
    MONTH_HEIGHT = 22
    
    CARD_WIDTH = GRID_WIDTH + (PADDING_X * 2)
    CARD_HEIGHT = HEADER_HEIGHT + MONTH_HEIGHT + GRID_HEIGHT + PADDING_TOP + PADDING_BOTTOM
    
    SVG_WIDTH = CARD_WIDTH
    SVG_HEIGHT = CARD_HEIGHT
    
    # Month labels
    month_labels = []
    last_month = None
    for col_idx, week in enumerate(weeks):
        # Check first day of week or any day transitioning to new month
        for day in week:
            m_name = day["dt"].strftime("%b")
            if m_name != last_month and day["dt"].day <= 7:
                month_labels.append({
                    "name": m_name,
                    "x": PADDING_X + col_idx * (BLOCK_SIZE + BLOCK_MARGIN)
                })
                last_month = m_name
                break
    
    # Cat sprite paths
    cat_black, cat_white = get_sprite_paths()
    
    # Position the cat near the bottom right (week 23-24, row 5-6)
    cat_col = min(22, num_weeks - 5)
    cat_x = PADDING_X + cat_col * (BLOCK_SIZE + BLOCK_MARGIN) + 8
    cat_y = PADDING_TOP + HEADER_HEIGHT + MONTH_HEIGHT + (5 * (BLOCK_SIZE + BLOCK_MARGIN)) - 8
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" fill="none">')
    
    # Font and styling
    svg.append("""
  <defs>
    <style>
      .title { font-family: "Playfair Display", Georgia, "Times New Roman", serif; font-size: 26px; fill: #f4f4f5; font-weight: 500; }
      .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; fill: #71717a; }
      .month-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: #a1a1aa; font-weight: 500; }
      .tile-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-weight: 700; text-anchor: middle; dominant-baseline: central; user-select: none; }
      .card-border { stroke: rgba(255, 255, 255, 0.08); stroke-width: 1; }
    </style>
  </defs>
""")
    
    # Background Card
    svg.append(f'  <rect x="1" y="1" width="{SVG_WIDTH - 2}" height="{SVG_HEIGHT - 2}" rx="16" fill="#141416" class="card-border" />')
    
    # Header: "GitHub Activity"
    svg.append(f'  <text x="{PADDING_X}" y="{PADDING_TOP + 20}" class="title">GitHub Activity</text>')
    
    # Subtle link or stats indicator
    svg.append(f'  <text x="{SVG_WIDTH - PADDING_X}" y="{PADDING_TOP + 20}" text-anchor="end" class="subtitle">anilpaneru.com.np</text>')
    
    # Horizontal divider line under title
    div_y = PADDING_TOP + HEADER_HEIGHT - 10
    svg.append(f'  <line x1="{PADDING_X}" y1="{div_y}" x2="{SVG_WIDTH - PADDING_X}" y2="{div_y}" stroke="rgba(255, 255, 255, 0.06)" stroke-width="1" />')
    
    # Month Labels
    months_y = PADDING_TOP + HEADER_HEIGHT + 12
    for m in month_labels:
        svg.append(f'  <text x="{m["x"]}" y="{months_y}" class="month-label">{m["name"]}</text>')
    
    # Grid offset
    grid_start_y = PADDING_TOP + HEADER_HEIGHT + MONTH_HEIGHT
    
    # Render Tiles
    for col_idx, week in enumerate(weeks):
        x = PADDING_X + col_idx * (BLOCK_SIZE + BLOCK_MARGIN)
        for row_idx, day in enumerate(week):
            y = grid_start_y + row_idx * (BLOCK_SIZE + BLOCK_MARGIN)
            lvl = min(day["level"], 4)
            color = COLORS[lvl]
            count = day["count"]
            
            # Tile rectangle
            svg.append(f'  <rect x="{x}" y="{y}" width="{BLOCK_SIZE}" height="{BLOCK_SIZE}" rx="{BLOCK_RADIUS}" fill="{color}"><title>{day["date"]}: {count} contribution{"s" if count != 1 else ""}</title></rect>')
            
            # Number inside block (if count > 0)
            if count > 0:
                font_size = "7" if count > 99 else "8.5" if count > 9 else "9.5"
                text_x = x + BLOCK_SIZE / 2
                text_y = y + BLOCK_SIZE / 2
                svg.append(f'  <text x="{text_x:.1f}" y="{text_y:.1f}" font-size="{font_size}" fill="#ffffff" class="tile-text">{count}</text>')
    
    # Oneko Pixel Cat mascot
    svg.append(f'  <g transform="translate({cat_x}, {cat_y}) scale(1.1)">')
    svg.append(f'    <path d="{cat_white}" fill="#ffffff" />')
    svg.append(f'    <path d="{cat_black}" fill="#000000" />')
    svg.append('  </g>')
    
    svg.append('</svg>')
    
    output_path = "assets/github-activity.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Successfully generated {output_path} ({SVG_WIDTH}x{SVG_HEIGHT})")

if __name__ == "__main__":
    generate_svg()
