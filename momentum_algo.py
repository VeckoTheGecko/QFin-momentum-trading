import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gemini_modules import engine
import random as rand


class BaseAlgo:
    """A foundation algorithm class that is used to initialise:
    - Buy points
    - Sell points
    - Plotting of support, resistance, buypoints etc.
    """

    def __init__(self, total_df_length: int, should_plot: bool, plotting_options=None):
        self.total_df_length = total_df_length
        self.should_plot = should_plot

        # Setting up lists to store buy and sell points
        self.buypoints = []
        self.sellpoints = []

        self.default_plotting_options = {
                "lines": {
                    "open": False,
                    "close": True,
                    "low": True,
                    "high": True,
                    "support": True,
                    "resistance": True,
                },
                "points": {"buy": True, "sell": True},
                "tick-interval": (0, total_df_length - 1),
            }
        
        if plotting_options is None:
            self.plotting_options = self.default_plotting_options
        else:
            # Filling custom options with missing defaults
            for key in self.default_plotting_options.keys():
                if key not in plotting_options:
                    plotting_options[key] = self.default_plotting_options[key]

            self.plotting_options = plotting_options

    def calc_support_df(self, lookback):
        """Base algo doesnt have an associated support,
        so just returns nan array"""
        return np.full_like(lookback, np.nan)
    
    def calc_resistance_df(self, lookback):
        """Base algo doesnt have an associated resistance,
        so just returns nan array"""
        return np.full_like(lookback, np.nan)


    def plot(self, lookback: pd.DataFrame):
        _, ax1 = plt.subplots()
        ax1.set_xlabel("Time")

        start_index, stop_index = self.plotting_options["tick-interval"]
        buypoints_array = np.array(self.buypoints)
        sellpoints_array = np.array(self.sellpoints)

        lookback['Resistance'] = self.calc_resistance_df(lookback)
        lookback['Support'] = self.calc_support_df(lookback)

        if self.plotting_options["lines"]["open"]:
            # trim close prices
            prices = lookback["open"].iloc[start_index:stop_index]
            prices.plot(label="Open Price")
            ax1.set_ylabel("Price (USDT)")

        if self.plotting_options["lines"]["close"]:
            # trim close prices
            prices = lookback["close"].iloc[start_index:stop_index]
            prices.plot(label="Close Price", color="black")
            ax1.set_ylabel("Price (USDT)")

        if self.plotting_options["lines"]["low"]:
            # trim close prices
            prices = lookback["low"].iloc[start_index:stop_index]
            prices.plot(label="Low Price")

        if self.plotting_options["lines"]["high"]:
            # trim close prices
            prices = lookback["high"].iloc[start_index:stop_index]
            prices.plot(label="High Price")

        if self.plotting_options["lines"]["resistance"]:
            # trim close prices
            prices = lookback["Resistance"].iloc[start_index:stop_index]
            prices.plot(label="Resistance Price")

        if self.plotting_options["lines"]["support"]:
            # trim close prices
            prices = lookback["Support"].iloc[start_index:stop_index]
            prices.plot(label="Support Price")

        # Plotting points
        if self.plotting_options["points"]["buy"]:
            in_range_mask = (start_index <= buypoints_array) & (buypoints_array<= stop_index)
            buy = buypoints_array[in_range_mask]  # trim buy points

            plt.scatter(buy, lookback["close"][buy], color="red", label="Buy Point")

        if self.plotting_options["points"]["sell"]:
            in_range_mask = (start_index <= sellpoints_array) & (sellpoints_array<= stop_index)
            sell = sellpoints_array[in_range_mask]  # trim sell points
            plt.scatter(
                sell, lookback["close"][sell], color="green", label="Sell Point"
            )

        plt.legend()
        plt.show()  # graph it
        return

class AdaptiveWindowAlgo(BaseAlgo):
    """This algorithm will use a window of adaptive length to calculate support and resistance
    Window length is calculated as a function of volatility
    """
    def __init__(
        self,
        volatility_tick_width: int,
        total_df_length: int,
        should_plot: bool,
        plotting_options=None,
    ):
        self.volatility_tick_width=volatility_tick_width
        
        super().__init__(total_df_length, should_plot, plotting_options)    
        return


    def logic(self, account: engine.exchange.Account, lookback: pd.DataFrame):
        """Function to be passed to the backtesting module."""
        # Just started. Skip iteration
        current_index = len(lookback) - 1

        if current_index == 0:
            return

        current_price = lookback["close"][current_index]
        support = self.calc_support_df(lookback)[current_index - 1]
        resistance = self.calc_resistance_df(lookback)[current_index - 1]


        if resistance < current_price:
            # Enter long position
            self.enter_long(account=account, current_price=current_price)
            self.buypoints.append(current_index)

        if support > current_price:
            # Close out all long positions
            self.close_long(account=account, current_price=current_price)
            self.sellpoints.append(current_index)
            pass

        # Whether to plot
        if current_index == self.total_df_length-1 and self.should_plot:
            self.plot(lookback=lookback)

        return

    def calculate_lookback_period(self, lookback: pd.DataFrame)-> float:
        lookback_period=rand.randint(0,100)
        price_df=lookback["close"].rolling(window=self.volatility_tick_width)
        momentum=abs(price_df[0]-price_df[self.volatility_tick_width-1])
        volatility=0
        for i in range(len(price_df)-1):
            volatility=volatility+abs(price_df[i+1]-price_df[i])
        efficiency_ratio=momentum/volatility

        lookback_period=int(100*efficiency_ratio)
        #print(a)
        return lookback_period
    

    def calc_support_df(self, lookback: pd.DataFrame) -> float:
        """Calculates the support df and returns it"""
        self.lookback_period=self.calculate_lookback_period(lookback) #calculate_lookback()
        if (self.lookback_period>len(lookback)):
            window=len(lookback)-1
        else:
            window=self.lookback_period
        support_df = lookback["low"].rolling(window=window).min()
        return support_df

    def calc_resistance_df(self, lookback: pd.DataFrame) -> float:
        """Calculates the resistance df and returns it"""
        self.lookback_period=self.calculate_lookback_period(lookback)
        if (self.lookback_period>len(lookback)):
            window=len(lookback)-1
        else:
            window=self.lookback_period
        support_df = lookback["high"].rolling(window=window).max()
        return support_df

    def enter_long(self, account: engine.exchange.Account, current_price: float):
        """Enters a long position with the whole portfolio."""
        if account.buying_power > 0:
            # use 100% of portfolio to buy
            account.enter_position(
                "long", entry_capital=account.buying_power, entry_price=current_price
            )
        return

    def close_long(self, account: engine.exchange.Account, current_price: float):
        """Closing all positions in the portfolio."""
        for position in account.positions:
            if position.type_ == "long":
                # use 100% of portfolio to sell
                account.close_position(position, 1, current_price)
        return


class FixedWindowAlgo(BaseAlgo):
    """This algorithm will use a fixed window of specified length in order to calculate support and resistance.
    :param lookback_tick_width: how many ticks back to calculate support and resistance.
    :total_df_length: length of the total dataframe
    """

    def __init__(
        self,
        lookback_tick_width: int,
        total_df_length: int,
        should_plot: bool,
        plotting_options=None,
    ):
        self.lookback_period = lookback_tick_width

        super().__init__(total_df_length, should_plot, plotting_options)
        return

    def logic(self, account: engine.exchange.Account, lookback: pd.DataFrame):
        """Function to be passed to the backtesting module."""
        # Just started. Skip iteration
        current_index = len(lookback) - 1

        if current_index == 0:
            return

        current_price = lookback["close"][current_index]
        support = self.calc_support_df(lookback)[current_index - 1]
        resistance = self.calc_resistance_df(lookback)[current_index - 1]


        if resistance < current_price:
            # Enter long position
            self.enter_long(account=account, current_price=current_price)
            self.buypoints.append(current_index)

        if support > current_price:
            # Close out all long positions
            self.close_long(account=account, current_price=current_price)
            self.sellpoints.append(current_index)
            pass

        # Whether to plot
        if current_index == self.total_df_length-1 and self.should_plot:
            self.plot(lookback=lookback)

        return

    def calc_support_df(self, lookback: pd.DataFrame) -> float:
        """Calculates the support df and returns it"""
        if (self.lookback_period>len(lookback)):
            window=len(lookback)-1
        else:
            window=self.lookback_period
        support_df = lookback["low"].rolling(window=window).min()
        return support_df

    def calc_resistance_df(self, lookback: pd.DataFrame) -> float:
        """Calculates the resistance df and returns it"""
        if (self.lookback_period>len(lookback)):
            window=len(lookback)-1
        else:
            window=self.lookback_period
        support_df = lookback["high"].rolling(window=window).max()
        return support_df

    def enter_long(self, account: engine.exchange.Account, current_price: float):
        """Enters a long position with the whole portfolio."""
        if account.buying_power > 0:
            # use 100% of portfolio to buy
            account.enter_position(
                "long", entry_capital=account.buying_power, entry_price=current_price
            )
        return

    def close_long(self, account: engine.exchange.Account, current_price: float):
        """Closing all positions in the portfolio."""
        for position in account.positions:
            if position.type_ == "long":
                # use 100% of portfolio to sell
                account.close_position(position, 1, current_price)
        return
