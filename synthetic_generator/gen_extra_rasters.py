import os
import numpy as np
import rasterio
from rasterio.transform import from_origin

# 1. Base settings (aligned with previous grid)
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(baseDir, 'gis_data')
crs = 'EPSG:32639'
pixel_size, rows, cols = 50, 40, 40
xmin, ymax = 300000, 4000000
transform = from_origin(xmin, ymax, pixel_size, pixel_size)

def save_raster(filename, array):
    filepath = os.path.join(output_dir, filename)
    with rasterio.open(
        filepath, 'w', driver='GTiff', height=rows, width=cols,
        count=1, dtype=str(array.dtype), crs=crs, transform=transform
    ) as dst:
        dst.write(array, 1)

print("--- 1. Generating Hydraulic Conductivity (K) Zones ---")
# Create an array with base value of 5 m/day (fine-grained - eastern half)
k_array = np.full((rows, cols), 5.0)

# Change first 20 columns (western half) to 20 m/day (coarse-grained)
k_array[:, :20] = 20.0 
save_raster('k_zones.tif', k_array)
print(" -> Saved 'k_zones.tif'")

print("--- 2. Generating Areal Recharge ---")
# Assume infiltration recharge is 0.001 m/day (equivalent to 1 mm/day)
rech_array = np.full((rows, cols), 0.001)
save_raster('recharge.tif', rech_array)
print(" -> Saved 'recharge.tif'")

print("Extra GIS rasters successfully generated!")