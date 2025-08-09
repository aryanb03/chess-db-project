# Final Project — Chess Performance Database (Top Players / Grand Chess Tour Focus)

**Course:** CS4092 — Database Design and Development (Summer 2025)  
**Student:** Aryan Balyan  
**Date:** 2025-08-08

## 1. Project Overview
This project designs and implements a relational database tracking top chess players (e.g., Grand Chess Tour regulars), their tournament participations, performances, game-level details, and rating histories. The database supports analytical queries for trends, head-to-head results, and per-event performance ratings.

## 2. Users & Use Cases
**Users:** Researchers, chess fans, data analysts, and app developers.  
**Key Use Cases:**
- Search players by name, title, or country.
- Explore a tournament’s standings (points, rank, performance rating).
- Retrieve games between any two players, with results by color and ECO codes.
- Analyze a player’s rating trend over time (classical/rapid/blitz).
- Compare players by average performance rating over a time window.
- Insert new events, participations, and games via a CLI.

## 3. Data Requirements
- **Player**: Name, title (GM/IM/FM), country, FIDE ID, DOB/BirthYear, peak rating/date.
- **Tournament**: Name, location, start/end dates, category (Classical/Rapid/Blitz/Mixed), organizer.
- **Participation** (Player × Tournament): Points, final rank, average opponent rating (AOR), performance rating.
- **Game**: Tournament, round, white/black players, result, moves, opening (ECO + name).
- **RatingHistory**: For each player, dated ratings in classical, rapid, blitz.
- **Integrity**: Foreign keys for references, uniqueness on (FIDEID), sensible types, and indexing on common filters (names, dates).

## 4. Scope & Assumptions
- Dataset focuses on **top players** and **GCT-style events** with representative sample data.
- Ratings and results are illustrative for this academic project (not authoritative). The schema supports importing real data later.
- DBMS-agnostic SQL is provided; the demo uses **SQLite** for simplicity. The same schema can be ported to PostgreSQL/MySQL.

## 5. Non-Functional Requirements
- **Portability:** Standard SQL and simple Python (no third-party deps).
- **Usability:** Clear CLI for CRUD + search.
- **Performance:** Indexes on FK columns and player/tournament lookups.
- **Security:** Local dev scope; no auth/PII beyond public chess facts.

## 6. Success Criteria
- Complete ERD and normalized schema (at least 5 tables).
- SQL script to create and populate sample data.
- CLI demonstrating DB interaction and business logic.
- Run example queries answering meaningful chess questions.
