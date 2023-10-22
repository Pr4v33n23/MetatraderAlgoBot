import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

from utils.factory import MetatraderFactory

metatrader = MetatraderFactory.get_metatrader()
sql_connection = sqlite3.connect('src\\metatrader\\data\\tickers_data.db')

sns.set_theme()

mt5 = metatrader.connect()

symbol = "AAPL"
bars = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 1000)

df = pd.DataFrame(bars)
df["time"] = pd.to_datetime(df["time"], unit="s")
sns.lineplot(data=df, x="time", y="close")

df.to_sql('aapl', con=sql_connection, if_exists='replace')

metatrader.disconnect()
