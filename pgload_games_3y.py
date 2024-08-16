import json
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from login import engine_id

# Create a MetaData instance
engine = create_engine(engine_id)
metadata = MetaData()

# Define the epl_head2head_3y table schema
epl_head2head_3y = Table(
    'epl_head2head_3y', metadata,
    Column('match_id', Integer, primary_key=True),
    Column('season_year', Integer),
    Column('utc_date', String),
    Column('status', String),
    Column('matchday', Integer),
    Column('home_team_id', Integer),
    Column('home_team_name', String),
    Column('away_team_id', Integer),
    Column('away_team_name', String),
    Column('home_score_fulltime', Integer),
    Column('away_score_fulltime', Integer),
    Column('home_score_halftime', Integer),
    Column('away_score_halftime', Integer),
    Column('winner', String),
    Column('referee_id', Integer, ForeignKey('epl_referee_3y.referee_id'))  # Add referee_id with foreign key constraint
)

# Define the epl_referee_3y table schema
epl_referee_3y = Table(
    'epl_referee_3y', metadata,
    Column('referee_id', Integer, primary_key=True),
    Column('name', String),
    Column('nationality', String)
)

# Drop the existing tables if they exist and recreate them
epl_head2head_3y.drop(engine, checkfirst=True)
epl_referee_3y.drop(engine, checkfirst=True)
metadata.create_all(engine)

# Function to insert data into the tables
def insert_match_and_referee_data(data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for season_data in data:
                season_year = season_data['filters']['season']  # Extract season year from filters
                
                for match in season_data['matches']:
                    # Insert referee data first
                    for referee in match['referees']:
                        referee_record = {
                            'referee_id': referee['id'],
                            'name': referee['name'],
                            'nationality': referee.get('nationality', 'Unknown')
                        }
                        existing_referee = connection.execute(
                            select(epl_referee_3y).where(
                                epl_referee_3y.c.referee_id == referee_record['referee_id']
                            )
                        ).fetchone()
                        if existing_referee:
                            print(f"Referee {referee_record['name']} already exists. Skipping.")
                        else:
                            connection.execute(epl_referee_3y.insert().values(referee_record))
                            print(f"Inserted referee {referee_record['name']}")

                    # Now insert match data
                    referee_id = match['referees'][0]['id'] if match['referees'] else None
                    match_record = {
                        'match_id': match['id'],
                        'season_year': season_year,
                        'utc_date': match['utcDate'],
                        'status': match['status'],
                        'matchday': match['matchday'],
                        'home_team_id': match['homeTeam']['id'],
                        'home_team_name': match['homeTeam']['name'],
                        'away_team_id': match['awayTeam']['id'],
                        'away_team_name': match['awayTeam']['name'],
                        'home_score_fulltime': match['score']['fullTime']['home'],
                        'away_score_fulltime': match['score']['fullTime']['away'],
                        'home_score_halftime': match['score']['halfTime']['home'],
                        'away_score_halftime': match['score']['halfTime']['away'],
                        'winner': match['score']['winner'],
                        'referee_id': referee_id
                    }
                    existing_match = connection.execute(
                        select(epl_head2head_3y).where(
                            epl_head2head_3y.c.match_id == match_record['match_id']
                        )
                    ).fetchone()
                    if existing_match:
                        print(f"Match {match_record['match_id']} already exists. Skipping.")
                    else:
                        connection.execute(epl_head2head_3y.insert().values(match_record))
                        print(f"Inserted match {match_record['match_id']} for season {season_year}")

            transaction.commit()  # Commit the transaction after all inserts
        except IntegrityError as e:
            print(f"Integrity error: {e}. Rolling back transaction.")
            transaction.rollback()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy error: {e}. Rolling back transaction.")
            transaction.rollback()

# Load the data from the JSON file
with open('/app/data/data/last_season_games_3y.json', 'r') as file:

    data = json.load(file)

# Insert data into the tables
insert_match_and_referee_data(data)
