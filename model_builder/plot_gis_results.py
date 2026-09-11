import os
import numpy as np
import matplotlib.pyplot as plt
import flopy

print("--- 1. Loading Model and Output ---")
sim_name = 'gis_based_model'
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workspace = os.path.join(baseDir, 'gis_model_output')   
hds_file = os.path.join(workspace, f'{sim_name}.hds')

# Load groundwater head results
headobj = flopy.utils.HeadFile(hds_file)
head_data = headobj.get_data()[0]

# Load model structure to use plotting utilities
sim = flopy.mf6.MFSimulation.load(sim_name=sim_name, sim_ws=workspace, verbosity_level=0)
gwf = sim.get_model(sim_name)

print("--- 2. Generating Contour Map ---")
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect('equal')

# Map plotting tool on model grid
mapview = flopy.plot.PlotMapView(model=gwf, ax=ax)

# Plot background: inactive areas turn black
mapview.plot_ibound(color_noflow='black', alpha=0.8)

# Plot grid lines (faint)
mapview.plot_grid(linewidth=0.5, color='gray', alpha=0.2)

# Plot boundaries (blue) and wells (red)
mapview.plot_bc('CHD', color='blue', alpha=0.7)
mapview.plot_bc('WEL', color='red', alpha=0.9)

# Plot groundwater head contours (only in active areas)
# Our water head ranges between 85 (outflow) and 98 (inflow)
levels = np.arange(80, 100, 1)

# Use attractive colormap to display head depth
contour_set = mapview.contour_array(head_data, levels=levels, cmap='viridis')
plt.clabel(contour_set, fmt='%.0f', colors='white', fontsize=10)

plt.title('Groundwater Head Contours (GIS-Based Model)')
plt.xlabel('UTM X (m)')
plt.ylabel('UTM Y (m)')

output_image = 'final_gis_contours.png'
plt.savefig(output_image, dpi=300, bbox_inches='tight')
print(f"BINGO! Map saved successfully as '{output_image}'.")