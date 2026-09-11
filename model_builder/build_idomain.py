import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import matplotlib.pyplot as plt

# 1. Setting up paths
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gis_dir = os.path.join(baseDir, 'gis_data')   

print("--- 1. Reading Grid Metadata ---")
# Read metadata from topography raster to ensure exact pixel alignment with other rasters
with rasterio.open(os.path.join(gis_dir, 'topography.tif')) as src:
    transform = src.transform
    shape = src.shape  # Dimensions (40, 40)

print("--- 2. Reading Aquifer Polygon ---")
gdf_poly = gpd.read_file(os.path.join(gis_dir, 'aquifer_boundary.shp'))

print("--- 3. Rasterizing Polygon (Vector to Grid) ---")
# Extract polygon geometry (only the drawn shape)
geom = [shapes for shapes in gdf_poly.geometry]

# The rasterize tool converts irregular lines into 0 and 1 pixels
idomain = rasterize(
    geom,
    out_shape=shape,
    transform=transform,
    fill=0,           # Default value for cells outside polygon (inactive)
    default_value=1,  # Value for cells inside polygon (active)
    dtype=np.int8
)

print(f"Total Grid Size: {idomain.size} cells")
print(f"Active Cells: {np.sum(idomain)} cells")
print(f"Inactive Cells: {idomain.size - np.sum(idomain)} cells")

# 4. Save outputs (for both MODFLOW and visual quality control)
np.save('idomain_array.npy', idomain) 

plt.figure(figsize=(6, 6))
# Plot image: zero cells appear black and one cells appear white
plt.imshow(idomain, cmap='gray')
plt.title('MODFLOW IDOMAIN \n(White=Active, Black=Inactive)')
plt.savefig('idomain_preview.png')

print("-> Saved 'idomain_preview.png' for visual check.")
print("-> Saved 'idomain_array.npy' for MODFLOW.")