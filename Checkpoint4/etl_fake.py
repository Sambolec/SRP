import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Float, Boolean

# --- Database setup ---
engine = create_engine('mysql+pymysql://root:root@localhost:3306/lol_experiment')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# ---------------------
# SCHEMA DEFINITIONS
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
    team_id = Column(Integer, primary_key=True)
    side = Column(String(10))  # 'Blue' or 'Red'
    has_won = Column(Boolean)

class DimObjective(Base):
    __tablename__ = 'dim_objective'
    objective_tk = Column(Integer, primary_key=True, autoincrement=True)
    objective_name = Column(String(50), unique=True)
    category = Column(String(20))
    type = Column(String(20))
    version = Column(Integer, default=1)
    valid_from = Column(DateTime, default=datetime.now)
    valid_to = Column(DateTime, nullable=True)

class DimStructure(Base):
    __tablename__ = 'dim_structure'
    structure_tk = Column(Integer, primary_key=True, autoincrement=True)
    structure_name = Column(String(50), unique=True)
    lane = Column(String(10))
    structure_type = Column(String(20))
    version = Column(Integer, default=1)
    valid_from = Column(DateTime, default=datetime.now)
    valid_to = Column(DateTime, nullable=True)

class FactGameEvent(Base):
    __tablename__ = 'fact_game_event'
    fact_tk = Column(BigInteger, primary_key=True, autoincrement=True)
    game_id = Column(BigInteger, ForeignKey('dim_game.game_id'))
    frame = Column(Integer, ForeignKey('dim_time.frame'))
    team_id = Column(Integer, ForeignKey('dim_team.team_id'))
    objective_tk = Column(Integer, ForeignKey('dim_objective.objective_tk'), nullable=True)
    structure_tk = Column(Integer, ForeignKey('dim_structure.structure_tk'), nullable=True)
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

Base.metadata.create_all(engine)

# --- Load CSV ---
df = pd.read_csv('lol_ranked_games.csv')

# --- Helper functions ---
def get_game_phase(frame):
    if frame < 900: return 'Early'
    elif frame < 1800: return 'Mid'
    return 'Late'

def get_or_create_structure(name, lane, s_type):
    obj = session.query(DimStructure).filter_by(structure_name=name).first()
    if not obj:
        obj = DimStructure(structure_name=name, lane=lane, structure_type=s_type)
        session.add(obj)
        session.commit()
    return obj.structure_tk

def get_or_create_objective(name, category, o_type):
    obj = session.query(DimObjective).filter_by(objective_name=name).first()
    if not obj:
        obj = DimObjective(objective_name=name, category=category, type=o_type)
        session.add(obj)
        session.commit()
    return obj.objective_tk

# --- ETL Main Loop ---
for idx, row in df.iterrows():
    # --- DimGame ---
    if not session.query(DimGame).filter_by(game_id=row['gameId']).first():
        session.add(DimGame(
            game_id=row['gameId'],
            game_duration=row['gameDuration'],
            game_date=datetime.now(),
            game_type='Ranked'
        ))

    # --- DimTime ---
    if not session.query(DimTime).filter_by(frame=row['frame']).first():
        session.add(DimTime(
            frame=row['frame'],
            minute=row['frame'] // 60,
            second=row['frame'] % 60,
            game_phase=get_game_phase(row['frame'])
        ))

    # --- DimTeam ---
    team_id = idx + 1
    session.add(DimTeam(
        team_id=team_id,
        side='Blue' if team_id % 2 == 0 else 'Red',
        has_won=row['hasWon']
    ))

    # --- Objectives (Example: killedFireDrake) ---
    objective_tk = None
    if row['killedFireDrake'] > 0:
        objective_tk = get_or_create_objective('FireDrake', 'Dragon', 'Fire')

    # --- Structures (Example: destroyedTopInhibitor) ---
    structure_tk = None
    if row['destroyedTopInhibitor'] > 0:
        structure_tk = get_or_create_structure('TopInhibitor', 'Top', 'Inhibitor')

    # --- FactGameEvent ---
    session.add(FactGameEvent(
        game_id=row['gameId'],
        frame=row['frame'],
        team_id=team_id,
        objective_tk=objective_tk,
        structure_tk=structure_tk,
        gold_diff=row['goldDiff'],
        exp_diff=row['expDiff'],
        champ_level_diff=row['champLevelDiff'],
        is_first_tower=row['isFirstTower'],
        is_first_blood=row['isFirstBlood'],
        kills=row['kills'],
        deaths=row['deaths'],
        assists=row['assists'],
        wards_placed=row['wardsPlaced'],
        wards_destroyed=row['wardsDestroyed'],
        wards_lost=row['wardsLost'],
        event_time=row['frame']
    ))

    if idx % 100 == 0:
        session.commit()
        print(f"[INFO] Committed batch at row {idx}")

# Final commit
session.commit()
print(" ETL complete: all rows inserted.")
