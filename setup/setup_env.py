import flopy
import os

# ساخت یک پوشه به اسم 'bin' در مسیر فعلی برای ذخیره موتورهای مدفلو
bin_dir = os.path.join(os.getcwd(), 'bin')
if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)

print("Downloading MODFLOW executables... This might take a minute.")
# دانلود موتورها و قرار دادن آن‌ها در پوشه bin
flopy.utils.get_modflow(bindir=bin_dir)
print(f"Done! Check the '{bin_dir}' folder.")