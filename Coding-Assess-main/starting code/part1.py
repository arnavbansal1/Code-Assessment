vaimport requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
    df = pd.DataFrame(json_data["observations"])
    df["date"] = pd.to_datetime(df["date])
    df.set_index("date", inplace = True)
    # Convert the 'value' column to numeric and rename it based on series_id
    df["value"] = pd.to_numeric(df["value", errors="coerce]) # we do not want this to throw an exception but to set an invalid parsing as NaN
    df.rename(columns={"value" : series_id}, in_place = True)                            
    return df[[series_id]]  # Final DataFrame with date index and yield column
                                
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
df = df.ffill().bfill() # missing values are filled, first by propagating the last valid observation forward then by propagating the next valid observation backward.
# Print the number of rows in the final DataFrame
print(df.shape[0])

# Spread calculation using linear interpolation of Treasury yields
def calculate_spreads(bond_data, treasury_data):
    spreads = []
    tenors = [float(k[3:]) / 12 if "MO" in k else float(k[3:]) for k in tenor_series_ids] # we are converting the text-based ids to numeric represenations for the tenors based on whether they are months or years
    for _, row in bond_data.iterrows():
        wal = row["WAL"]
        sector = row["Sector"]
        yield_rate = row["Yield"]
        index = sorted(tenors + [wal]).index(wal)
        if wal in tenors:
            treasury_yield = treasury_data[f"DGS{int(wal)}"].mean()
        else:
            lower, upper = nearest_tenors[index - 1], nearest_tenors[index + 1]
            lower_yield = treasury_data[f"DGS{int(lower)}"].mean()
            upper_yield = treasury_data[f"DGS{int(upper)}"].mean()
            treasury_yield = np.interp(wal, [lower, upper], [lower_yield, upper_yield]) #returns the estimated treasury yield for wal based on the relationship between the lower and upper tenors and the lower and upper treasury yields, or the nearest points to wal
        spread = yield_rate - treasury_yield
        spreads.append({"Sector": sector, "WAL": wal, "Spread": spread})
    return pd.DataFrame(spreads)
          
file_path = "data/Part 1. bonds_yields.xlsx"
spread_data = calculate_spreads(pd.read_excel(file_path, sheet_name=0), data_complete)

#Visualizations. First is a boxplot of the bond spread distribution by sector. Second is a scatter plot of bond spreads vs. WAL.
def plot_spread_distribution(spread_data):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="Sector", y="Spread", data=spread_data)
    plt.xticks(rotation=45) #rotating x-axis tick labels since they're long
    plt.title("Bond Spread Distribution by Sector")
    plt.show()
         
def plot_spread_vs_wal(spread_data):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="WAL", y="Spread", hue="Sector", data=spread_data, alpha=0.7) #slightly transparent
    plt.title("Bond Spreads vs. Weighted Average Life (WAL)")
    plt.xlabel("Weighted Average Life (WAL)")
    plt.ylabel("Spread")
    plt.legend(title="Sector")
    plt.show()

plot_spread_distribution(spread_data)
plot_spread_vs_wal(spread_data)

