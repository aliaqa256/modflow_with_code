import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
import flopy

# ==========================================
# Section 1: Pre-processing Spatial Data
# ==========================================
print("--- 1. Loading GIS Data ---")    
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gis_dir = os.path.join(baseDir, 'gis_data')

# 1. Read grid geometry from topography raster
with rasterio.open(os.path.join(gis_dir, 'topography.tif')) as src:
    top = src.read(1)
    xmin, ymax = src.bounds.left, src.bounds.top
    delr, delc = src.res[0], src.res[1]
    nrow, ncol = src.height, src.width

# 2. Read other rasters
with rasterio.open(os.path.join(gis_dir, 'bedrock.tif')) as src:
    botm = src.read(1)
with rasterio.open(os.path.join(gis_dir, 'k_zones.tif')) as src:
    k_array = src.read(1)
with rasterio.open(os.path.join(gis_dir, 'recharge.tif')) as src:
    rech_array = src.read(1)

# 3. Read IDOMAIN array (active cells)
idomain = np.load('idomain_array.npy')

print(f"Grid Params: {nrow}x{ncol}, Cell={delr}m, Origin=({xmin}, {ymax})")

print("--- 2. Mapping Vector Data to Grid ---")
# Helper function to convert X, Y coordinates to model row and column
def coord_to_cell(x, y):
    col = int((x - xmin) / delr)
    row = int((ymax - y) / delc)
    return row, col

# 4. Process wells
df_wells = pd.read_excel(os.path.join(gis_dir, 'wells.xlsx'))
wel_spd = []
for _, row in df_wells.iterrows():
    r, c = coord_to_cell(row['X_Coord'], row['Y_Coord'])
    # Only add wells located in active area (idomain==1)
    if idomain[r, c] == 1:
        wel_spd.append([(0, r, c), row['Pumping_Rate']])
        print(f" -> Well {row['Well_ID']} mapped to Row:{r}, Col:{c}")

# 5. Process flow boundaries (CHD) from shapefile
# This section is slightly complex because lines must be rasterized onto grid cells
gdf_bound = gpd.read_file(os.path.join(gis_dir, 'flow_boundaries.shp'))
from rasterio.features import rasterize

chd_spd = []
for idx, row in gdf_bound.iterrows():
    # Rasterize each line into pixels separately
    geom = [row.geometry]
    line_mask = rasterize(geom, out_shape=(nrow, ncol), transform=src.transform, fill=0, default_value=1)
    
    # Find row and column of pixels crossed by the line
    rows, cols = np.where(line_mask == 1)
    for r, c in zip(rows, cols):
        if idomain[r, c] == 1:
            chd_spd.append([(0, r, c), row['Head_m']])
    print(f" -> Boundary '{row['Name']}' mapped to {len(rows)} cells.")

print("\nPre-processing complete. Ready to build the model.")


# ==========================================
# Section 2: Building and Running Model in MODFLOW
# ==========================================
print("\n--- 3. Building MODFLOW 6 Model ---")

# Set paths (MODFLOW executable path is the previous bin folder)
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exe_name = os.path.join(baseDir, 'bin', 'mf6')  # Add baseDir
sim_name = 'gis_based_model'
workspace = os.path.join(baseDir, 'gis_model_output')

# Build simulation and time package
sim = flopy.mf6.MFSimulation(sim_name=sim_name, exe_name=exe_name, sim_ws=workspace)
tdis = flopy.mf6.ModflowTdis(sim, time_units='DAYS', nper=1, perioddata=[(1.0, 1, 1.0)])
gwf = flopy.mf6.ModflowGwf(sim, modelname=sim_name, save_flows=True)

# 1. Spatial package (DIS): Direct injection of rasters and IDOMAIN
dis = flopy.mf6.ModflowGwfdis(
    gwf, nlay=1, nrow=nrow, ncol=ncol, delr=delr, delc=delc, 
    top=top, botm=botm, idomain=idomain
)

# 2. Initial conditions (water head set to ~90 between 98 and 85)
ic = flopy.mf6.ModflowGwfic(gwf, strt=90.0)

# 3. Flow properties package (NPF): Inject dual hydraulic conductivity raster
npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=0, k=k_array, save_flows=True)

# 4. Recharge package: Inject rainfall raster
rch = flopy.mf6.ModflowGwfrcha(gwf, recharge=rech_array)

# 5. Boundary packages: Inject lists extracted from shapefile
chd = flopy.mf6.ModflowGwfchd(gwf, stress_period_data=chd_spd)
wel = flopy.mf6.ModflowGwfwel(gwf, stress_period_data=wel_spd)

# 6. Output control and solver
oc = flopy.mf6.ModflowGwfoc(
    gwf, saverecord=[('HEAD', 'ALL'), ('BUDGET', 'ALL')],
    head_filerecord=f'{sim_name}.hds', budget_filerecord=f'{sim_name}.cbc'
)
ims = flopy.mf6.ModflowIms(sim, complexity='SIMPLE')

print("--- 4. Running the Model ---")
sim.write_simulation()
success, buff = sim.run_simulation()

if success:
    print("\nBINGO! The Real-World GIS model ran successfully!")
else:
    print("\nModel run failed. Please check the output for errors.")