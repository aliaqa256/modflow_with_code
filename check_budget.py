import os
import numpy as np
import flopy

# ۱. تعریف مسیرها
sim_name = 'my_first_model'
workspace = os.path.join(os.getcwd(), 'model_output')
cbc_file = os.path.join(workspace, f'{sim_name}.cbc')

# ۲. خواندن فایل باینری بیلان (Cell Budget File)
cbb = flopy.utils.CellBudgetFile(cbc_file)

# ۳. نمایش لیست تمام پارامترهای ذخیره شده در فایل
print("--- Available Budget Terms ---")
terms = cbb.get_unique_record_names()
for t in terms:
    print(f"- {t.decode('utf-8').strip()}")

# ۴. استخراج دیتای مربوط به چاه‌ها (WEL)
# متد get_data یک لیست برمی‌گردونه، ما داده‌های اولین (و تنها) دوره زمانی رو می‌خوایم [0]
wel_data = cbb.get_data(text='WEL')[0]
total_wel_flow = np.sum(wel_data['q'])

# ۵. استخراج دیتای مربوط به مرزهای سر ثابت (CHD)
chd_data = cbb.get_data(text='CHD')[0]
total_chd_flow = np.sum(chd_data['q'])

print("\n--- Steady-State Water Budget ---")
print(f"Total Well Extraction: {total_wel_flow:.2f} m3/day")
print(f"Net Constant Head Flow: {total_chd_flow:.2f} m3/day")
print("-" * 33)

# بررسی بقای جرم (مجموع ورودی‌ها و خروجی‌ها باید نزدیک به صفر باشد)
mass_balance_error = total_wel_flow + total_chd_flow
print(f"Mass Balance Error: {mass_balance_error:.2e} m3/day")