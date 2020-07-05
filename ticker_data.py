# ticker_data.py
"""
market data from yfinance
"""
import yfinance as yf
import pickle
import os


class Ticker:
    def download_ticker(self, ticker, date):
        if os.path.exists('stocks/{0}.pickle'.format(ticker)):
            return
        d = yf.Ticker(ticker)
        with open('stocks/{0}.pickle'.format(ticker), 'wb') as f:
            pickle.dump({
                'price': d.history(start=date)
            }, f)

    def load_ticker(self, ticker):
        with open('stocks/{0}.pickle'.format(ticker), 'rb') as f:
            dump = pickle.load(f)
        raw = dump['price']
        return raw[['Close', 'Dividends', 'Stock Splits']] \
            .rename(columns={'Date': 'date', 'Close': f'{ticker} price', 'Dividends': f'{ticker} dividends',
                             'Stock Splits': f'{ticker} splits'})

    def ticker_at_date(self, ticker, date):
        df = self.load_ticker(ticker)
        df = df[df.index >= date]
        return df['{0} price'.format(ticker)].iloc[0]
