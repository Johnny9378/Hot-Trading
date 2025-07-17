
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Hot Trading", layout="centered")
st.title("📈 Hot Trading - Segnali Tecnici")

# --- Lista ampliata di asset ---
assets = {
    "Bitcoin (BTC/USD)": "BTC-USD",
    "Ethereum (ETH/USD)": "ETH-USD",
    "Solana (SOL/USD)": "SOL-USD",
    "Ripple (XRP/USD)": "XRP-USD",
    "Euro/Dollaro": "EURUSD=X",
    "Sterlina/Dollaro": "GBPUSD=X",
    "Dollaro/Yen": "USDJPY=X",
    "Oro/USD": "GC=F",
    "Argento/USD": "SI=F"
}

asset_label = st.selectbox("Scegli un asset", list(assets.keys()))
asset = assets[asset_label]

period = st.selectbox("Periodo", ["7d", "1mo", "3mo", "6mo", "1y"], index=1)

try:
    data = yf.download(asset, period=period, interval="1h")
    if data.empty:
        st.warning("⚠️ Nessun dato trovato.")
        st.stop()
except Exception as e:
    st.error(f"Errore nel caricamento: {e}")
    st.stop()

data["SMA10"] = data["Close"].rolling(10).mean()
data["SMA30"] = data["Close"].rolling(30).mean()

delta = data["Close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
data["RSI"] = 100 - (100 / (1 + rs))

def get_signal(row):
    if (row["RSI"] < 30) & (row["SMA10"] > row["SMA30"]):
        return "🟢 BUY"
    elif (row["RSI"] > 70) & (row["SMA10"] < row["SMA30"]):
        return "🔴 SELL"
    else:
        return "⚪ WAIT"

data["Signal"] = data.apply(get_signal, axis=1)

st.markdown(f"### 📊 Dati per: `{asset_label}`")
st.line_chart(data[["Close", "SMA10", "SMA30"]].dropna())

st.markdown("### 🧾 Ultimi segnali")
st.dataframe(data[["Close", "RSI", "SMA10", "SMA30", "Signal"]].dropna().tail(10), use_container_width=True)

last_signal = data["Signal"].dropna().iloc[-1]
if last_signal == "🟢 BUY":
    st.success("Segnale di acquisto!")
elif last_signal == "🔴 SELL":
    st.error("Segnale di vendita!")
else:
    st.info("Attendere conferme...")

st.markdown("— _Powered by Yahoo Finance & Streamlit_")
