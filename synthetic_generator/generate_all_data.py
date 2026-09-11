import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Polygon, LineString, Point

# 1. Initial settings
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(baseDir, 'gis_data')
os.makedirs(output_dir, exist_ok=True)
crs = 'EPSG:32639'

print("--- 1. Generating Rasters ---")
pixel_size, rows, cols = 50, 40, 40
xmin, ymax = 300000, 4000000

# Topography (gradient from west to east) and bedrock
surface_elev = np.linspace(100, 80, cols)
topo_array = np.tile(surface_elev, (rows, 1))
bedrock_array = np.full((rows, cols), 20.0)

transform = from_origin(xmin, ymax, pixel_size, pixel_size)

def save_raster(filename, array):
    filepath = os.path.join(output_dir, filename)
    with rasterio.open(filepath, 'w', driver='GTiff', height=rows, width=cols,
                       count=1, dtype=str(array.dtype), crs=crs, transform=transform) as dst:
        dst.write(array, 1)
        
save_raster('topography.tif', topo_array)
save_raster('bedrock.tif', bedrock_array)

print("--- 2. Generating Aquifer Polygon ---")
boundary_coords = [
    (300150, 3999900), (301600, 3999850), 
    (301850, 3998800), (301200, 3998150), (300300, 3998300)
]
aquifer_poly = Polygon(boundary_coords)
gdf_poly = gpd.GeoDataFrame({'ID': [1], 'Name': ['Main_Aquifer']}, geometry=[aquifer_poly], crs=crs)
gdf_poly.to_file(os.path.join(output_dir, 'aquifer_boundary.shp'))

print("--- 3. Generating Wells (Inside Aquifer) ---")
wells_data = {
    'Well_ID': ['W-1', 'W-2', 'W-3'],
    'X_Coord': [300800, 301200, 301000],  # Adjusted coordinates to lie in the center of the plain
    'Y_Coord': [3999200, 3999500, 3998700], 
    'Pumping_Rate': [-1500, -2500, -1000]
}
pd.DataFrame(wells_data).to_excel(os.path.join(output_dir, 'wells.xlsx'), index=False)

# Create wells shapefile for GIS visualization
geometry = [Point(xy) for xy in zip(wells_data['X_Coord'], wells_data['Y_Coord'])]
gdf_wells = gpd.GeoDataFrame(wells_data, geometry=geometry, crs=crs)
gdf_wells.to_file(os.path.join(output_dir, 'wells.shp'))

print("--- 4. Generating Boundaries (Exact on Polygon Edges) ---")

# Recharge boundary (inflow from mountains in the west)
# Exactly on the western edge of the polygon (between southwest and northwest points)
inflow_line = LineString([(300300, 3998300), (300150, 3999900)])

# Discharge boundary (outflow from plain in the southeast)
# Exactly on the southeastern edge of the polygon (between east and south points)
outflow_line = LineString([(301850, 3998800), (301200, 3998150)])

boundaries_data = {
    'Name': ['Recharge_Zone', 'Discharge_Zone'],
    'Head_m': [98.0, 85.0]
}
gdf_bound = gpd.GeoDataFrame(boundaries_data, geometry=[inflow_line, outflow_line], crs=crs)
gdf_bound.to_file(os.path.join(output_dir, 'flow_boundaries.shp'))

print("All GIS data successfully created and logically aligned!")