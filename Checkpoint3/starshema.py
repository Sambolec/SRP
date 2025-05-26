from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, ForeignKey, Float, Boolean, text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create DB
temp_engine = create_engine('mysql+pymysql://root:root@localhost:3306/', echo=True)
with temp_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS lol_experiment"))
    conn.commit()

# Connect to new DB
engine = create_engine('mysql+pymysql://root:root@localhost:3306/lol_experiment', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# ---------------------
# DIMENSION TABLES
# ---------------------

class DimGame(Base):
    __tablename__ = 'dim_game'
    game_id = Column(BigInteger, primary_key=True)
    game_duration = Column(Integer)
    game_date = Column(DateTime, default=datetime.now)
    game_type = Column(String(50), default='Ranked')


class DimTime(Base):
    __tablename__ = 'dim_time'
    time_id = Column(Integer, primary_key=True, autoincrement=True)
    frame = Column(Integer, unique=True, nullable=False)
    minute = Column(Integer)
    second = Column(Integer)
    game_phase = Column(String(20))  # 'Early', 'Mid', 'Late'


class DimTeam(Base):
    __tablename__ = 'dim_team'
    team_id = Column(Integer, primary_key=True)  # now primary key
    side = Column(String(10))  # 'Blue' or 'Red'
    has_won = Column(Boolean)


class DimObjective(Base):
    __tablename__ = 'dim_objective'
    objective_tk = Column(Integer, primary_key=True, autoincrement=True)
    objective_name = Column(String(50), unique=True)
    category = Column(String(20))  # 'Dragon', 'Baron', etc.
    type = Column(String(20))  # 'Fire', 'Water', etc.
    version = Column(Integer, default=1)
    valid_from = Column(DateTime, default=datetime.now)
    valid_to = Column(DateTime, nullable=True)


class DimStructure(Base):
    __tablename__ = 'dim_structure'
    structure_tk = Column(Integer, primary_key=True, autoincrement=True)
    structure_name = Column(String(50), unique=True)
    lane = Column(String(10))  # 'Top', 'Mid', 'Bot'
    structure_type = Column(String(20))  # 'Inhibitor', etc.
    version = Column(Integer, default=1)
    valid_from = Column(DateTime, default=datetime.now)
    valid_to = Column(DateTime, nullable=True)

# ---------------------
# FACT TABLE (1 central table)
# ---------------------

class FactGameEvent(Base):
    __tablename__ = 'fact_game_event'
    fact_tk = Column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    game_id = Column(BigInteger, ForeignKey('dim_game.game_id'))
    frame = Column(Integer, ForeignKey('dim_time.frame'))
    team_id = Column(Integer, ForeignKey('dim_team.team_id'))
    objective_tk = Column(Integer, ForeignKey('dim_objective.objective_tk'), nullable=True)
    structure_tk = Column(Integer, ForeignKey('dim_structure.structure_tk'), nullable=True)

    # Metrics
    gold_diff = Column(Integer)
    exp_diff = Column(Integer)
    champ_level_diff = Column(Float)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    wards_placed = Column(Integer)
    wards_destroyed = Column(Integer)
    wards_lost = Column(Integer)
    is_first_tower = Column(Boolean)
    is_first_blood = Column(Boolean)
    event_time = Column(Integer, nullable=True)

# ---------------------
# CREATE ALL TABLES
# ---------------------
Base.metadata.create_all(engine)
print(" Dimensional model successfully created.")
