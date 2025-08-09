
-- Example Analytical Queries

-- Q1: Top 5 players by average performance rating in 2024
SELECT p.FullName, AVG(pt.PerformanceRating) AS AvgPerf
FROM Player p
JOIN Participation pt ON p.PlayerID = pt.PlayerID
JOIN Tournament t ON pt.TournamentID = t.TournamentID
WHERE strftime('%Y', t.StartDate) = '2024'
GROUP BY p.FullName
ORDER BY AvgPerf DESC
LIMIT 5;

-- Q2: All games between Carlsen and Caruana (any color)
SELECT t.Name, g.RoundNumber, w.FullName AS White, b.FullName AS Black, g.Result, g.OpeningName
FROM Game g
JOIN Player w ON g.WhitePlayerID = w.PlayerID
JOIN Player b ON g.BlackPlayerID = b.PlayerID
JOIN Tournament t ON g.TournamentID = t.TournamentID
WHERE (w.FullName = 'Magnus Carlsen' AND b.FullName = 'Fabiano Caruana')
   OR (w.FullName = 'Fabiano Caruana' AND b.FullName = 'Magnus Carlsen')
ORDER BY t.StartDate, g.RoundNumber;

-- Q3: Rating trend data for a player (Carlsen)
SELECT Date, ClassicalRating, RapidRating, BlitzRating
FROM RatingHistory
JOIN Player USING(PlayerID)
WHERE FullName = 'Magnus Carlsen'
ORDER BY Date ASC;

-- Q4: Tournament standings (by points) for a selected event (Sinquefield Cup)
SELECT t.Name AS Tournament, p.FullName, pt.Points, pt.FinalRank, pt.PerformanceRating
FROM Participation pt
JOIN Player p ON pt.PlayerID = p.PlayerID
JOIN Tournament t ON pt.TournamentID = t.TournamentID
WHERE t.Name = 'Sinquefield Cup'
ORDER BY pt.Points DESC, pt.FinalRank ASC;

-- Q5: Most frequent openings across all games (top 5)
SELECT OpeningName, COUNT(*) as Games
FROM Game
GROUP BY OpeningName
ORDER BY Games DESC
LIMIT 5;

-- Q6: Head-to-head score table (Carlsen vs Nakamura)
SELECT 
  SUM(CASE WHEN g.WhitePlayerID = w.PlayerID AND g.Result = '1-0' THEN 1
           WHEN g.BlackPlayerID = w.PlayerID AND g.Result = '0-1' THEN 1 ELSE 0 END) AS Wins_W,
  SUM(CASE WHEN g.Result = '1/2-1/2' THEN 1 ELSE 0 END) AS Draws,
  SUM(CASE WHEN g.WhitePlayerID = b.PlayerID AND g.Result = '1-0' THEN 1
           WHEN g.BlackPlayerID = b.PlayerID AND g.Result = '0-1' THEN 1 ELSE 0 END) AS Wins_B
FROM Game g
JOIN Player w ON w.FullName = 'Magnus Carlsen'
JOIN Player b ON b.FullName = 'Hikaru Nakamura';
