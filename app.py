# WhiteD666l - Crypto Signal Web App (Streamlit)

import streamlit as st
import pandas as pd
from pycoingecko import CoinGeckoAPI
from ta.momentum import RSIIndicator
from ta.trend import MACD
from datetime import datetime

# Initialize CoinGecko
cg = CoinGeckoAPI()

# --- Fetch all coins ---
all_coins = cg.get_coins_list()
coin_names = sorted([coin['id'] for coin in all_coins])

# --- Sidebar ---
st.set_page_config(page_title="WhiteD666l", layout="wide", initial_sidebar_state="expanded")
st.sidebar.title("⚙️ Settings")
coin = st.sidebar.selectbox("Choose a Coin", coin_names, index=coin_names.index("bitcoin"))
theme = st.sidebar.radio("Theme", ["Dark", "Light"])
invest_amount = st.sidebar.number_input("Your Investment ($)", min_value=1.0, value=10.0, step=1.0)

# --- Styling ---
if theme == "Dark":
    st.markdown("""
        <style>
            body {
                background-color: #111;
                color: #ddd;
            }
            .stApp {
                background-color: #111;
                color: #ddd;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Main ---
st.title(f"📈 WhiteD666l - {coin.upper()} Signal Analysis")

try:
    # --- Fetch Data ---
    data = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days='30')
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # --- Indicators ---
    df['rsi'] = RSIIndicator(close=df['price'], window=14).rsi()
    macd = MACD(close=df['price'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    latest = df.iloc[-1]
    price = latest['price']
    rsi = latest['rsi']
    macd_val = latest['macd']
    macd_signal = latest['macd_signal']

    # --- Signal Logic ---
    if rsi < 30 and macd_val > macd_signal:
        signal = "🟢 STRONG BUY"
    elif rsi > 70 and macd_val < macd_signal:
        signal = "🔴 STRONG SELL"
    else:
        signal = "🟡 NEUTRAL / HOLD"

    # --- Display Output ---
    st.metric("Current Price (USD)", f"${price:,.2f}")
    st.metric("RSI (14)", f"{rsi:.2f}")
    st.metric("MACD", f"{macd_val:.2f}")
    st.metric("Signal Line", f"{macd_signal:.2f}")
    st.subheader("📌 Final Signal:")
    st.success(signal if "BUY" in signal else signal if "NEUTRAL" in signal else signal)

    # --- Investment Advice ---
    st.subheader("💰 Investment Advice")
    if "BUY" in signal:
        entry_price = price
        take_profit = entry_price * 1.05
        stop_loss = entry_price * 0.95
        st.write(f"- **Entry:** ${entry_price:,.2f}")
        st.write(f"- **Target (5% Gain):** ${take_profit:,.2f}")
        st.write(f"- **Stop Loss (5% Risk):** ${stop_loss:,.2f}")
        potential_profit = invest_amount * 0.05
        st.write(f"- **Potential Profit:** ${potential_profit:.2f}")
    else:
        st.info("No safe entry point right now. Please wait.")

    # --- Chart ---
    st.subheader("📉 Price Chart (Last 30 Days)")
    st.line_chart(df.set_index("timestamp")["price"])

except Exception as e:
    st.error("Failed to fetch or process data. Please try another coin or try again later.")
    st.exception(e)

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ for Amal | WhiteD666l.ai")
