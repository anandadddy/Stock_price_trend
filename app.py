import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from keras.models import load_model
import streamlit as st

start = '2010-01-01'
end = '2026-01-31'
start = '2010-01-01'
st.title('Stock Trend Prediction')

user_input = st.text_input('Enter Stock Ticker', 'AAPL')

def fetch_with_suggestions(ticker, start, end):
    # Normalize and build candidate tickers without duplicating suffixes
    t = (ticker or '').strip()
    if not t:
        return None, None, {}

    base = t.split('.')[0].upper()
    seen = set()
    candidates = []

    def add(c):
        if c and c not in seen:
            seen.add(c)
            candidates.append(c)

    # Try the user-provided variant first
    add(t)
    add(t.upper())

    # If user provided a suffix (e.g., 'SBI.NS'), also try the base (e.g., 'SBI')
    if '.' in t:
        add(base)

    # Common suffixes to try on the base only
    suffixes = ['.NS', '.BO', '.L', '.AX']
    for s in suffixes:
        add(base + s)

    tried = {}
    for cand in candidates:
        try:
            df_try = yf.download(cand, start=start, end=end, progress=False)
            if df_try is not None and not df_try.empty:
                return df_try, cand, tried
            else:
                tried[cand] = 'empty'
        except Exception as ex:
            tried[cand] = str(ex)

    return None, None, tried

try:
    df, used_ticker, tried_info = fetch_with_suggestions(user_input, start, end)
    if df is None or df.empty:
        tried_keys = list(tried_info.keys())
        msg = f"Could not retrieve data for '{user_input}'. Tried: {', '.join(tried_keys)}."
        empties = [k for k, v in tried_info.items() if v == 'empty']
        if empties:
            msg += f" Possible tickers returned no data: {', '.join(empties)}."
        msg += "\nIf your ticker already includes a suffix (like '.NS'), try the base symbol without extra suffixes, or verify the symbol on Yahoo Finance."
        st.error(msg)
    else:
        if used_ticker and used_ticker != user_input:
            st.info(f"Using ticker '{used_ticker}' (matched alternative for '{user_input}').")

        #Describing Data
        st.subheader('Data from 2010 - 2026')
        st.write(df.describe())

        #Visualizations
        st.subheader('Closing Price vs Time chart')
        fig = plt.figure(figsize=(12, 6))
        plt.plot(df.Close)
        st.pyplot(fig)
except Exception as e:
    st.error(f"Error retrieving data: {str(e)}")