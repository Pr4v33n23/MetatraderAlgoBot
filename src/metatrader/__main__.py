import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from utils.factory import MetatraderFactory

metatrader = MetatraderFactory.get_metatrader()

sns.set_theme()

mt5 = metatrader.connect()

symbol = "AAPL"
bars = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 100)

df = pd.DataFrame(bars)
df["time"] = pd.to_datetime(df["time"], unit="s")
sns.lineplot(data=df, x="time", y="close")


plt.show()
metatrader.disconnect()
