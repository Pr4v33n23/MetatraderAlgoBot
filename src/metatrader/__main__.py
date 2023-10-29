import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pytz

from metatrader.utils.factory import MetatraderFactory
from metatrader.strategies.ema_crossover import EMACrossover


metatrader = MetatraderFactory.get_metatrader()
sql_connection = sqlite3.connect("./data/tickers_data.db")

mt5 = metatrader.connect()