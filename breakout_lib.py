def return_support(asset_history, ticks):
    """
    Input:
        asset_history       historical price movement of asset
        ticks               integer number of ticks 
    
    Output:
        support_level       price at which a SELL recommendation is issued
                            i.e. lowest price of asset over the defined number of ticks
    """
    prices = asset_history["low"][-ticks:]
    
    support_level = min(prices)
    return support_level

def return_resistance(asset_history, ticks):
    """
    Input:
        asset_history       historical price movement of asset
        ticks               integer number of ticks 
    
    Output:
        resistance_level    price at which a BUY recommendation is issued
                            highest price of asset over the defined number of ticks
    """
    prices = asset_history["high"][-ticks:]
    
    resistance_level = max(prices)
    return resistance_level

def monitor_price(asset_history):
    """
    Used to manage portfolio
    """
    return -1