import pandas as pd
from sqlalchemy import create_engine, text

# Učitavanje CSV datoteke
df = pd.read_csv("C:/Users/domin/Downloads/lol_ranked_games.csv/lol_ranked_games.csv")

# Povezivanje s bazom podataka
# Prilagodite parametre prema vašoj konfiguraciji
engine = create_engine('mysql+mysqlconnector://root:root@localhost/lol-ranked')

# 1. Izdvajanje jedinstvenih igara za Game tablicu
games_df = df[['gameId', 'gameDuration']].drop_duplicates()
games_df.to_sql('game', con=engine, if_exists='append', index=False, chunksize=1000)

# 2. Izdvajanje podataka za GameState tablicu
game_state_columns = ['gameId', 'frame', 'goldDiff', 'expDiff', 'champLevelDiff', 
                      'isFirstTower', 'isFirstBlood', 'kills', 'deaths', 
                      'assists', 'wardsPlaced', 'wardsDestroyed', 'wardsLost']
game_state_df = df[game_state_columns]
game_state_df.to_sql('gamestate', con=engine, if_exists='append', index=False, chunksize=1000)

# 3. Izdvajanje podataka za ObjectiveStatus tablicu
objective_columns = ['gameId', 'frame', 'killedFireDrake', 'killedWaterDrake',
                    'killedAirDrake', 'killedEarthDrake', 'killedElderDrake',
                    'lostFireDrake', 'lostWaterDrake', 'lostAirDrake',
                    'lostEarthDrake', 'lostElderDrake', 'killedBaronNashor',
                    'lostBaronNashor', 'killedRiftHerald', 'lostRiftHerald']
objective_df = df[objective_columns]
objective_df.to_sql('objectivestatus', con=engine, if_exists='append', index=False, chunksize=1000)

# 4. Izdvajanje podataka za StructureStatus tablicu
structure_columns = ['gameId', 'frame']
structure_columns.extend([col for col in df.columns if 'destroyed' in col.lower() or 'lost' in col.lower()])
# Uklanjanje stupaca koji ne pripadaju strukturi
non_structure_cols = ['lostFireDrake', 'lostWaterDrake', 'lostAirDrake', 'lostEarthDrake', 
                      'lostElderDrake', 'lostBaronNashor', 'lostRiftHerald', 'wardsLost']
structure_columns = [col for col in structure_columns if col not in non_structure_cols]
structure_df = df[structure_columns]
structure_df.to_sql('structurestatus', con=engine, if_exists='append', index=False, chunksize=1000)

# 5. Izdvajanje podataka za TeamResult tablicu
team_result_df = df[['gameId', 'hasWon']].drop_duplicates()
team_result_df.to_sql('teamresult', con=engine, if_exists='append', index=False, chunksize=1000)

print("Podaci uspješno učitani u bazu podataka!")
