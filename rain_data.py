import pandas as pd
from datetime import datetime
import pvlib
from pvlib import soiling
from matplotlib import pyplot as plt

df = pd.read_csv("rain_data.csv")
for index, row in df.iterrows():
    if df.loc[index, "Temp"] < 0:
        df.loc[index, "Rain"] = 0
    df.loc[index, "Date"] = str(df.loc[index, "Date"])

df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y'))
df = df.set_index('Date')
# df.to_csv("rain_data_prep.csv")
# df["Rain"].plot(legend=True, title='Moscow rain data', figsize=(10, 5), grid=False)
# plt.show()


rainfall = df['Rain']
depo_veloc = {'2_5': 0.0009, '10': 0.004}  # default values from [1] (m/s)
rain_accum_period = pd.Timedelta('1h')     # default
cleaning_threshold = 0.5
tilt = 45
# pm2_5 = imperial_county['PM2_5'].values
# pm10 = imperial_county['PM10'].values
# run the hsu soiling model
soiling_ratio = soiling.hsu(rainfall, cleaning_threshold, tilt, 0.001145, 0.002603,
                            depo_veloc=depo_veloc,
                            rain_accum_period=rain_accum_period)

daily_soiling_ratio = soiling_ratio.resample('d').mean()
daily_soiling_ratio = pd.DataFrame(daily_soiling_ratio, columns = ["SR"])

for index, row in daily_soiling_ratio.iterrows():
    daily_soiling_ratio.loc[index, "SR"] = daily_soiling_ratio.loc[index, "SR"] + (1 - daily_soiling_ratio.loc[index, "SR"])/2

df_sr = daily_soiling_ratio.copy(deep = True)
df_sr["LOSS"] = abs(df_sr["SR"]*0)
for index, row in df_sr.iterrows():
    df_sr.loc[index, "LOSS"] = 1 - df_sr.loc[index, "SR"]
print(df_sr["LOSS"].max())

fig, ax1 = plt.subplots(figsize=(8, 2))
ax1.plot(daily_soiling_ratio.index, daily_soiling_ratio, marker='.',
         c='r', label='hsu function output')
ax1.set_ylabel('Daily Soiling Ratio')
ax1.set_ylim(0.55, 1.01)
ax1.set_title('MOSCOW TMY')
ax1.legend(loc='center left')

daily_rain = rainfall.resample('d').sum()
ax2 = ax1.twinx()
ax2.plot(daily_rain.index, daily_rain, marker='.',
         c='c', label='daily rainfall')
ax2.set_ylabel('Daily Rain (mm)')
ax2.set_ylim(-10, 50)
ax2.legend(loc='center right')
fig.tight_layout()
fig.show()
plt.show()
