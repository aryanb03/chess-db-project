#!/usr/bin/env python3
"""
06_etl_from_pgn.py
Load real tournament games from PGN (local files or URLs) into the chess DB.

- No third-party libraries required.
- Parses standard PGN headers to populate Tournament, Player, Game.
- Builds Participation (points, rank) from inserted games.
- Leaves PerformanceRating and AvgOpponentRating NULL (optional future step).

USAGE
-----
1) Put PGN files into a folder named `pgn/` OR add remote PGN URLs to `06_sources.json`.
2) Run:
   python3 06_etl_from_pgn.py

CONFIG
------
Edit 06_sources.json, e.g.:
{
  "urls": [
    "https://example.com/sinquefield_2024.pgn",
    "https://example.com/saintlouis_rapid_blitz_2024.pgn"
  ],
  "files": [
    "pgn/superbet_2024.pgn"
  ]
}

NOTES
-----
- Tournament mapped from PGN tag [Event "…"].
- Date from [Date "YYYY.MM.DD"] (uses first game's date as tournament start).
- Location best-effort from [Site "…"].
- Result mapped 1-0 / 0-1 / 1/2-1/2.
- ECO/Opening from PGN tags if present.
"""

import os, json, urllib.request, sqlite3, re
from datetime import datetime
from urllib.parse import urlparse

DB_FILE = os.path.join(os.path.dirname(__file__), "chess.db")
SCHEMA = os.path.join(os.path.dirname(__file__), "03_schema_and_sample_data.sql")
SOURCES_JSON = os.path.join(os.path.dirname(__file__), "06_sources.json")

def ensure_db():
    need_bootstrap = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    if need_bootstrap:
        with open(SCHEMA, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    return conn

def read_sources():
    urls, files = [], []
    if os.path.exists(SOURCES_JSON):
        with open(SOURCES_JSON, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        urls = cfg.get("urls", [])
        files = cfg.get("files", [])
    # also auto-add all .pgn in ./pgn
    pgn_dir = os.path.join(os.path.dirname(__file__), "pgn")
    if os.path.isdir(pgn_dir):
        for name in os.listdir(pgn_dir):
            if name.lower().endswith(".pgn"):
                files.append(os.path.join(pgn_dir, name))
    return urls, files

def fetch_url(url):
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

HEADER_RE = re.compile(r'^\[(\w+)\s+"([^"]*)"\]\s*$', re.M)

def split_games(pgn_text):
    # Split on blank line between header and moves; games typically separated by blank lines
    # A more robust split: each game starts with a header like [Event "..."]
    parts = re.split(r'\n(?=\[Event\s+")', pgn_text.strip())
    return [p for p in parts if p.strip()]

def parse_headers(game_text):
    headers = dict(HEADER_RE.findall(game_text))
    return headers

def parse_moves_count(game_text):
    # crude count: number of move numbers like "1.", "2.", etc.
    # fallback to half-move count based on spaces after result line
    nums = re.findall(r'\b\d+\.(?:\.\.)?', game_text)
    return len(nums) if nums else None

def upsert_player(conn, name):
    cur = conn.execute("SELECT PlayerID FROM Player WHERE FullName = ?", (name,))
    row = cur.fetchone()
    if row: return row[0]
    conn.execute("INSERT INTO Player (FullName, Title) VALUES (?, ?)", (name, None))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_or_create_tournament(conn, name, site, date_str):
    # Try to parse date
    start = None
    if date_str and date_str != "????.??.??":
        try:
            start = datetime.strptime(date_str, "%Y.%m.%d").date()
        except Exception:
            start = None
    cur = conn.execute("SELECT TournamentID FROM Tournament WHERE Name = ?", (name,))
    row = cur.fetchone()
    if row: return row[0]
    conn.execute(
        "INSERT INTO Tournament (Name, Location, StartDate, Organizer, Category) VALUES (?,?,?,?,?)",
        (name, site or None, str(start) if start else None, "Imported via ETL", None))
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def insert_game(conn, tid, round_no, white_id, black_id, result, eco, opening, moves):
    # dedupe by (tid, round, white_id, black_id, result) best effort
    cur = conn.execute("""SELECT GameID FROM Game 
                          WHERE TournamentID=? AND RoundNumber=? AND WhitePlayerID=? 
                            AND BlackPlayerID=? AND Result=?""",
                       (tid, round_no, white_id, black_id, result))
    if cur.fetchone():
        return
    conn.execute("""INSERT INTO Game (TournamentID, RoundNumber, WhitePlayerID, BlackPlayerID, Result, ECOCode, OpeningName, MovesCount)
                    VALUES (?,?,?,?,?,?,?,?)""",
                 (tid, round_no, white_id, black_id, result, eco, opening, moves))
    conn.commit()

def rebuild_participation(conn, tid):
    # aggregate points from Game per player (1 win, 0.5 draw, 0 loss)
    # Compute per tournament
    sql = """
    WITH results AS (
      SELECT WhitePlayerID as PID,
             CASE Result WHEN '1-0' THEN 1.0 WHEN '1/2-1/2' THEN 0.5 ELSE 0 END AS pts
      FROM Game WHERE TournamentID = ?
      UNION ALL
      SELECT BlackPlayerID as PID,
             CASE Result WHEN '0-1' THEN 1.0 WHEN '1/2-1/2' THEN 0.5 ELSE 0 END AS pts
      FROM Game WHERE TournamentID = ?
    ),
    sums AS (
      SELECT PID as PlayerID, SUM(pts) AS Points FROM results GROUP BY PID
    ),
    ranked AS (
      SELECT PlayerID, Points,
             DENSE_RANK() OVER (ORDER BY Points DESC) AS rnk
      FROM sums
    )
    SELECT PlayerID, Points, rnk FROM ranked ORDER BY Points DESC, PlayerID;
    """
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.execute(sql, (tid, tid))
    rows = cur.fetchall()
    for pid, pts, rnk in rows:
        # upsert participation
        cur2 = conn.execute("SELECT ParticipationID FROM Participation WHERE PlayerID=? AND TournamentID=?",
                            (pid, tid))
        if cur2.fetchone():
            conn.execute("UPDATE Participation SET Points=?, FinalRank=? WHERE PlayerID=? AND TournamentID=?",
                         (pts, rnk, pid, tid))
        else:
            conn.execute("""INSERT INTO Participation (PlayerID, TournamentID, Points, FinalRank) 
                            VALUES (?,?,?,?)""", (pid, tid, pts, rnk))
    conn.commit()

def process_pgn_text(conn, text):
    games = split_games(text)
    t_seen = set()
    for chunk in games:
        headers = parse_headers(chunk)
        event = headers.get("Event") or "Unknown Event"
        site = headers.get("Site")
        date = headers.get("Date")
        white = headers.get("White")
        black = headers.get("Black")
        result = headers.get("Result")
        eco = headers.get("ECO")
        opening = headers.get("Opening")
        round_no = headers.get("Round")
        try:
            round_no = int(round_no) if round_no and round_no.isdigit() else None
        except Exception:
            round_no = None
        moves = parse_moves_count(chunk)

        tid = get_or_create_tournament(conn, event, site, date)
        wid = upsert_player(conn, white) if white else None
        bid = upsert_player(conn, black) if black else None
        if tid and wid and bid and result:
            insert_game(conn, tid, round_no, wid, bid, result, eco, opening, moves)
            t_seen.add(tid)

    # rebuild participation per tournament touched
    for tid in t_seen:
        rebuild_participation(conn, tid)

def main():
    conn = ensure_db()
    urls, files = read_sources()
    print(f"Found {len(urls)} URL(s) and {len(files)} file(s).")

    for url in urls:
        try:
            print(f"Downloading: {url}")
            txt = fetch_url(url)
            process_pgn_text(conn, txt)
        except Exception as e:
            print(f"Failed: {url} -> {e}")

    for path in files:
        try:
            print(f"Reading file: {path}")
            txt = read_file(path)
            process_pgn_text(conn, txt)
        except Exception as e:
            print(f"Failed: {path} -> {e}")

    print("Done. You can now run `python3 05_cli.py` and query the imported events.")

if __name__ == "__main__":
    main()
