import json
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, select, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from login import engine_id

# Create a MetaData instance
engine = create_engine(engine_id)
metadata = MetaData()

# Define the epl_teams_3y table schema
epl_teams_3y = Table(
    'epl_teams_3y', metadata,
    Column('id', String, primary_key=True),  # Composite key (team_id + season_year)
    Column('team_id', Integer),
    Column('team_name', String),
    Column('venue', String),
    Column('founded', Integer),
    Column('tla', String),
    Column('clubColors', String),
    Column('season_year', Integer)
)

# Define the epl_manager_3y table schema
epl_manager_3y = Table(
    'epl_manager_3y', metadata,
    Column('id', String, primary_key=True),  # Composite key (manager_id + season_year)
    Column('manager_id', Integer),
    Column('team_id', Integer),
    Column('manager_name', String),
    Column('date_of_birth', Date),
    Column('nationality', String),
    Column('contract_start', String),
    Column('contract_until', String),
    Column('season_year', Integer)
)

# Define the epl_player_3y table schema
epl_player_3y = Table(
    'epl_player_3y', metadata,
    Column('id', String, primary_key=True),  # Composite key (player_id + season_year)
    Column('player_id', Integer),
    Column('team_id', Integer),
    Column('player_name', String),
    Column('position', String),
    Column('date_of_birth', Date),
    Column('nationality', String),
    Column('season_year', Integer)
)

# Drop the existing tables if they exist and recreate them
epl_teams_3y.drop(engine, checkfirst=True)
epl_manager_3y.drop(engine, checkfirst=True)
epl_player_3y.drop(engine, checkfirst=True)
metadata.create_all(engine)

# Function to insert data into the epl_teams_3y table
def insert_team_data(data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for season_data in data:
                season_year = season_data['filters']['season']
                for team in season_data['teams']:
                    team_id = team['id']
                    composite_id = f"{team_id}_{season_year}"  # Create composite ID
                    # Check if the record already exists
                    existing_record = connection.execute(
                        select(epl_teams_3y).where(
                            epl_teams_3y.c.id == composite_id
                        )
                    ).fetchone()

                    if existing_record:
                        print(f"Record for {team['name']} in season {season_year} already exists. Skipping.")
                        continue  # Skip to the next record if it already exists

                    record = {
                        'id': composite_id,  # Use composite ID
                        'team_id': team_id,
                        'team_name': team['name'],
                        'venue': team.get('venue', None),
                        'founded': team.get('founded', None),
                        'tla': team.get('tla', None),
                        'clubColors': team.get('clubColors', None),
                        'season_year': int(season_year)
                    }
                    connection.execute(epl_teams_3y.insert().values(record))
                    print(f"Inserted record for {record['team_name']} in season {season_year}")

            transaction.commit()  # Commit the transaction after all inserts
        except IntegrityError as e:
            print(f"Integrity error: {e}. Rolling back transaction.")
            transaction.rollback()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy error: {e}. Rolling back transaction.")
            transaction.rollback()

# Function to insert data into the epl_manager_3y table
def insert_manager_data(data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for season_data in data:
                season_year = season_data['filters']['season']
                for team in season_data['teams']:
                    coach = team.get('coach', None)
                    if coach:
                        manager_id = coach['id']
                        composite_id = f"{manager_id}_{season_year}"  # Create composite ID
                        # Check if the record already exists
                        existing_record = connection.execute(
                            select(epl_manager_3y).where(
                                epl_manager_3y.c.id == composite_id
                            )
                        ).fetchone()

                        if existing_record:
                            print(f"Record for {coach['name']} in season {season_year} already exists. Skipping.")
                            continue  # Skip to the next record if it already exists

                        record = {
                            'id': composite_id,  # Use composite ID
                            'manager_id': manager_id,
                            'team_id': team['id'],
                            'manager_name': coach['name'],
                            'date_of_birth': coach.get('dateOfBirth', None),
                            'nationality': coach.get('nationality', None),
                            'contract_start': coach.get('contract', {}).get('start', None),
                            'contract_until': coach.get('contract', {}).get('until', None),
                            'season_year': int(season_year)
                        }
                        connection.execute(epl_manager_3y.insert().values(record))
                        print(f"Inserted record for {record['manager_name']} in season {season_year}")

            transaction.commit()  # Commit the transaction after all inserts
        except IntegrityError as e:
            print(f"Integrity error: {e}. Rolling back transaction.")
            transaction.rollback()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy error: {e}. Rolling back transaction.")
            transaction.rollback()

# Function to insert data into the epl_player_3y table
def insert_player_data(data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for season_data in data:
                season_year = season_data['filters']['season']
                for team in season_data['teams']:
                    for player in team.get('squad', []):
                        player_id = player['id']
                        composite_id = f"{player_id}_{season_year}"  # Create composite ID
                        # Check if the record already exists
                        existing_record = connection.execute(
                            select(epl_player_3y).where(
                                epl_player_3y.c.id == composite_id
                            )
                        ).fetchone()

                        if existing_record:
                            print(f"Record for {player['name']} in season {season_year} already exists. Skipping.")
                            continue  # Skip to the next record if it already exists

                        record = {
                            'id': composite_id,  # Use composite ID
                            'player_id': player_id,
                            'team_id': team['id'],
                            'player_name': player['name'],
                            'position': player.get('position', None),
                            'date_of_birth': player.get('dateOfBirth', None),
                            'nationality': player.get('nationality', None),
                            'season_year': int(season_year)
                        }
                        connection.execute(epl_player_3y.insert().values(record))
                        print(f"Inserted record for {record['player_name']} in season {season_year}")

            transaction.commit()  # Commit the transaction after all inserts
        except IntegrityError as e:
            print(f"Integrity error: {e}. Rolling back transaction.")
            transaction.rollback()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy error: {e}. Rolling back transaction.")
            transaction.rollback()

# Load the data from the JSON file
with open('/app/data/data/competition_teams_3y.json', 'r') as file:

    data = json.load(file)

# Insert data into the tables
insert_team_data(data)
insert_manager_data(data)
insert_player_data(data)
