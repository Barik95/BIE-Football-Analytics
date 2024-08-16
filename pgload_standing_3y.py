import json
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from sqlalchemy.exc import ProgrammingError, IntegrityError
from login import engine_id

# Create a MetaData instance
engine = create_engine(engine_id)
metadata = MetaData()

# Define the epl_standing_3y table schema
epl_standing_3y = Table(
    'epl_standing_3y', metadata,
    Column('season_year', Integer, primary_key=True),
    Column('team_id', Integer, primary_key=True),
    Column('position', Integer),
    Column('team_name', String),
    Column('team_shortName', String),
    Column('team_tla', String),
    Column('team_crest', String),
    Column('playedGames', Integer),
    Column('form', String),
    Column('won', Integer),
    Column('draw', Integer),
    Column('lost', Integer),
    Column('points', Integer),
    Column('goalsFor', Integer),
    Column('goalsAgainst', Integer),
    Column('goalDifference', Integer)
)

# Create the table in the database if it doesn't exist
metadata.create_all(engine)

# Function to insert data into the table
def insert_data(data):
    with engine.begin() as connection:
        for season_data in data:
            season_year = season_data['filters']['season']
            for standing in season_data['standings']:
                if standing['type'] == 'TOTAL':
                    for team in standing['table']:
                        team_id = team['team']['id']
                        # Check if the record already exists
                        existing_record = connection.execute(
                            select(epl_standing_3y).where(
                                (epl_standing_3y.c.season_year == int(season_year)) &
                                (epl_standing_3y.c.team_id == team_id)
                            )
                        ).fetchone()

                        if existing_record:
                            print(f"Record for {team['team']['name']} in season {season_year} already exists. Skipping.")
                            continue  # Skip to the next record if it already exists

                        record = {
                            'season_year': int(season_year),
                            'team_id': team_id,
                            'position': team['position'],
                            'team_name': team['team']['name'],
                            'team_shortName': team['team']['shortName'],
                            'team_tla': team['team']['tla'],
                            'team_crest': team['team']['crest'],
                            'playedGames': team['playedGames'],
                            'form': team.get('form', None),
                            'won': team['won'],
                            'draw': team['draw'],
                            'lost': team['lost'],
                            'points': team['points'],
                            'goalsFor': team['goalsFor'],
                            'goalsAgainst': team['goalsAgainst'],
                            'goalDifference': team['goalDifference']
                        }
                        try:
                            connection.execute(epl_standing_3y.insert().values(record))
                            print(f"Inserted record for {record['team_name']} in season {season_year}")
                        except (ProgrammingError, IntegrityError) as e:
                            print(f"Error inserting data: {e}")

# Load the data from the JSON file
with open('/app/data/data/competition_standings_3y.json', 'r') as file:

    data = json.load(file)

# Insert data into the table
insert_data(data)
