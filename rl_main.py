import sqlite3
import os
from generate_rl_website import generate_static_website

DB_FILE = 'rocket_league.db'

# Universal 16-Team Double Elimination Routing Map
ROUTING = {
    'W1': ('W9', 1, 'L1', 1), 'W2': ('W9', 2, 'L1', 2),
    'W3': ('W10', 1, 'L2', 1), 'W4': ('W10', 2, 'L2', 2),
    'W5': ('W11', 1, 'L3', 1), 'W6': ('W11', 2, 'L3', 2),
    'W7': ('W12', 1, 'L4', 1), 'W8': ('W12', 2, 'L4', 2),
    'W9': ('W13', 1, 'L5', 2), 'W10': ('W13', 2, 'L6', 2),
    'W11': ('W14', 1, 'L7', 2), 'W12': ('W14', 2, 'L8', 2),
    'W13': ('W15', 1, 'L11', 2), 'W14': ('W15', 2, 'L12', 2),
    'W15': ('GF', 1, 'L14', 2),
    'L1': ('L5', 1, None, None), 'L2': ('L6', 1, None, None),
    'L3': ('L7', 1, None, None), 'L4': ('L8', 1, None, None),
    'L5': ('L9', 1, None, None), 'L6': ('L9', 2, None, None),
    'L7': ('L10', 1, None, None), 'L8': ('L10', 2, None, None),
    'L9': ('L11', 1, None, None), 'L10': ('L12', 1, None, None),
    'L11': ('L13', 1, None, None), 'L12': ('L13', 2, None, None),
    'L13': ('L14', 1, None, None),
    'L14': ('GF', 2, None, None),
    'GF': (None, None, None, None)
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY AUTOINCREMENT, season TEXT, name TEXT UNIQUE, p1 TEXT, p2 TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches (season TEXT, match_id TEXT, t1_id INTEGER DEFAULT -1, t2_id INTEGER DEFAULT -1, score1 INTEGER DEFAULT 0, score2 INTEGER DEFAULT 0, is_completed INTEGER DEFAULT 0, PRIMARY KEY (season, match_id))''')
    conn.commit()
    return conn

def get_or_create_season(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT season FROM teams UNION SELECT DISTINCT season FROM matches")
    seasons = sorted([row[0] for row in cursor.fetchall() if row[0]], reverse=True)
    print("\n--- Season Selection ---")
    if seasons:
        for i, s in enumerate(seasons, 1): print(f"[{i}] {s}")
    else: print("No seasons found.")
    
    user_input = input("\nEnter season number, or type a new season: ").strip()
    if user_input.isdigit() and 1 <= int(user_input) <= len(seasons): return seasons[int(user_input) - 1]
    return user_input.title()

def register_team(conn, season):
    print(f"\n--- Register Team for {season} ---")
    
    name = ""
    while not name:
        name = input("Team Name: ").strip()
        
    p1 = ""
    while not p1:
        p1 = input("Player 1 Name: ").strip()
        
    p2 = ""
    while not p2:
        p2 = input("Player 2 Name: ").strip()
        
    try:
        conn.cursor().execute("INSERT INTO teams (season, name, p1, p2) VALUES (?, ?, ?, ?)", (season, name, p1, p2))
        conn.commit()
        print("Team registered successfully!")
    except sqlite3.IntegrityError:
        print("Error: Team name already exists.")

def edit_team(conn, season):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, p1, p2 FROM teams WHERE season = ?", (season,))
    teams = cursor.fetchall()
    
    if not teams:
        print("No teams registered for this season.")
        return

    print(f"\n--- Edit Team for {season} ---")
    for i, t in enumerate(teams, 1):
        print(f"[{i}] {t[1]} ({t[2]} & {t[3]})")
        
    choice = input("\nEnter team number to edit (or press Enter to cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(teams)):
        return
        
    team = teams[int(choice) - 1]
    team_id = team[0]
    
    print("\nEnter new values (leave blank to keep current value):")
    new_name = input(f"Team Name [{team[1]}]: ").strip()
    new_p1 = input(f"Player 1 [{team[2]}]: ").strip()
    new_p2 = input(f"Player 2 [{team[3]}]: ").strip()
    
    new_name = new_name if new_name else team[1]
    new_p1 = new_p1 if new_p1 else team[2]
    new_p2 = new_p2 if new_p2 else team[3]
    
    try:
        cursor.execute("UPDATE teams SET name = ?, p1 = ?, p2 = ? WHERE id = ?", (new_name, new_p1, new_p2, team_id))
        conn.commit()
        print("Team updated successfully!")
    except sqlite3.IntegrityError:
        print("Error: That team name is already taken.")

def delete_team(conn, season):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, p1, p2 FROM teams WHERE season = ?", (season,))
    teams = cursor.fetchall()
    
    if not teams:
        print("No teams registered for this season.")
        return

    print(f"\n--- Delete Team for {season} ---")
    for i, t in enumerate(teams, 1):
        print(f"[{i}] {t[1]} ({t[2]} & {t[3]})")
        
    choice = input("\nEnter team number to delete (or press Enter to cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(teams)):
        return
        
    team = teams[int(choice) - 1]
    team_id = team[0]
    
    confirm = input(f"Are you sure you want to completely delete '{team[1]}'? (Y/N): ").strip().upper()
    if confirm == 'Y':
        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        # Remove them from any active matches just in case the bracket was already seeded
        cursor.execute("UPDATE matches SET t1_id = -1 WHERE t1_id = ?", (team_id,))
        cursor.execute("UPDATE matches SET t2_id = -1 WHERE t2_id = ?", (team_id,))
        conn.commit()
        print(f"Team '{team[1]}' deleted successfully! (If bracket was already seeded, please re-seed it now).")
    else:
        print("Deletion cancelled.")

def push_to_match(conn, season, target_match, slot, team_id):
    if target_match:
        col = 't1_id' if slot == 1 else 't2_id'
        conn.cursor().execute(f"UPDATE matches SET {col} = ? WHERE season = ? AND match_id = ?", (team_id, season, target_match))

def auto_resolve_byes(conn, season):
    cursor = conn.cursor()
    resolving = True
    while resolving:
        resolving = False
        cursor.execute("SELECT match_id, t1_id, t2_id FROM matches WHERE season = ? AND is_completed = 0 AND t1_id != -1 AND t2_id != -1", (season,))
        for match_id, t1, t2 in cursor.fetchall():
            if t1 == 0 or t2 == 0:  # 0 represents a BYE
                resolving = True
                winner = t1 if t2 == 0 else t2
                loser = 0
                cursor.execute("UPDATE matches SET is_completed = 1, score1 = ?, score2 = ? WHERE season = ? AND match_id = ?", (1 if winner == t1 else 0, 1 if winner == t2 else 0, season, match_id))
                win_target, win_slot, lose_target, lose_slot = ROUTING[match_id]
                push_to_match(conn, season, win_target, win_slot, winner)
                push_to_match(conn, season, lose_target, lose_slot, loser)
                conn.commit()

def seed_bracket(conn, season):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teams WHERE season = ?", (season,))
    teams = [r[0] for r in cursor.fetchall()]
    
    if not teams:
        print("No teams registered.")
        return
    if len(teams) > 16:
        print("Error: Maximum 16 teams supported.")
        return

    # Pad empty slots with BYE (id=0)
    teams += [0] * (16 - len(teams))
    # Standard 16-team seeding distribution
    seeds = [teams[0], teams[15], teams[7], teams[8], teams[3], teams[12], teams[4], teams[11], teams[1], teams[14], teams[6], teams[9], teams[2], teams[13], teams[5], teams[10]]
    
    cursor.execute("DELETE FROM matches WHERE season = ?", (season,))
    
    for match_id in ROUTING.keys():
        cursor.execute("INSERT INTO matches (season, match_id) VALUES (?, ?)", (season, match_id))
        
    for i in range(8):
        match_id = f"W{i+1}"
        cursor.execute("UPDATE matches SET t1_id = ?, t2_id = ? WHERE season = ? AND match_id = ?", (seeds[i*2], seeds[i*2+1], season, match_id))
        
    conn.commit()
    auto_resolve_byes(conn, season)
    print("\nBracket seeded and BYEs resolved automatically!")

def enter_scores(conn, season):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.match_id, t1.name, t2.name, m.t1_id, m.t2_id 
        FROM matches m
        JOIN teams t1 ON m.t1_id = t1.id
        JOIN teams t2 ON m.t2_id = t2.id
        WHERE m.season = ? AND m.is_completed = 0 AND m.t1_id > 0 AND m.t2_id > 0
    ''', (season,))
    
    active_matches = cursor.fetchall()
    if not active_matches:
        print("No matches currently available to play.")
        return
        
    print("\n--- Active Matches ---")
    for match_id, n1, n2, _, _ in active_matches:
        print(f"[{match_id}] {n1} vs {n2}")
        
    m_id = input("\nEnter Match ID to score: ").strip().upper()
    match = next((m for m in active_matches if m[0] == m_id), None)
    
    if match:
        try:
            s1 = int(input(f"Goals for {match[1]}: "))
            s2 = int(input(f"Goals for {match[2]}: "))
            winner = match[3] if s1 > s2 else match[4]
            loser = match[4] if s1 > s2 else match[3]
            
            cursor.execute("UPDATE matches SET score1 = ?, score2 = ?, is_completed = 1 WHERE season = ? AND match_id = ?", (s1, s2, season, m_id))
            win_target, win_slot, lose_target, lose_slot = ROUTING[m_id]
            push_to_match(conn, season, win_target, win_slot, winner)
            push_to_match(conn, season, lose_target, lose_slot, loser)
            conn.commit()
            
            auto_resolve_byes(conn, season)
            print("Score saved and bracket advanced!")
        except ValueError:
            print("Invalid score. Please enter numbers.")
    else:
        print("Invalid Match ID.")

def main():
    conn = init_db()
    while True:
        print("\n=== Rocket League Tracker ===")
        print("1. Register Team")
        print("2. Edit Team")
        print("3. Delete Team")
        print("4. Generate & Seed Bracket")
        print("5. Enter Match Scores")
        print("6. Update Website")
        print("7. Exit & Update")
        
        choice = input("Select an option: ").strip()
        if choice == '1': register_team(conn, get_or_create_season(conn))
        elif choice == '2': edit_team(conn, get_or_create_season(conn))
        elif choice == '3': delete_team(conn, get_or_create_season(conn))
        elif choice == '4': seed_bracket(conn, get_or_create_season(conn))
        elif choice == '5': enter_scores(conn, get_or_create_season(conn))
        elif choice == '6':
            print("Pushing update...")
            generate_static_website()
        elif choice == '7':
            conn.close()
            generate_static_website()
            break

if __name__ == "__main__":
    main()