from pyspark.sql import SparkSession

# Start Spark session and include MySQL JDBC driver
spark = SparkSession.builder \
    .appName("LoL ETL") \
    .config("spark.jars", "C:/path/to/mysql-connector-java.jar") \
    .getOrCreate()

try:
    # 1. Load your CSV file
    csv_path = r"C:\Users\domin\Desktop\SIRP-Checkpoint 2\lol_ranked_games.csv"
    print(f"Loading CSV from: {csv_path}")
    df = spark.read.option("header", True).csv(csv_path)
    print("CSV loaded. Columns:", df.columns)
    print("Sample data:")
    df.show(5)

    # 2. Extract unique games for Game table
    print("\nExtracting Game table...")
    games_df = df.select("gameId", "gameDuration").dropDuplicates()
    games_df.show(5)

    # 3. Extract data for GameState table
    print("\nExtracting GameState table...")
    game_state_columns = [
        "gameId", "frame", "goldDiff", "expDiff", "champLevelDiff",
        "isFirstTower", "isFirstBlood", "kills", "deaths",
        "assists", "wardsPlaced", "wardsDestroyed", "wardsLost"
    ]
    game_state_df = df.select(game_state_columns)
    game_state_df.show(5)

    # 4. Extract data for ObjectiveStatus table
    print("\nExtracting ObjectiveStatus table...")
    objective_columns = [
        "gameId", "frame", "killedFireDrake", "killedWaterDrake",
        "killedAirDrake", "killedEarthDrake", "killedElderDrake",
        "lostFireDrake", "lostWaterDrake", "lostAirDrake",
        "lostEarthDrake", "lostElderDrake", "killedBaronNashor",
        "lostBaronNashor", "killedRiftHerald", "lostRiftHerald"
    ]
    objective_df = df.select(objective_columns)
    objective_df.show(5)

    # 5. Extract data for StructureStatus table
    print("\nExtracting StructureStatus table...")
    structure_columns = ["gameId", "frame"]
    # Append all columns that contain 'destroyed' or 'lost'
    structure_columns += [col for col in df.columns if 'destroyed' in col.lower() or 'lost' in col.lower()]
    # Remove non-structure columns
    non_structure_cols = [
        'lostFireDrake', 'lostWaterDrake', 'lostAirDrake', 'lostEarthDrake',
        'lostElderDrake', 'lostBaronNashor', 'lostRiftHerald', 'wardsLost'
    ]
    structure_columns = [col for col in structure_columns if col not in non_structure_cols]
    structure_df = df.select(structure_columns)
    structure_df.show(5)

    # 6. Extract data for TeamResult table
    print("\nExtracting TeamResult table...")
    team_result_df = df.select("gameId", "hasWon").dropDuplicates()
    team_result_df.show(5)

    # 7. Write all tables to MySQL using JDBC
    jdbc_url = "jdbc:mysql://localhost:3306/lol-ranked"
    properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    print("\nWriting Game table...")
    games_df.write.jdbc(url=jdbc_url, table="game", mode="append", properties=properties)
    print("Game table written.")

    print("Writing GameState table...")
    game_state_df.write.jdbc(url=jdbc_url, table="gamestate", mode="append", properties=properties)
    print("GameState table written.")

    print("Writing ObjectiveStatus table...")
    objective_df.write.jdbc(url=jdbc_url, table="objectivestatus", mode="append", properties=properties)
    print("ObjectiveStatus table written.")

    print("Writing StructureStatus table...")
    structure_df.write.jdbc(url=jdbc_url, table="structurestatus", mode="append", properties=properties)
    print("StructureStatus table written.")

    print("Writing TeamResult table...")
    team_result_df.write.jdbc(url=jdbc_url, table="teamresult", mode="append", properties=properties)
    print("TeamResult table written.")

    print("\n=== ETL PROCESS COMPLETED SUCCESSFULLY! ===")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    spark.stop()
    print("Spark session stopped.")
