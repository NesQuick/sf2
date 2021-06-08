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


rainfall = df['Rain']
depo_veloc = {'2_5': 0.0009, '10': 0.004}  # default values from [1] (m/s)
rain_accum_period = pd.Timedelta('1h')     # default
cleaning_threshold = 0.5
tilt = 45
# pm2_5 = imperial_county['PM2_5'].values
# pm10 = imperial_county['PM10'].values
# run the hsu soiling model
soiling_ratio = soiling.hsu(rainfall, cleaning_threshold, tilt, 0.0009, 0.004,
                            depo_veloc=depo_veloc,
                            rain_accum_period=rain_accum_period)

daily_soiling_ratio = soiling_ratio.resample('d').mean()
fig, ax1 = plt.subplots(figsize=(8, 2))
ax1.plot(daily_soiling_ratio.index, daily_soiling_ratio, marker='.',
         c='r', label='hsu function output')
ax1.set_ylabel('Daily Soiling Ratio')
ax1.set_ylim(0.65, 1.01)
ax1.set_title('Imperial County TMY')
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
