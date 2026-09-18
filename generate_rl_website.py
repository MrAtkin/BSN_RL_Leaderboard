import sqlite3
import os

DB_FILE = 'rocket_league.db'

def generate_static_website():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, DB_FILE)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT season FROM teams ORDER BY season DESC")
    seasons = [row[0] for row in cursor.fetchall()]
    
    if not seasons:
        conn.close()
        return

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rocket League Tournaments</title>
    <style>
        :root {
            --bg-color: #f4f7f6;
            --text-color: #333;
            --container-bg: white;
            --match-bg: #2c3e50;
            --match-border: #1a252f;
            --win-bg: #27ae60;
            --score-bg: #111;
        }
        .dark-mode {
            --bg-color: #121212;
            --text-color: #e0e0e0;
            --container-bg: #1e1e1e;
            --match-bg: #2a2a2a;
            --match-border: #444;
            --win-bg: #b58500;
        }
        
        body { font-family: Arial, sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; transition: 0.3s; }
        .container { max-width: 1400px; margin: 0 auto; background: var(--container-bg); padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1, h2 { text-align: center; }
        .controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        select, button { padding: 10px; border-radius: 4px; font-size: 16px; cursor: pointer; }
        
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        th, td { padding: 10px; text-align: center; border-bottom: 1px solid var(--match-border); }
        th { background-color: var(--match-bg); color: white; }
        
        .season-view { display: none; }
        .season-view.active { display: block; }

        /* CSS GRID FOR ARROW UPPER BRACKET */
        .ub-grid { display: grid; grid-template-columns: repeat(4, minmax(220px, 1fr)); grid-template-rows: auto repeat(8, 1fr); gap: 15px 25px; margin-bottom: 40px; overflow-x: auto; padding-bottom: 20px; }
        .ub-head h3 { text-align: center; font-size: 14px; color: #888; text-transform: uppercase; margin: 0 0 10px 0; align-self: end; }
        .head-1 { grid-column: 1; grid-row: 1; }
        .head-2 { grid-column: 2; grid-row: 1; }
        .head-3 { grid-column: 3; grid-row: 1; }
        .head-4 { grid-column: 4; grid-row: 1; }
        
        .ub-cell { align-self: center; }
        .cell-w1 { grid-column: 1; grid-row: 2; }
        .cell-w2 { grid-column: 1; grid-row: 3; }
        .cell-w3 { grid-column: 1; grid-row: 4; }
        .cell-w4 { grid-column: 1; grid-row: 5; }
        .cell-w5 { grid-column: 1; grid-row: 6; }
        .cell-w6 { grid-column: 1; grid-row: 7; }
        .cell-w7 { grid-column: 1; grid-row: 8; }
        .cell-w8 { grid-column: 1; grid-row: 9; }
        
        .cell-w9 { grid-column: 2; grid-row: 2 / 4; }
        .cell-w10 { grid-column: 2; grid-row: 4 / 6; }
        .cell-w11 { grid-column: 2; grid-row: 6 / 8; }
        .cell-w12 { grid-column: 2; grid-row: 8 / 10; }
        
        .cell-w13 { grid-column: 3; grid-row: 2 / 6; }
        .cell-w14 { grid-column: 3; grid-row: 6 / 10; }
        
        .cell-w15 { grid-column: 4; grid-row: 2 / 10; }

        /* FLEXBOX LAYOUT FOR LOWER BRACKET */
        .bracket-section { display: flex; gap: 20px; margin-bottom: 40px; overflow-x: auto; padding-bottom: 20px; }
        .bracket-column { display: flex; flex-direction: column; justify-content: space-around; gap: 15px; min-width: 220px; }
        .bracket-column h3 { text-align: center; font-size: 14px; color: #888; text-transform: uppercase; margin-bottom: 5px; }
        
        .match-card { background: var(--match-bg); border: 1px solid var(--match-border); border-radius: 6px; overflow: hidden; color: white; display: flex; flex-direction: column; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .match-id { background: #111; font-size: 10px; padding: 3px; text-align: center; color: #aaa; letter-spacing: 1px; }
        .team-row { display: flex; justify-content: space-between; padding: 8px 12px; border-bottom: 1px solid #111; font-size: 14px; align-items: center;}
        .team-row:last-child { border-bottom: none; }
        .team-row.winner { background-color: var(--win-bg); font-weight: bold; }
        .score { background: var(--score-bg); padding: 2px 8px; border-radius: 4px; font-family: monospace; }
        .bye-text { color: #888; font-style: italic; }
    </style>
    <script>
        function updateView() {
            var season = document.getElementById('seasonSelect').value;
            document.querySelectorAll('.season-view').forEach(el => el.classList.remove('active'));
            document.getElementById('view-' + season.replace(/\s+/g, '-')).classList.add('active');
        }
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('rlDarkMode', document.body.classList.contains('dark-mode'));
        }
        window.onload = function() {
            if (localStorage.getItem('rlDarkMode') === 'true') document.body.classList.add('dark-mode');
            updateView();
        }
    </script>
</head>
<body>
<div class="container">
    <div class="controls">
        <h1>Rocket League 2v2 Tracker</h1>
        <div>
            <select id="seasonSelect" onchange="updateView()">
"""
    for season in seasons:
        html_content += f'<option value="{season}">{season}</option>\n'
        
    html_content += """            </select>
            <button onclick="toggleDarkMode()">🌙</button>
        </div>
    </div>
"""

    for index, season in enumerate(seasons):
        safe_season = season.replace(" ", "-")
        is_active = "active" if index == 0 else ""
        
        # Build team dictionary
        cursor.execute("SELECT id, name, p1, p2 FROM teams WHERE season = ?", (season,))
        teams = {row[0]: {'name': row[1], 'p1': row[2], 'p2': row[3]} for row in cursor.fetchall()}
        teams[0] = {'name': 'BYE', 'p1': '', 'p2': ''}
        teams[-1] = {'name': 'TBD', 'p1': '', 'p2': ''}
        
        # Build Match Dictionary
        cursor.execute("SELECT match_id, t1_id, t2_id, score1, score2, is_completed FROM matches WHERE season = ?", (season,))
        matches = {r[0]: {'t1': r[1], 't2': r[2], 's1': r[3], 's2': r[4], 'comp': r[5]} for r in cursor.fetchall()}

        def render_match(m_id):
            if m_id not in matches: return ""
            m = matches[m_id]
            t1 = teams.get(m['t1'], teams[-1])
            t2 = teams.get(m['t2'], teams[-1])
            
            w1_class = "winner" if m['comp'] and m['s1'] > m['s2'] else ""
            w2_class = "winner" if m['comp'] and m['s2'] > m['s1'] else ""
            
            n1_class = "bye-text" if m['t1'] in [0, -1] else ""
            n2_class = "bye-text" if m['t2'] in [0, -1] else ""

            html = f'<div class="match-card"><div class="match-id">{m_id}</div>'
            html += f'<div class="team-row {w1_class}"><span class="{n1_class}">{t1["name"]}</span><span class="score">{m["s1"]}</span></div>'
            html += f'<div class="team-row {w2_class}"><span class="{n2_class}">{t2["name"]}</span><span class="score">{m["s2"]}</span></div></div>'
            return html

        html_content += f'<div id="view-{safe_season}" class="season-view {is_active}">'
        
        # Roster Table
        html_content += "<h2>Registered Roster</h2><table><tr><th>Team Name</th><th>Player 1</th><th>Player 2</th></tr>"
        for t_id, data in teams.items():
            if t_id > 0: html_content += f"<tr><td><strong>{data['name']}</strong></td><td>{data['p1']}</td><td>{data['p2']}</td></tr>"
        html_content += "</table>"
        
        # Upper Bracket Grid Layout
        html_content += '<h2>Upper Bracket</h2><div class="ub-grid">'
        html_content += '<div class="ub-head head-1"><h3>Round 1</h3></div>'
        html_content += '<div class="ub-head head-2"><h3>Quarter-Finals</h3></div>'
        html_content += '<div class="ub-head head-3"><h3>Semi-Finals</h3></div>'
        html_content += '<div class="ub-head head-4"><h3>UB Final</h3></div>'
        
        for i in range(1, 16):
            html_content += f'<div class="ub-cell cell-w{i}">{render_match(f"W{i}")}</div>'
            
        html_content += '</div>'

        # Lower Bracket Flexbox Columns
        html_content += '<h2>Lower Bracket</h2><div class="bracket-section">'
        html_content += f'<div class="bracket-column"><h3>Round 1</h3>{render_match("L1")}{render_match("L2")}{render_match("L3")}{render_match("L4")}</div>'
        html_content += f'<div class="bracket-column"><h3>Round 2</h3>{render_match("L5")}{render_match("L6")}{render_match("L7")}{render_match("L8")}</div>'
        html_content += f'<div class="bracket-column"><h3>Round 3</h3>{render_match("L9")}{render_match("L10")}</div>'
        html_content += f'<div class="bracket-column"><h3>Round 4</h3>{render_match("L11")}{render_match("L12")}</div>'
        html_content += f'<div class="bracket-column"><h3>Semi-Final</h3>{render_match("L13")}</div>'
        html_content += f'<div class="bracket-column"><h3>LB Final</h3>{render_match("L14")}</div>'
        html_content += '</div>'
        
        # Grand Final
        html_content += '<h2>Championship</h2><div class="bracket-section" style="justify-content: center;">'
        html_content += f'<div class="bracket-column" style="min-width: 300px;"><h3>Grand Final</h3>{render_match("GF")}</div>'
        html_content += '</div></div>'

    html_content += "</div></body></html>"
    conn.close()

    with open(os.path.join(script_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    generate_static_website()