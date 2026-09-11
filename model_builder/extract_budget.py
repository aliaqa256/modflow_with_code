import os
import flopy

print("--- 1. Locating Model Output ---")
sim_name = 'gis_based_model'
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workspace = os.path.join(baseDir, 'gis_model_output')   
list_file = os.path.join(workspace, f'{sim_name}.lst')

# Check if list file exists
if not os.path.exists(list_file):
    raise FileNotFoundError(f"List file not found at: {list_file}")

print("--- 2. Extracting Water Budget ---")
# Read list file using MODFLOW 6 utility in FloPy
mflist = flopy.utils.Mf6ListBudget(list_file)

# Convert data to pandas DataFrames (IN and OUT)
df_in, df_out = mflist.get_dataframes(start_datetime=None)

# Extract last time step (since model is steady-state, last step is sufficient)
latest_in = df_in.iloc[-1]
latest_out = df_out.iloc[-1]

print("\n" + "="*40)
print(" 💧 WATER BUDGET SUMMARY (INFLOW) 💧")
print("="*40)
# Remove extra columns for cleaner display
print(latest_in.drop(['IN-OUT', 'PERCENT_DISCREPANCY']).to_string())

print("\n" + "="*40)
print(" 🚰 WATER BUDGET SUMMARY (OUTFLOW) 🚰")
print("="*40)
print(latest_out.to_string())

print("\n" + "="*40)
print(" ⚖️  BALANCE CHECK ⚖️")
print("="*40)

total_in = latest_in['TOTAL_IN']
total_out = latest_out['TOTAL_OUT']
error = latest_in['PERCENT_DISCREPANCY']

print(f"Total Water IN:   {total_in:,.2f} (m3/day)")
print(f"Total Water OUT:  {total_out:,.2f} (m3/day)")
print(f"Model Error:      {error:.6f} %")

if abs(error) < 1.0:
    print("\n✅ STATUS: EXCELLENT! The model is perfectly balanced.")
else:
    print("\n⚠️ STATUS: WARNING! The model has a high mass balance error.")