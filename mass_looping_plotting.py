import matplotlib.pyplot as plt
from numpy import busday_count
import pandas as pd
import os

DATASET_FOLDER = "data"
RESULTS_FOLDER = "mass_looping_results (2days)"

PLOT_FOLDER = "mass_looping_plots (2days)"

DATASET_NAMES = {
    "Bitcoin": "USDT_BTC.csv",
    "Dogecoin": "USDT_DOGE.csv",
    "Ethereum": "USDT_ETH.csv",
    "Litecoin": "USDT_LTC.csv",
    "XRP": "USDT_XRP.csv"
    }

DATASET_PATHS = {key: os.path.join(DATASET_FOLDER, DATASET_NAMES[key]) for key in DATASET_NAMES.keys()}

RESULTS_PATHS = {coin: os.path.join(RESULTS_FOLDER, f"{coin}_fixed_window_results.csv") for coin in DATASET_NAMES.keys()}

for coin in RESULTS_PATHS.keys():
    df = pd.read_csv(RESULTS_PATHS[coin])

    plt.plot(df["Window width in mins"], df["strategy"], label=f"{coin} strategy")
    plt.hlines(y=df["buy_and_hold"][0], xmin=min(df["Window width in mins"]), xmax=max(df["Window width in mins"]), label="Buy and hold", color="red")
    plt.hlines(y=0, xmin=min(df["Window width in mins"]), xmax=max(df["Window width in mins"]), linestyles="-", color="grey")

    plt.xlabel("Lookback interval (mins)")
    plt.ylabel("Percentage profit")
    plt.title(f"{coin} - Strategy performance for varying intervals")
    plt.legend(loc="lower right")
    
    plt.savefig(os.path.join(PLOT_FOLDER, f"strategy for {coin}"))

    plt.clf()

for coin in RESULTS_PATHS.keys():
    df = pd.read_csv(RESULTS_PATHS[coin])

    plt.plot(df["Window width in mins"], df["total_trades"], label=f"{coin} total trades")

plt.xlabel("Lookback interval (mins)")
plt.ylabel("Number of trades")
plt.title("Number of trades for different coins")
plt.legend()
plt.xlim(left = 0)
plt.ylim(bottom = 0)
plt.savefig(os.path.join(PLOT_FOLDER, "trade volumes"))
plt.show()





    # plt.plot()