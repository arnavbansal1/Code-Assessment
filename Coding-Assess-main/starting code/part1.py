import requests
import pandas as pd


def fetch_fred_yield(series_id, start_date="2023-01-01", end_date="2023-12-31", api_key="c33bc0ccdfcb244124f432a3edfc4f7a"):
    # Define the API URL and parameters here
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    params = {
      "series_id": series_id,
      "api_key": FRED_API_KEY,
      "file_type": "json",
      "observation_start": start_date,
      "observation_end": end_date 
    }
    # Make an API request and handle errors
    response = requests.get(BASE_URL, params)
    if response.status_code != 200:
      print(f"Error fetching {series_id}: {response.status_code}")
      return pd.DataFrame()
    # Convert response JSON into a DataFrame, setting 'date' as index
    json_data = response.json()
    print(json_data)
    df = pd.DataFrame(json_data[""])
    df["date"] = pd.to_datetime(df["date])
    df.set_index("date", inplace = True)
    # Convert the 'value' column to numeric and rename it based on series_id
    df["value"] = pd.to_numeric(df["value", errors="coerce]) #we do not want this to throw an exception but to set an invalid parsing as NaN
    df.rename(columns={"value" : series_id}, in_place = True)                            
    return df[[series_id]]  # Final DataFrame with date index and yield column

def 
# List of Treasury yield series IDs on FRED
tenor_series_ids = [
    "DGS1MO", "DGS3MO", "DGS6MO", "DGS1",  # Short-term yields
    "DGS2", "DGS3", "DGS5",               # Medium-term yields
    "DGS7", "DGS10", "DGS20", "DGS30"     # Long-term yields
]

# Initialize API key
FRED_API_KEY = "c33bc0ccdfcb244124f432a3edfc4f7a"

# Fetch data for each tenor, store in a dictionary of DataFrames
data_complete = [fetch_fred_yield(series) for series in tenor_series_ids]
# Combine all DataFrames into a single DataFrame, joining on the date index
df = pd.concat(data_complete, axis=1).sort_index()
df = df.ffill().bfill() #missing values are filled, first by propagating the last valid observation forward then by propagating the next valid observation backward.
# Print the number of rows in the final DataFrame
print(df.shape[0])
