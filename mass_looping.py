from genericpath import isfile
import pandas as pd
import numpy as np
from talib.abstract import *
import matplotlib.pyplot as plt
import sys
import breakout_lib as bl
import multiprocessing

from momentum_algo import FixedWindowAlgo

#local imports
from gemini_modules import engine
import os

DATASET_FOLDER = "data"
DATASET_NAMES = {
    "Bitcoin": "USDT_BTC.csv",
    "Dogecoin": "USDT_DOGE.csv",
    "Ethereum": "USDT_ETH.csv",
    "Litecoin": "USDT_LTC.csv",
    "XRP": "USDT_XRP.csv"
    }

DATASET_PATHS = {key: os.path.join(DATASET_FOLDER, DATASET_NAMES[key]) for key in DATASET_NAMES.keys()}

def analyse_coin(coin):
        results = {
            "Coin": [],
            "Window width in mins": [],
            "buy_and_hold": [],
            "hold_net_profit":[],
            "strategy": [],
            "strategy_net_profit": [],
            "longs": [],
            "sells": [],
            "shorts":[],
            "covers":[],
            "total_trades":[]
        }
        
        out_file_name = f"mass_looping_results/{coin}_fixed_window_results.csv"
        if os.path.isfile(out_file_name):
            raise AssertionError(f"File {out_file_name} already exists.")
        
        df = pd.read_csv(DATASET_PATHS[coin], parse_dates=[0])

        for lookback_period in range(1, 240, 4):#97):
            backtest = engine.backtest(df)
            backtest.start(100, logic=FixedWindowAlgo(
                lookback_tick_width=lookback_period, total_df_length=len(df), should_plot=False
                ).logic)

            run_result = backtest.results()

            results["Coin"].append(coin)
            results["Window width in mins"].append(lookback_period*30)

            for key in run_result.keys():
                results[key].append(run_result[key])

        results_df = pd.DataFrame(results)
        results_df.to_csv(out_file_name)
        return

if __name__ == "__main__":
    processes = []
    for coin in DATASET_NAMES.keys():
        process = multiprocessing.Process(target=analyse_coin, args=(coin,))
        process.start()
        processes.append(process)
    
    for process in processes:
        process.join()

    print("DONE!")
