import pandas as pd
from google.cloud import bigquery
import requests  # We now need this to query the API
import re # For cleaning column names
import numpy as np # For np.nan

# --- Configuration ---
# !!! - REPLACE THESE VALUES - !!!
PROJECT_ID = 'itd-aia-datalake'
DATASET_ID = 'gcs_ops'
TABLE_NAME = 'tb_quac_tech_demo'
billing_project = 'itd-aia-de'

# FIX: Pass the project ID using the 'project' keyword
client = bigquery.Client(project=billing_project)   

# --- API Endpoint Configuration ---
# These point to your local json-server
ROSTER_URL = 'http://localhost:3001/roster'
WORK_URL = 'http://localhost:3001/work'

# Define the full BigQuery table ID
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"

# --- Helper Functions ---

def safe_to_float(value):
    """Safely converts a value to float, handling strings, or returns np.nan."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Attempt to convert the string to float
        return float(value)
    except (ValueError, TypeError):
        # If conversion fails, return np.nan
        return np.nan

def clean_col_name(col_name):
    """Cleans column names for BQ (no spaces, special chars) and removes BOM."""
    if not isinstance(col_name, str):
        return col_name
    cleaned = col_name.strip().replace('\ufeff', '')
    cleaned = re.sub(r'\s+', '_', cleaned) # Replace spaces with underscores
    cleaned = re.sub(r'[^A-Za-z0-9_]', '', cleaned) # Remove other special chars
    return cleaned

def main():
    print("Starting API-to-BigQuery workflow...")

    try:
        # --- 1. Extract (from API) ---
        print(f"Querying API for Roster data at {ROSTER_URL}...")
        response_roster = requests.get(ROSTER_URL)
        response_roster.raise_for_status()  # Will raise an error for bad responses (404, 500)
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

        # --- 2. Transform (Clean Headers & Join DataFrames) ---
        
        # <<< FIX 1: Clean column names to remove BOM ('\ufeff') and whitespace >>>
        print("Cleaning column names...")
        # FIX: Use the robust clean_col_name function to match the schema
        # (e.g., "Direct Manager" -> "Direct_Manager")
        df_roster.columns = [clean_col_name(c) for c in df_roster.columns]
        df_work.columns = [clean_col_name(c) for c in df_work.columns]
        
        # <<< FIX 2: Drop any columns that have an empty string as a name >>>
        print(f"Original Roster columns: {list(df_roster.columns)}")
        print(f"Original Work columns: {list(df_work.columns)}")

        df_roster = df_roster.loc[:, ~df_roster.columns.isin([''])]
        df_work = df_work.loc[:, ~df_work.columns.isin([''])]

        print(f"Cleaned Roster columns: {list(df_roster.columns)}")
        print(f"Cleaned Work columns: {list(df_work.columns)}")
        
        # <<< NEW/FIXED SECTION: Convert Data Types BEFORE Upload >>>
        print("Converting data types...")
        
        # Convert date columns
        df_work['week_end_date'] = pd.to_datetime(df_work['week_end_date'], errors='coerce')
        df_work['week_start_date'] = pd.to_datetime(df_work['week_start_date'], errors='coerce')
        
        # Safely convert numeric columns using the robust function
        print("Safely converting float columns...")
        df_work['Fundraising'] = df_work['Fundraising'].apply(safe_to_float)
        df_work['Philanthropy'] = df_work['Philanthropy'].apply(safe_to_float)
        df_work['Brotherhood'] = df_work['Bortherhood'].apply(safe_to_float)
        
        print("Safely converting 'Capacity' column to int...")
        # pd.to_numeric is fine for this, as it's not the one that failed
        df_work['Capacity'] = pd.to_numeric(df_work['Capacity'], errors='coerce').astype('Int64')
        # <<< END OF NEW SECTION >>>

        print("Joining data on 'userid'...")
        df_joined = pd.merge(df_roster, df_work, on='userid', how='inner')

        if df_joined.empty:
            print("Warning: The joined DataFrame is empty. Check your 'userid' columns.")
            return

        print(f"Joined data shape: {df_joined.shape}")

        # --- 3. Load (Upload to BigQuery) ---
        print(f"Uploading joined data to BigQuery table: {TABLE_ID}")
        
        # This command uploads the DataFrame.
        # if_exists='replace' will overwrite the table if it already exists.
        job_config = bigquery.LoadJobConfig(
            schema = [
            # Columns from Roster data
            bigquery.SchemaField("Name", "STRING"),
            bigquery.SchemaField("userid", "STRING"),
            bigquery.SchemaField("Direct_Manager", "STRING"), # Cleaned name
            bigquery.SchemaField("Pledge_Class", "STRING"),   # Cleaned name
            bigquery.SchemaField("Major", "STRING"),
            bigquery.SchemaField("Concentration", "STRING"),
            bigquery.SchemaField("Academic_Year", "STRING"),  # Cleaned name
            bigquery.SchemaField("Expected_Grad", "STRING"),  # Cleaned name
            
            # Columns from Work data
            bigquery.SchemaField("Fundraising", "FLOAT64"),
            bigquery.SchemaField("Philanthropy", "FLOAT64"),
            bigquery.SchemaField("Professionalism", "FLOAT64"),
            bigquery.SchemaField("Capacity", "INT64"),
            bigquery.SchemaField("week_end_date", "DATE"),
            bigquery.SchemaField("week_start_date", "DATE")
        ],write_disposition="WRITE_TRUNCATE",
        ) 



        job = client.load_table_from_dataframe(df_joined,TABLE_ID,job_config)

        print("\n✅ Success! Data fetched from API, joined, and uploaded to BigQuery.")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to the API at {ROSTER_URL} or {WORK_URL}.")
        print("Please make sure your local API server is running in a separate terminal with 'npm start'.")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error: The API returned a non-200 status code. {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred:")
        print(e)
        print("\nPlease check your GCP project/dataset IDs and authentication.")

if __name__ == "__main__":
    main()


