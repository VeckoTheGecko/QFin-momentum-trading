import pandas as pd
import numpy as np
from talib.abstract import *
import matplotlib.pyplot as plt
import sys
import breakout_lib as bl

from momentum_algo import FixedWindowAlgo, AdaptiveWindowAlgo

#local imports
from gemini_modules import engine
import os

DATASET_FOLDER = "data"
DATASET_NAMES = {
    "Bitcoin": "USDT_BTC.csv",
    "Ethereum": "USDT_ETH.csv",
    "Litecoin": "USDT_LTC.csv",
    "XRP": "USDT_XRP.csv"
    }

DATASET_PATHS = {key: os.path.join(DATASET_FOLDER, DATASET_NAMES[key]) for key in DATASET_NAMES.keys()}

#reads in crypto data
df = pd.read_csv(DATASET_PATHS["Bitcoin"], parse_dates=[0])

#globals
lookback_period = 48*2#*30

buypoints = np.array([]) #for graphing only
sellpoints = np.array([]) #for graphing only

#backtesting
backtest = engine.backtest(df)

if __name__ == "__main__":
    backtest.start(100, logic=AdaptiveWindowAlgo(
        minimum_tick_width=1,total_df_length=len(df), should_plot=True
        ).logic)
    backtest.results()
    # backtest.chart(show_trades=True)