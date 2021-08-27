import pandas as pd
import numpy as np
from talib.abstract import *
import matplotlib.pyplot as plt
import sys
import breakout_lib as bl

#local imports
from gemini_modules import engine

#reads in crypto data
df = pd.read_csv("data/USDT_BTC.csv",parse_dates=[0])

#globals
lookback_period = 48*2#*30

buypoints = np.array([]) #for graphing only
sellpoints = np.array([]) #for graphing only

#backtesting
backtest = engine.backtest(df)

'''Algorithm function, lookback is a data frame parsed to function continuously until end of initial dataframe is reached.'''
def logic(account, lookback):
    global buypoints,sellpoints
    try: 
        lookback['Support'] = lookback['low'].rolling(window = lookback_period).min() #update PMA
        lookback['Resistance'] = lookback['high'].rolling(window = lookback_period).mean() #update VMA
                    
        today = len(lookback)-1 #latest data frame row index

        if today==0:
            return

        if(lookback['Support'][today-1] > lookback['close'][today]): 
            # Close out long position
            for position in account.positions:
                if position.type_ == 'long':
                    account.close_position(position, 1, lookback['close'][today]) #use 100% of portfolio to sell
                    sellpoints = np.append(sellpoints,today) #for graphing only

        else:
            if(lookback['Resistance'][today-1] < lookback['close'][today]):
                if(account.buying_power>0):
                    # Enter long position
                    account.enter_position('long', account.buying_power, lookback['close'][today]) #use 100% of portfolio to buy
                    buypoints = np.append(buypoints,today) #for graphing only                    
    
        
        if(len(lookback)==len(df)): #after running algorithm, graph it.
            base_plot_settings = {
                "lines": {
                    "open":False,
                    "close":True,
                    "low":True,
                    "high":True,
                    "support":True,
                    "resistance":True
                    },
                "points":{
                    "buy":True,
                    "sell":True
                    }
                }
            plotAlgorithm(
                lookback=lookback,
                startIndex = 0, 
                size = len(lookback)-1,
                settings = base_plot_settings
                )
 
    except Exception as e:
        print(e)
    pass # Handles lookback errors in beginning of dataset





'''
Graphs algorithm with given parameters.
Lookback is the dataframe.
Startindex is the index to start the graphing from and continues for 'size' units. 
plotPrice,plotBuySell,plotPMA,plotVolume,plotVMA are booleans to determine what is graphed.
'''
def plotAlgorithm(lookback: pd.DataFrame, startIndex:int, size:int, settings:dict):
    _, ax1 = plt.subplots()
    ax1.set_xlabel("Time")
    
    
    if settings["lines"]["open"]:
        close_price = lookback['open'].iloc[startIndex:startIndex+size] #trim close prices
        close_price.plot(label='Open Price')
        ax1.set_ylabel('Price (USDT)')

    if settings["lines"]["close"]:
        close_price = lookback['close'].iloc[startIndex:startIndex+size] #trim close prices
        close_price.plot(label='Close Price',color="black")
        ax1.set_ylabel('Price (USDT)')

    if settings["lines"]["low"]:
        resistance_price = lookback['low'].iloc[startIndex:startIndex+size] #trim close prices
        resistance_price.plot(label='Low Price')

    if settings["lines"]["high"]:
        resistance_price = lookback['high'].iloc[startIndex:startIndex+size] #trim close prices
        resistance_price.plot(label='High Price')

    if settings["lines"]["resistance"]:
        resistance_price = lookback['Resistance'].iloc[startIndex:startIndex+size] #trim close prices
        resistance_price.plot(label='Resistance Price')

    if settings["lines"]["support"]:
        support_price = lookback['Support'].iloc[startIndex:startIndex+size] #trim close prices
        support_price.plot(label='Support Price')    

    if settings["points"]["buy"]:
        buy = buypoints[(buypoints >= startIndex) & (buypoints <= startIndex+size)] #trim buy points
        plt.scatter(buy,lookback['close'][buy],color= 'red',label='Buy Point')

    if settings["points"]["sell"]:
        sell = sellpoints[(sellpoints >= startIndex) & (sellpoints <= startIndex+size)] #trim sell points
        plt.scatter(sell,lookback['close'][sell],color= 'green',label='Sell Point')
   
    
    plt.legend()
    plt.show() #graph it

if __name__ == "__main__":
    backtest.start(100, logic)
    backtest.results()
    # backtest.chart(show_trades=True)