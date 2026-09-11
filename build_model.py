import flopy
import os

# ۱. تنظیمات اولیه پروژه
# مسیر موتور محاسباتی (در لینوکس اسم فایل فقط mf6 است)
exe_name = os.path.join(os.getcwd(), 'bin', 'mf6')

# نام پروژه و مسیر ذخیره فایل‌های خروجی مدل
sim_name = 'my_first_model'
workspace = os.path.join(os.getcwd(), 'model_output')

# ۲. ساخت شیء شبیه‌ساز (Simulation)
sim = flopy.mf6.MFSimulation(
    sim_name=sim_name, 
    version='mf6', 
    exe_name=exe_name, 
    sim_ws=workspace
)

# ۳. تعریف دیتای سنتتیک هندسی آبخوان
Lx = 1000.0  # طول آبخوان (متر)
Ly = 1000.0  # عرض آبخوان (متر)
nrow = 10    # تعداد سطرها
ncol = 10    # تعداد ستون‌ها
nlay = 1     # تعداد لایه‌ها 

delr = Lx / ncol  # طول هر سلول در راستای سطرها (متر)
delc = Ly / nrow  # عرض هر سلول در راستای ستون‌ها (متر)

top = 50.0   # تراز بالای آبخوان از سطح مبنا (متر)
botm = 0.0   # تراز کف آبخوان از سطح مبنا (متر)

print(f"Simulation '{sim_name}' initialized.")
print(f"Grid: {nlay} Layer(s), {nrow} Rows, {ncol} Columns.")
print(f"Cell dimensions: {delr}m x {delc}m")



# =====================================================2
# ۴. ساخت پکیج دامنه‌بندی زمانی (TDIS)
# یک دوره تنش (Stress Period) با طول ۱ روز تعریف می‌کنیم (برای حالت ماندگار عددش مهم نیست)
tdis = flopy.mf6.ModflowTdis(
    sim, 
    pname='tdis', 
    time_units='DAYS', 
    nper=1, 
    perioddata=[(1.0, 1, 1.0)] 
)

# ۵. ساخت مدل جریان آب زیرزمینی (GWF) و اتصال آن به شبیه‌ساز
gwf = flopy.mf6.ModflowGwf(
    sim, 
    modelname=sim_name, 
    save_flows=True
)

# ۶. ساخت پکیج دامنه‌بندی مکانی (DIS) و اتصال آن به مدل جریان (GWF)
dis = flopy.mf6.ModflowGwfdis(
    gwf, 
    nlay=nlay, 
    nrow=nrow, 
    ncol=ncol, 
    delr=delr, 
    delc=delc, 
    top=top, 
    botm=botm
)

print("Packages TDIS and DIS successfully added to the GWF model.")


# ============================================================3
# ۷. تعیین شرایط اولیه (Initial Conditions - IC)
# فرض می‌کنیم تراز اولیه آب در تمام سلول‌های مدل 45 متر است
ic = flopy.mf6.ModflowGwfic(gwf, pname='ic', strt=45.0)

# ۸. تعیین خواص فیزیکی و هیدرولیکی آبخوان (NPF)
# icelltype=0 یعنی آبخوان محصور (Confined) است تا محاسبات فعلاً خطی و ساده بماند
# k=10.0 یعنی هدایت هیدرولیکی 10 متر بر روز است
npf = flopy.mf6.ModflowGwfnpf(
    gwf, 
    pname='npf', 
    save_flows=True,
    icelltype=0,  
    k=10.0        
)

# ۹. تعریف شرایط مرزی سر ثابت (Constant Head Boundary - CHD)
# ساخت لیست سلول‌های مرزی برای ستون اول (چپ) و ستون آخر (راست)
chd_list = []
for row in range(nrow):
    # لبه چپ: سلول‌های (لایه 0، سطر متغیر، ستون 0) با تراز 50 متر
    chd_list.append([(0, row, 0), 50.0])
    # لبه راست: سلول‌های (لایه 0، سطر متغیر، ستون آخر) با تراز 40 متر
    chd_list.append([(0, row, ncol - 1), 40.0])

chd = flopy.mf6.ModflowGwfchd(
    gwf,
    pname='chd',
    stress_period_data=chd_list
)

print("Initial conditions, NPF (hydraulic conductivity), and CHD boundaries added.")






# ۹.۵. اضافه کردن پکیج چاه (WEL Package)
# تعریف یک چاه در لایه 0، سطر 5، ستون 5 (دقیقاً وسط مدل)
# مقدار پمپاژ: -2000.0 (علامت منفی یعنی استخراج و خروج آب از سیستم)
wel_spd = [[(0, 5, 5), -2000.0]]

wel = flopy.mf6.ModflowGwfwel(
    gwf,
    pname='wel',
    stress_period_data=wel_spd
)
print("Well package added: Pumping at center (-2000 m3/day).")













# ===================================================4

# ۱۰. تنظیمات کنترل خروجی (Output Control - OC)
# درخواست ذخیره تراز آب (HEAD) و بیلان جریان (BUDGET) برای تمام سلول‌ها
saverecord = [('HEAD', 'ALL'), ('BUDGET', 'ALL')]
oc = flopy.mf6.ModflowGwfoc(
    gwf, 
    pname='oc', 
    saverecord=saverecord, 
    head_filerecord=f'{sim_name}.hds', 
    budget_filerecord=f'{sim_name}.cbc'
)

# ۱۱. اضافه کردن حل‌گر ماتریسی (Iterative Model Solver - IMS)
ims = flopy.mf6.ModflowIms(sim, pname='ims', complexity='SIMPLE')

# ۱۲. تولید فایل‌های ورودی برای مدفلو
print("Writing simulation files to disk...")
sim.write_simulation()

# ۱۳. اجرای موتور محاسباتی MODFLOW 6
print("Running MODFLOW 6...")
success, buff = sim.run_simulation()

if success:
    print("Model ran successfully!")
else:
    print("Model run failed. Please check the output for errors.")