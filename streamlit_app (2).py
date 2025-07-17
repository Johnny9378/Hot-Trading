
import streamlit as st
import yfinance as yf
import pandas as pd

# --- Titolo ---
st.set_page_config(page_title="Hot Trading", layout="wide")
st.title("🔥 Hot Trading - Segnali tecnici su Crypto & Forex")

# --- Selezione Asset ---
asset = st.selectbox("Scegli un asset", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X", "USDJPY=X"])

# --- Intervallo temporale ---
period = st.selectbox("Intervallo", ["7d", "1mo", "3mo", "6mo", "1y"], index=1)

# --- Scarica dati ---
try:
    data = yf.download(asset, period=period, interval="1h")
    if data.empty:
        st.error("⚠️ Nessun dato trovato per questo asset.")
        st.stop()
except Exception as e:
    st.error(f"Errore nel caricamento dei dati: {e}")
    st.stop()

# --- Indicatori ---
data["SMA10"] = data["Close"].rolling(10).mean()
data["SMA30"] = data["Close"].rolling(30).mean()

# RSI
delta = data["Close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
data["RSI"] = 100 - (100 / (1 + rs))

# --- Genera Segnale ---
def get_signal(row):
    if (row["RSI"] < 30) & (row["SMA10"] > row["SMA30"]):
        return "🟢 BUY"
    elif (row["RSI"] > 70) & (row["SMA10"] < row["SMA30"]):
        return "🔴 SELL"
    else:
        return "⚪ WAIT"

data["Signal"] = data.apply(get_signal, axis=1)

# --- Visualizza ---
st.subheader(f"📊 Dati per {asset}")
st.line_chart(data[["Close", "SMA10", "SMA30"]].dropna())

st.subheader("📈 Ultimi segnali")
st.dataframe(data[["Close", "RSI", "SMA10", "SMA30", "Signal"]].dropna().tail(10))

# --- Alert sonoro (simbolico) ---
last_signal = data["Signal"].dropna().iloc[-1]
if last_signal == "🟢 BUY":
    st.success("Segnale di acquisto!")
elif last_signal == "🔴 SELL":
    st.error("Segnale di vendita!")
else:
    st.info("Nessun segnale attivo.")
