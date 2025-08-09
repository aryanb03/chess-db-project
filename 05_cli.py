#!/usr/bin/env python3
"""
Chess DB CLI (SQLite demo)
- Creates DB from schema + sample data if not present
- Simple commands:
  list players | list tournaments | standings <tournament>
  h2h <playerA> <playerB> | games <player>
  add tournament | add player | add game
"""
import sqlite3, os, sys, textwrap

DB_FILE = os.path.join(os.path.dirname(__file__), "chess.db")
SCHEMA = os.path.join(os.path.dirname(__file__), "03_schema_and_sample_data.sql")

def ensure_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        with open(SCHEMA, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

def q(conn, sql, params=()):
    cur = conn.execute(sql, params)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    return cols, rows

def pretty(cols, rows):
    if not rows:
        print("(no rows)")
        return
    widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0)) for i,c in enumerate(cols)]
    print(" | ".join(str(c).ljust(widths[i]) for i,c in enumerate(cols)))
    print("-+-".join("-"*w for w in widths))
    for r in rows:
        print(" | ".join(str(r[i]).ljust(widths[i]) for i in range(len(cols))))

def list_players(conn):
    cols, rows = q(conn, "SELECT PlayerID, FullName, Country, Title FROM Player ORDER BY FullName;")
    pretty(cols, rows)

def list_tournaments(conn):
    cols, rows = q(conn, "SELECT TournamentID, Name, Location, StartDate, Category FROM Tournament ORDER BY StartDate;")
    pretty(cols, rows)

def standings(conn, tournament_name):
    sql = """
    SELECT p.FullName, pt.Points, pt.FinalRank, pt.PerformanceRating
    FROM Participation pt
    JOIN Player p ON pt.PlayerID = p.PlayerID
    JOIN Tournament t ON pt.TournamentID = t.TournamentID
    WHERE t.Name = ?
    ORDER BY pt.Points DESC, pt.FinalRank ASC;
    """
    cols, rows = q(conn, sql, (tournament_name,))
    pretty(cols, rows)

def h2h(conn, a, b):
    sql = """
    SELECT t.Name, g.RoundNumber, w.FullName AS White, b.FullName AS Black, g.Result, g.OpeningName
    FROM Game g
    JOIN Player w ON g.WhitePlayerID = w.PlayerID
    JOIN Player b ON g.BlackPlayerID = b.PlayerID
    JOIN Tournament t ON g.TournamentID = t.TournamentID
    WHERE (w.FullName = ? AND b.FullName = ?) OR (w.FullName = ? AND b.FullName = ?)
    ORDER BY t.StartDate, g.RoundNumber;
    """
    cols, rows = q(conn, sql, (a,b,b,a))
    pretty(cols, rows)

def games_of(conn, name):
    sql = """
    SELECT t.Name, g.RoundNumber, w.FullName AS White, b.FullName AS Black, g.Result, g.OpeningName
    FROM Game g
    JOIN Player w ON g.WhitePlayerID = w.PlayerID
    JOIN Player b ON g.BlackPlayerID = b.PlayerID
    JOIN Tournament t ON g.TournamentID = t.TournamentID
    WHERE w.FullName = ? OR b.FullName = ?
    ORDER BY t.StartDate, g.RoundNumber;
    """
    cols, rows = q(conn, sql, (name, name))
    pretty(cols, rows)

def add_player(conn):
    name = input("Full name: ").strip()
    country = input("Country (3-letter): ").strip().upper()
    fide = input("FIDE ID: ").strip()
    title = input("Title (GM/IM/FM): ").strip().upper()
    birth = input("Birth year: ").strip() or None
    conn.execute("INSERT INTO Player (FullName, Country, FIDEID, Title, BirthYear) VALUES (?,?,?,?,?)",
                 (name, country, fide, title, birth))
    conn.commit()
    print("Added.")

def add_tournament(conn):
    name = input("Name: ").strip()
    loc = input("Location: ").strip()
    start = input("Start date (YYYY-MM-DD): ").strip()
    end = input("End date (YYYY-MM-DD): ").strip()
    org = input("Organizer: ").strip() or "Grand Chess Tour"
    cat = input("Category (Classical/Rapid/Blitz/Mixed): ").strip().title()
    conn.execute("INSERT INTO Tournament (Name, Location, StartDate, EndDate, Organizer, Category) VALUES (?,?,?,?,?,?)",
                 (name, loc, start, end, org, cat))
    conn.commit()
    print("Added.")

def add_game(conn):
    print("Enter game details:")
    tname = input("Tournament name: ").strip()
    roundn = int(input("Round number: ").strip())
    white = input("White player full name: ").strip()
    black = input("Black player full name: ").strip()
    result = input("Result (1-0/0-1/1/2-1/2): ").strip()
    eco = input("ECO code: ").strip().upper()
    opening = input("Opening name: ").strip()
    moves = int(input("Moves count: ").strip())

    # Resolve IDs
    cur = conn.execute("SELECT TournamentID FROM Tournament WHERE Name = ?", (tname,))
    trow = cur.fetchone()
    if not trow:
        print("Tournament not found.")
        return
    tid = trow[0]
    cur = conn.execute("SELECT PlayerID FROM Player WHERE FullName = ?", (white,))
    wrow = cur.fetchone()
    if not wrow:
        print("White player not found.")
        return
    wid = wrow[0]
    cur = conn.execute("SELECT PlayerID FROM Player WHERE FullName = ?", (black,))
    brow = cur.fetchone()
    if not brow:
        print("Black player not found.")
        return
    bid = brow[0]

    conn.execute("""INSERT INTO Game 
      (TournamentID, RoundNumber, WhitePlayerID, BlackPlayerID, Result, ECOCode, OpeningName, MovesCount)
      VALUES (?,?,?,?,?,?,?,?)""", (tid, roundn, wid, bid, result, eco, opening, moves))
    conn.commit()
    print("Added.")

def help():
    print(textwrap.dedent("""\
    Commands:
      help
      list players
      list tournaments
      standings <tournament name>
      h2h <player A> <player B>
      games <player full name>
      add player
      add tournament
      add game
      quit
    """))

def main():
    ensure_db()
    conn = sqlite3.connect(DB_FILE)
    print("Chess DB CLI — type 'help' for commands")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd: 
            continue
        if cmd == "quit":
            break
        if cmd == "help":
            help()
        elif cmd == "list players":
            list_players(conn)
        elif cmd == "list tournaments":
            list_tournaments(conn)
        elif cmd.startswith("standings "):
            name = cmd[len("standings "):].strip()
            standings(conn, name)
        elif cmd.startswith("h2h "):
            parts = cmd.split(" ", 2)
            if len(parts) < 3:
                print("Usage: h2h <player A> <player B>")
            else:
                a, b = parts[1], parts[2]
                h2h(conn, a, b)
        elif cmd.startswith("games "):
            name = cmd[len("games "):].strip()
            games_of(conn, name)
        elif cmd == "add player":
            add_player(conn)
        elif cmd == "add tournament":
            add_tournament(conn)
        elif cmd == "add game":
            add_game(conn)
        else:
            print("Unknown command. Type 'help'.")
    conn.close()

if __name__ == "__main__":
    main()
