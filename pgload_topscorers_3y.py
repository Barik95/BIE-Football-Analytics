import json
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from login import engine_id

# Create a MetaData instance
engine = create_engine(engine_id)
metadata = MetaData()

# Define the epl_topscorers_3y table schema
epl_topscorers_3y = Table(
    'epl_topscorers_3y', metadata,
    Column('id', String, primary_key=True),  # Composite key (player_id + season_year)
    Column('player_id', Integer),
    Column('player_name', String),
    Column('team_id', Integer),
    Column('played_matches', Integer),
    Column('goals', Integer),
    Column('assists', Integer),
    Column('penalties', Integer),
    Column('season_year', Integer)
)

# Drop the existing table if it exists and recreate it
epl_topscorers_3y.drop(engine, checkfirst=True)
metadata.create_all(engine)

# Function to insert data into the table
def insert_topscorers_data(data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for season_data in data:
                season_year = season_data['filters']['season']  # Extract season year from filters
                
                for scorer in season_data['scorers']:
                    player_id = scorer['player']['id']
                    composite_id = f"{player_id}_{season_year}"  # Create composite ID
                    # Check if the record already exists
                    existing_record = connection.execute(
                        select(epl_topscorers_3y).where(
                            epl_topscorers_3y.c.id == composite_id
                        )
                    ).fetchone()

                    if existing_record:
                        print(f"Record for {scorer['player']['name']} in season {season_year} already exists. Skipping.")
                        continue  # Skip to the next record if it already exists

                    record = {
                        'id': composite_id,  # Use composite ID
                        'player_id': player_id,
                        'player_name': scorer['player']['name'],
                        'team_id': scorer['team']['id'],
                        'played_matches': scorer['playedMatches'],
                        'goals': scorer['goals'],
                        'assists': scorer.get('assists', 0),  # Default to 0 if not available
                        'penalties': scorer.get('penalties', 0),  # Default to 0 if not available
                        'season_year': int(season_year)
                    }
                    connection.execute(epl_topscorers_3y.insert().values(record))
                    print(f"Inserted record for {record['player_name']} in season {season_year}")

            transaction.commit()  # Commit the transaction after all inserts
        except IntegrityError as e:
            print(f"Integrity error: {e}. Rolling back transaction.")
            transaction.rollback()
        except SQLAlchemyError as e:
            print(f"SQLAlchemy error: {e}. Rolling back transaction.")
            transaction.rollback()

# Load the data from the JSON file
with open('/app/data/data/topscorers_3y.json', 'r') as file:

    data = json.load(file)

# Insert data into the table
insert_topscorers_data(data)
