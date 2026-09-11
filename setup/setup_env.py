import flopy
import os

# Create a folder named 'bin' in current directory to store MODFLOW executables
bin_dir = os.path.join(os.getcwd(), 'bin')
if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)

print("Downloading MODFLOW executables... This might take a minute.")
# Download executables and place them in the bin folder
flopy.utils.get_modflow(bindir=bin_dir)
print(f"Done! Check the '{bin_dir}' folder.")