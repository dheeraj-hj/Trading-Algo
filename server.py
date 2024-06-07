import itertools
import os
import yfinance as yf
import pandas as pd
from pyalgotrade.optimizer import server
from pyalgotrade.barfeed import csvfeed
from pyalgotrade.bar import Frequency
from pyalgotrade.barfeed import yahoofeed

def parameters_generator():
    instrument = [ticker]
    emaPeriod = range(5, 100)
    return itertools.product(instrument, emaPeriod)

# 5 minute timeframe

# def download_data(ticker, start_date, end_date, interval, file_path):
#     data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
#     data.reset_index(inplace=True)
#     data['Date Time'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
#     data = data.rename(columns={
#         'Open': 'Open',
#         'High': 'High',
#         'Low': 'Low',
#         'Close': 'Close',
#         'Volume': 'Volume',
#         'Adj Close': 'Adj Close'
#     })
#     data = data[['Date Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
#     data.to_csv(file_path, index=False)
#     return data
   

# Daily time frame

def download_data(ticker , start_date , end_date , file_path):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data.to_csv(file_path, index=False)
    return data


ticker = "NKE" # Yahoo Finance ticker 

if __name__ == '__main__':
    data_dir = "./data/"
    feed = yahoofeed.Feed()
    # Create the data directory if it does not exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Download data if not already present
    csv_path = os.path.join(data_dir, f"{ticker}.csv")
    
    if not os.path.isfile(csv_path):
        print(f"Downloading data for {ticker}...")
        # download_data(ticker, "2024-05-1", "2024-05-29", "5m", csv_path)
        download_data(ticker, "2020-05-1", "2024-05-29", csv_path)
    else:
        print(f"Using existing data for {ticker}")

    # Load the 5-minute data into a custom feed
    # feed = csvfeed.GenericBarFeed(Frequency.MINUTE * 5)
    feed.addBarsFromCSV(ticker, csv_path)
    
    # Check if data was loaded correctly
    if ticker not in feed:
        raise Exception(f"5-minute data for {ticker} was not loaded correctly into the feed.")
    
    print("Data loaded successfully, starting server...")
    
    # Run the server
    best_result = server.serve(feed, parameters_generator(), "localhost", 5000)
    if best_result:
        print("Best Parameters:", best_result.getParameters())
        print("Best Result:", best_result.getResult())

import logging
logging.basicConfig(level=logging.INFO)
