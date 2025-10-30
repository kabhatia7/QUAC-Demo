import requests
import json

# The URL for your local API endpoint (must match the port in your server)
API_URL = "http://localhost:3001/roster" # Pointing to your roster endpoint

def fetch_data():
    """
    Fetches data from the local API.
    """
    try:
        # Make a GET request to the API
        response = requests.get(API_URL)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            print(f"Successfully fetched {len(data)} items from {API_URL}:")
            # Pretty-print the JSON data
            print(json.dumps(data, indent=2))

        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the API at {API_URL}.")
        print("Please make sure your 'npm start' server is running.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_data()


