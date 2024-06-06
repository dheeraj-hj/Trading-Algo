import itertools
import os
import yfinance as yf
from pyalgotrade.optimizer import server
from pyalgotrade.barfeed import yahoofeed

def parameters_generator():
    instrument = ["SBIN"]
    emaPeriod = range(20, 51)
    return itertools.product(instrument, emaPeriod)

def download_data(ticker, start_date, end_date, file_path):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data.to_csv(file_path, index=False)
    return data


ticker = "SBIN.NS"  # Yahoo Finance ticker for Reliance Industries on BSE

if __name__ == '__main__':
    feed = yahoofeed.Feed()
    data_dir = "./data/"
    
    # Create the data directory if it does not exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Download data if not already present
    csv_path = os.path.join(data_dir, "SBIN.csv")
    
    if not os.path.isfile(csv_path):
        print(f"Downloading data for {ticker}...")
        download_data(ticker, "2010-01-01", "2023-01-01", csv_path)
    else:
        print(f"Using existing data for {ticker}")

    # Add bars from CSV file
    feed.addBarsFromCSV("SBIN", csv_path)
    
    # Check if data was loaded correctly
    if "SBIN" not in feed:
        raise Exception("Data for SBI was not loaded correctly into the feed.")
    
    print("Data loaded successfully, starting server...")
    
    # Run the server
    best_result = server.serve(feed, parameters_generator(), "localhost", 5000)
    if best_result:
        print("Best Parameters:", best_result.getParameters())
        print("Best Result:", best_result.getResult())
import logging
logging.basicConfig(level=logging.INFO)

