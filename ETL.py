# This script is a modified version of our BigQuery pipeline.
# It performs the same E-T-L (Extract, Transform, Load) process,
# but instead of loading to a cloud data warehouse, it saves the
# clean, joined data to a local database file called 'my_local_database.db'.

import pandas as pd
import requests  # To query the API
import re        # For cleaning column names
import numpy as np # For np.nan
from sqlalchemy import create_engine # To create a local SQL database

# --- Configuration ---
DB_FILE = 'my_local_database.db'
TABLE_NAME = 'quac_tech_demo'
DB_CONNECTION_STRING = f'sqlite:///{DB_FILE}'

# --- API Endpoint Configuration ---
# These point to your local json-server
ROSTER_URL = 'http://localhost:3001/roster'
WORK_URL = 'http://localhost:3001/work'

# --- Helper Functions ---

def safe_to_float(value):
    """Safely converts a value to float, handling strings, or returns np.nan."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Convert the string to float
        return float(str(value).strip())
    except (ValueError, TypeError):
        # If conversion fails, return np.nan
        return np.nan

def clean_col_name(col_name):
    """Cleans column names for a database (no spaces, special chars) and removes BOM."""
    if not isinstance(col_name, str):
        return col_name
    cleaned = col_name.strip().replace('\ufeff', '')
    cleaned = re.sub(r'\s+', '_', cleaned) # Replace spaces with underscores
    cleaned = re.sub(r'[^A-Za-z0-9_]', '', cleaned) # Remove other special chars
    return cleaned

def main():
    print("Starting ETL workflow (API to local SQLite DB)...")

    try:
        # --- 1. Extract (from API) ---
        print(f"Querying API for Roster data at {ROSTER_URL}...")
        response_roster = requests.get(ROSTER_URL)
        response_roster.raise_for_status()
        df_roster = pd.DataFrame(response_roster.json())
        
        print(f"Querying API for Work data at {WORK_URL}...")
        response_work = requests.get(WORK_URL)
        response_work.raise_for_status()
        df_work = pd.DataFrame(response_work.json())

        print(f"Roster data shape from API: {df_roster.shape}")
        print(f"Work data shape from API: {df_work.shape}")

        if df_roster.empty or df_work.empty:
            print("Warning: One or both dataframes from API are empty. Check your endpoints.")
            return

        # --- 2. Transform (Clean Headers, Fix Types, Join DataFrames) ---
        
        print("Cleaning column names...")
        df_roster.columns = [clean_col_name(c) for c in df_roster.columns]
        df_work.columns = [clean_col_name(c) for c in df_work.columns]
        
        # Drop any columns that have an empty string as a name
        df_roster = df_roster.loc[:, ~df_roster.columns.isin([''])]
        df_work = df_work.loc[:, ~df_work.columns.isin([''])]

        print(f"Cleaned Roster columns: {list(df_roster.columns)}")
        print(f"Cleaned Work columns: {list(df_work.columns)}")
        
        print("Converting data types...")
        
        # Convert date columns
        df_work['week_end_date'] = pd.to_datetime(df_work['week_end_date'], errors='coerce')
        df_work['week_start_date'] = pd.to_datetime(df_work['week_start_date'], errors='coerce')
        
        # Safely convert numeric columns
        print("Safely converting float columns...")
        df_work['Fundraising'] = df_work['Fundraising'].apply(safe_to_float)
        df_work['Philanthropy'] = df_work['Philanthropy'].apply(safe_to_float)
        df_work['nonbillablework'] = df_work['nonbillablework'].apply(safe_to_float)
        
        print("Safely converting 'Capacity' column to int...")
        df_work['Capacity'] = pd.to_numeric(df_work['Capacity'], errors='coerce').astype('Int64')

        print("Joining data on 'userid'...")
        df_joined = pd.merge(df_roster, df_work, on='userid', how='inner')

        if df_joined.empty:
            print("Warning: The joined DataFrame is empty. Check your 'userid' columns.")
            return

        print(f"Joined data shape: {df_joined.shape}")

        # --- 3. Load (to Local SQLite Database) ---
        print(f"Connecting to local database file: {DB_FILE}...")
        # This creates the database engine and the file if it doesn't exist
        engine = create_engine(DB_CONNECTION_STRING)

        print(f"Uploading joined data to table: {TABLE_NAME}...")
        # This command uploads the DataFrame to the SQLite database.
        # if_exists='replace' will overwrite the table if it already exists.
        df_joined.to_sql(
            TABLE_NAME,
            con=engine,
            if_exists='replace',
            index=False # Don't save the pandas index as a column
        )

        print("\n✅ Success! Data fetched from API, joined, and loaded into your local database.")
        print(f"You can now connect Tableau to the file: {DB_FILE}")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to the API at {ROSTER_URL} or {WORK_URL}.")
        print("Please make sure your local API server is running in a separate terminal with 'npm start'.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred:")
        print(e)

if __name__ == "__main__":
    main()
