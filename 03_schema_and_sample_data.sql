
-- Chess DB Schema (SQLite-compatible). Port to Postgres/MySQL if needed.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS Participation;
DROP TABLE IF EXISTS RatingHistory;
DROP TABLE IF EXISTS Tournament;
DROP TABLE IF EXISTS Player;

CREATE TABLE Player (
  PlayerID INTEGER PRIMARY KEY AUTOINCREMENT,
  FullName TEXT NOT NULL,
  Country  TEXT,
  BirthYear INTEGER,
  FIDEID   TEXT UNIQUE,
  Title    TEXT,
  PeakRating INTEGER,
  PeakRatingDate DATE
);

CREATE TABLE Tournament (
  TournamentID INTEGER PRIMARY KEY AUTOINCREMENT,
  Name        TEXT NOT NULL,
  Location    TEXT,
  StartDate   DATE,
  EndDate     DATE,
  Organizer   TEXT,
  Category    TEXT
);

CREATE TABLE Participation (
  ParticipationID INTEGER PRIMARY KEY AUTOINCREMENT,
  PlayerID    INTEGER NOT NULL REFERENCES Player(PlayerID),
  TournamentID INTEGER NOT NULL REFERENCES Tournament(TournamentID),
  FinalRank   INTEGER,
  Points      REAL,
  AvgOpponentRating INTEGER,
  PerformanceRating INTEGER,
  UNIQUE (PlayerID, TournamentID)
);

CREATE TABLE Game (
  GameID INTEGER PRIMARY KEY AUTOINCREMENT,
  TournamentID INTEGER NOT NULL REFERENCES Tournament(TournamentID),
  RoundNumber INTEGER,
  WhitePlayerID INTEGER NOT NULL REFERENCES Player(PlayerID),
  BlackPlayerID INTEGER NOT NULL REFERENCES Player(PlayerID),
  Result TEXT,
  ECOCode TEXT,
  OpeningName TEXT,
  MovesCount INTEGER
);

CREATE TABLE RatingHistory (
  RatingID INTEGER PRIMARY KEY AUTOINCREMENT,
  PlayerID INTEGER NOT NULL REFERENCES Player(PlayerID),
  Date     DATE NOT NULL,
  ClassicalRating INTEGER,
  RapidRating INTEGER,
  BlitzRating INTEGER,
  UNIQUE (PlayerID, Date)
);

-- Sample Players
INSERT INTO Player (FullName, Country, BirthYear, FIDEID, Title, PeakRating, PeakRatingDate) VALUES
('Magnus Carlsen', 'NOR', 1990, '1503014', 'GM', 2882, '2014-05-01'),
('Fabiano Caruana', 'USA', 1992, '2020009', 'GM', 2844, '2014-10-01'),
('Hikaru Nakamura', 'USA', 1987, '2016192', 'GM', 2816, '2015-10-01'),
('Ian Nepomniachtchi', 'FID', 1990, '4168119', 'GM', 2795, '2021-05-01'),
('Ding Liren', 'CHN', 1992, '8603677', 'GM', 2816, '2018-11-01'),
('Wesley So', 'USA', 1993, '5202213', 'GM', 2822, '2017-03-01');

-- Sample Tournaments (GCT-style)
INSERT INTO Tournament (Name, Location, StartDate, EndDate, Organizer, Category) VALUES
('Superbet Chess Classic', 'Bucharest, Romania', '2024-05-06', '2024-05-15', 'Grand Chess Tour', 'Classical'),
('Saint Louis Rapid & Blitz', 'Saint Louis, USA', '2024-08-12', '2024-08-18', 'Grand Chess Tour', 'Mixed'),
('Sinquefield Cup', 'Saint Louis, USA', '2024-11-18', '2024-11-28', 'Grand Chess Tour', 'Classical');

-- Participation (illustrative numbers)
-- Get Player and Tournament IDs
-- For SQLite demo simplicity, assume AUTOINC ids by insertion order.
-- Players: 1=Carlsen,2=Caruana,3=Nakamura,4=Nepo,5=Ding,6=So
-- Tournaments: 1=Superbet, 2=STL Rapid&Blitz, 3=Sinquefield

INSERT INTO Participation (PlayerID, TournamentID, FinalRank, Points, AvgOpponentRating, PerformanceRating) VALUES
(1,1,1,6.5,2775,2840),
(2,1,2,6.0,2768,2810),
(3,1,4,5.0,2760,2760),
(4,1,3,5.5,2765,2790),
(5,1,5,4.5,2750,2740),
(6,1,6,4.0,2745,2720),

(1,2,2,22.5,2750,2820),
(2,2,3,21.0,2742,2790),
(3,2,1,24.0,2758,2850),
(4,2,5,18.0,2735,2730),
(5,2,4,19.0,2740,2760),
(6,2,6,16.5,2720,2700),

(1,3,1,7.0,2780,2860),
(2,3,3,5.5,2760,2790),
(3,3,2,6.0,2765,2810),
(4,3,4,5.0,2758,2760),
(5,3,6,4.0,2740,2720),
(6,3,5,4.5,2745,2730);

-- Games (illustrative)
INSERT INTO Game (TournamentID, RoundNumber, WhitePlayerID, BlackPlayerID, Result, ECOCode, OpeningName, MovesCount) VALUES
(1,1,1,2,'1-0','C65','Ruy Lopez, Berlin Defense',42),
(1,1,3,4,'1/2-1/2','D37','QGD, Hastings Variation',31),
(1,1,5,6,'0-1','B90','Sicilian Defense, Najdorf',45),
(1,2,2,1,'1/2-1/2','C67','Ruy Lopez, Berlin, Open',55),
(1,2,4,5,'1-0','E60','King''s Indian Defense',39),
(1,2,6,3,'0-1','A07','Reti Opening',28),

(2,5,3,1,'1-0','A45','Queen''s Pawn Game',60),
(2,7,1,3,'0-1','B30','Sicilian Defense',33),
(2,9,2,1,'1/2-1/2','C88','Ruy Lopez, Closed',52),

(3,4,1,3,'1-0','E54','Nimzo-Indian, 4.e3',41),
(3,7,2,3,'0-1','C11','French Defense, Classical',36),
(3,10,1,2,'1-0','C65','Ruy Lopez, Berlin Defense',47);

-- Rating History (illustrative)
INSERT INTO RatingHistory (PlayerID, Date, ClassicalRating, RapidRating, BlitzRating) VALUES
(1,'2024-05-01',2830,2850,2865),
(1,'2024-08-01',2840,2860,2870),
(1,'2024-12-01',2850,2865,2875),
(2,'2024-05-01',2805,2790,2780),
(2,'2024-08-01',2810,2805,2795),
(2,'2024-12-01',2820,2810,2805),
(3,'2024-05-01',2785,2820,2850),
(3,'2024-08-01',2795,2835,2860),
(3,'2024-12-01',2805,2840,2865);
