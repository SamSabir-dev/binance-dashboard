import streamlit as st
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 🔁 Auto-refresh every 60 seconds
st_autorefresh(interval=60_000, key="refresh")

# Title
st.title("📊 Binance.US Candlestick Dashboard")

# 📁 Handle local vs Drive folder
if os.path.exists("/content/drive/MyDrive/binance_us_data"):
    folder = "/content/drive/MyDrive/binance_us_data"
else:
    folder = "./binance_us_data"

files = sorted([f for f in os.listdir(folder) if f.startswith("binanceus_all_data") and f.endswith(".csv")])

if not files:
    st.warning("No CSV data files found in the folder.")
    st.stop()

file_choice = st.selectbox("Select daily CSV file", files)
df = pd.read_csv(os.path.join(folder, file_choice))

# Get available symbols
symbols = df["symbol"].unique().tolist()

# 📊 Compare Multiple Symbols
selected_symbols = st.multiselect("Select crypto symbols to compare", symbols, default=symbols[:2])
if selected_symbols:
    fig, ax = plt.subplots(figsize=(10, 6))
    for symbol in selected_symbols:
        df_coin = df[df["symbol"] == symbol].copy()
        df_coin["timestamp"] = pd.to_datetime(df_coin["timestamp"])
        df_coin.set_index("timestamp", inplace=True)
        df_close = df_coin["price"].resample("1Min").last()
        ax.plot(df_close.index, df_close, label=symbol)
    ax.set_title("📈 Price Comparison")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    st.pyplot(fig)

# 📈 Single Symbol Candlestick
symbol_choice = st.selectbox("Select crypto symbol for candlestick", symbols)
df_symbol = df[df["symbol"] == symbol_choice].copy()
df_symbol["timestamp"] = pd.to_datetime(df_symbol["timestamp"])
df_symbol.set_index("timestamp", inplace=True)

ohlc = df_symbol[["price"]].resample("1Min").ohlc()
ohlc.columns = ["Open", "High", "Low", "Close"]
ohlc["Volume"] = df_symbol["volume"].resample("1Min").sum()
ohlc.dropna(inplace=True)

st.subheader("📈 Market Summary")
st.write(f"Latest Price: {df_symbol['price'].iloc[-1]:,.2f} USD")
st.write(f"Day High: {df_symbol['high'].max():,.2f}")
st.write(f"Day Low: {df_symbol['low'].min():,.2f}")
st.write(f"Total Volume: {df_symbol['volume'].sum():,.2f}")

st.subheader("🕯️ Candlestick Chart (1-Minute)")
fig, axlist = mpf.plot(ohlc, type='candle', style='charles', volume=True, returnfig=True, figsize=(10,6))
st.pyplot(fig)

if st.checkbox("Show raw data"):
    st.dataframe(df_symbol.reset_index())
