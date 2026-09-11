import os
import numpy as np
import matplotlib.pyplot as plt
import flopy

# ۱. تعریف مسیرها
sim_name = 'my_first_model'
workspace = os.path.join(os.getcwd(), 'model_output')
hds_file = os.path.join(workspace, f'{sim_name}.hds')

# ۲. خواندن فایل باینری تراز آب (Head)
headobj = flopy.utils.HeadFile(hds_file)
# دریافت داده‌های اولین استپ زمانی
head_data = headobj.get_data()

print("Head data shape (Layers, Rows, Columns):", head_data.shape)
print(f"Max head: {np.max(head_data):.2f} m")
print(f"Min head: {np.min(head_data):.2f} m")

# ۳. بارگذاری مجدد مدل برای استفاده از ابزارهای رسم FloPy
print("Loading model for spatial context...")
sim = flopy.mf6.MFSimulation.load(sim_name=sim_name, sim_ws=workspace, verbosity_level=0)
gwf = sim.get_model(sim_name)

# ۴. رسم کانتورهای تراز آب (نقشه هم‌پتانسیل)
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')

# استفاده از ابزار PlotMapView برای رسم روی گرید مدل
mapview = flopy.plot.PlotMapView(model=gwf, ax=ax)

# رسم خطوط شبکه‌بندی (گرید)
mapview.plot_grid(linewidth=0.5, color='gray', alpha=0.5)

# رسم سلول‌های شرط مرزی (سلول‌های قرمز رنگ)
mapview.plot_bc("CHD", color='red', alpha=0.7)

# رسم کانتورهای آب
# مقادیر بین 40 تا 50 را به 11 خط تقسیم می‌کنیم
levels = np.linspace(40, 50, 11)
contour_set = mapview.contour_array(head_data, levels=levels, cmap='Blues_r')
plt.clabel(contour_set, fmt='%.1f', colors='black', fontsize=10)

plt.title('Groundwater Head Contours (Steady-State)')
plt.xlabel('X (m)')
plt.ylabel('Y (m)')

print("Opening plot window...")
# plt.show()

# ذخیره عکس به جای نمایش مستقیم
output_image = 'head_contours.png'
plt.savefig(output_image, dpi=300, bbox_inches='tight')
print(f"Plot saved successfully as '{output_image}' in your project folder.")