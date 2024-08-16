Dockerized ETL Process for Football Data
Overview
This project automates the process of fetching football data from an external API, storing it in PostgreSQL, and performing ETL (Extract, Transform, Load) operations using Docker containers. The data is then available for querying and analysis.

Project Structure
.
├── Dockerfile
├── docker-compose.yml
├── data/
│   ├── apiload.py
│   ├── pgload_competition_3y.py
│   ├── pgload_games_3y.py
│   ├── pgload_standing_3y.py
│   ├── pgload_topscorers_3y.py
│   ├── login.py
│   └── check_and_run.py
└── README.md

Files
Dockerfile: Contains instructions for building Docker images for the ETL process.
docker-compose.yml: Defines the services required to run the ETL process, including PostgreSQL and the data loading scripts.
data/: Directory containing the Python scripts used for fetching and loading data.
apiload.py: Fetches data from the football API and saves it as JSON files.
pgload_competition_3y.py: Loads competition data into PostgreSQL.
pgload_games_3y.py: Loads game data into PostgreSQL.
pgload_standing_3y.py: Loads standings data into PostgreSQL.
pgload_topscorers_3y.py: Loads top scorer data into PostgreSQL.
login.py: Contains API keys and database credentials.
check_and_run.py: Utility script to check for the existence of JSON files before running the ETL scripts.