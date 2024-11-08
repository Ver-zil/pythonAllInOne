import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

plt.style.use('seaborn-v0_8')
idx = 0

sheet = ['tmp_jl_gun_run_stat', 'tmp_jl_gun_run', 'tmp_jl_gun_online_trans']
col = ['运行状态开始时间=状态变化时的数据时间', '数据时间', '数据时间']
file = r'C:\Users\11435\Documents\WeChat Files\wxid_qdd1ha85u00n22\FileStorage\File\2023-11\tmp_jl_run_sat.sql123.xlsx'
df = pd.read_excel(file, sheet_name=sheet[idx])

print(df.info())

df['时刻'] = pd.to_datetime(df[col[idx]]).dt.time
df['时分'] = df['时刻'].apply(lambda x: x.hour * 60 + x.minute)
df['时间档次'] = pd.cut(df['时分'], bins=range(0, 1441, 30),
                    labels=pd.date_range(start='00:00', end='23:59', freq='30min').time)
sample_df = df.sample(n=1000, random_state=0)
sample_df['时分'] = sample_df['时分'].apply(lambda x: x / 60)
mean_value = sample_df['时分'].mean()
var_value = sample_df['时分'].var()

x = sample_df['时分']
x_range = range(int(x.min()), int(x.max()) + 1)
y = norm.pdf(x_range, mean_value, var_value ** 0.5)

# 绘制直方图和正态分布曲线
plt.hist(x, bins=48, density=True, alpha=0.6, color='b', label='Histogram')
plt.plot(x_range, y, 'r--', label='Normal Distribution')
plt.title('Histogram and Normal Distribution Curve')
plt.xlabel('Time (hours)')
plt.ylabel('Density')
plt.legend()
plt.show()

print(f'the mean value is {mean_value} , the var value is4 {var_value}')
save_path = r'.\sample_df_' + sheet[idx]
# plt.savefig(save_path + '.png')
# sample_df.to_excel(save_path + '.xlsx', index=False)
