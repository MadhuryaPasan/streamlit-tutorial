import yfinance as yf
import streamlit as st
import pandas as pd

st.write(
    """
         # Simple Stock Price App
         shown are the stock closing price and volume of google!
         """
)

# define ticker symbol

tickerSymbol = "GOOGL"
# tickerSymbol = "LKR=X"

# get data on this ticker
tickerData = yf.Ticker(tickerSymbol)

# get the historical prices for this ticker
tickerDf = tickerData.history(period="1y")

# tickerDf = tickerData.history(start = '2010-1-1', end = '2025-8-13')



st.line_chart(tickerDf["Close"])  # closing price
st.line_chart(tickerDf["Volume"]) # number of shares traded
