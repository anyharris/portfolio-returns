# data_manipulation.py
"""
next step is to make it work with different buy dates
then make sure it works buying more of the same stock and selling a part of a stock holding
I'll probably need to break down the manipulate function into parts
part 1 - fix quantity
part 2 - keep SPY normalised
part 3 - graph that fully normalises and just compares % returns over time
part 4 - what's taking so long?
part 5 - make it a web app

to do: add initial price to portfolio csv. could make it optional
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from ticker_data import Ticker
import logging

log_format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
logging.basicConfig(filename='portfolio-app.log', level=logging.INFO, format=log_format)


def manipulate(ticker, qty_orig, data):
    """
    add information about quantity, accounting for splits since buying
    """
    qty_list = []
    qty = qty_orig
    for index, row in data.iterrows():
        """
        can add something here about date
        will also need to account for additional sells/buys at some point
        """
        if int(row[f'{ticker} splits']):
            qty *= int(row[f'{ticker} splits'])
        qty_list.append(qty)
    data[f'{ticker} qty'] = qty_list
    """
    add information for value of assets and dividends, accounting for stock splits
    """
    qm = [qty_list[-1] / x for x in qty_list]
    data[f'{ticker} price'] = data[f'{ticker} price'] * qm
    data[f'{ticker} dividends'] = data[f'{ticker} dividends'] * qm
    asset_value = []
    dividend_value = []
    d = 0
    for index, row in data.iterrows():
        if row[f'{ticker} dividends']:
            d += row[f'{ticker} dividends'] * qty
        asset_value.append(row[f'{ticker} price'] * row[f'{ticker} qty'])
        dividend_value.append(d)
    data[f'{ticker} asset value'] = asset_value
    data[f'{ticker} dividend value'] = dividend_value
    return data


# Download required market data from yfinance
tk = Ticker()
portfolio = pd.read_csv('example-portfolio.csv')
for index, row in portfolio.iterrows():
    tk.download_ticker(row['Ticker'], row['Date'])
tk.download_ticker('SPY', '1993-01-29')

# Load required market data from pickle files, manipulate the data, concatenate them together
frames = []
for index, row in portfolio.iterrows():
    data = tk.load_ticker(row['Ticker'])
    frames.append(manipulate(row['Ticker'], row['Qty'], data))
big_frame = pd.concat(frames, axis=1)

# sum the total portfolio value (asset value + total dividend payments)
an_iterator = filter(lambda x: 'value' in x, big_frame.columns.values)
sub = list(an_iterator)
logging.debug(sub)
big_frame['portfolio total value'] = big_frame[sub].sum(axis=1)
logging.debug(big_frame)

# get the SPY data to compare
data = tk.load_ticker('SPY')
data = data[data.index >= big_frame.index[0]]

# normalise the SPY initial qty so that the initial investment is the same
"""
I want to make a list for every item in the portfolio and then sum them
so I should move this up some
I need to split up 'manipulate' into 2 parts and make 2 lists of frames when looping through portfolio
"""
spy_qty = big_frame['portfolio total value'].iloc[0]/tk.ticker_at_date('SPY', big_frame.index[0])
spy_frame = manipulate('SPY', spy_qty, data)
an_iterator = filter(lambda x: 'value' in x, spy_frame.columns.values)
sub = list(an_iterator)
logging.debug('sub')
spy_frame['SPY total value'] = spy_frame[sub].sum(axis=1)
logging.debug(spy_frame)

# concatenate the portfolio big frame and the spy data frame
final_frame = pd.concat([big_frame, spy_frame], axis=1)
logging.debug(final_frame)

# graph portfolio value vs SPY value for equivalent initial investment
graph = sns.relplot(kind='line',
                    data=final_frame[['portfolio total value', 'SPY total value']])
graph.set(xlabel='Date', ylabel='Asset value')
plt.show()
