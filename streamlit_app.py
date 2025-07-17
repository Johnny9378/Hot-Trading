
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="BTC/USD Signal Dashboard", layout="centered")

st.title("📊 BTC/USD - Dashboard Mobile Friendly")
st.markdown("Segnali generati con **RSI (14)** + **Medie Mobili (SMA10/SMA30)**")
st.caption("Versione ottimizzata per dispositivi mobili con alert sonori")

try:
    data = yf.download("BTC-USD", interval="15m", period="1d")
    data.dropna(inplace=True)

    if len(data) < 50:
        st.error("Dati insufficienti per elaborare il segnale. Riprova tra qualche minuto.")
    else:
        data['SMA10'] = data['Close'].rolling(window=10).mean()
        data['SMA30'] = data['Close'].rolling(window=30).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        def get_signal(row):
            if row['RSI'] < 30 and row['SMA10'] > row['SMA30']:
                return "🟢 BUY"
            elif row['RSI'] > 70 and row['SMA10'] < row['SMA30']:
                return "🔴 SELL"
            else:
                return "⚪ WAIT"

        data['Signal'] = data.apply(get_signal, axis=1)
        last_signal = data['Signal'].iloc[-1]
        last_price = data['Close'].iloc[-1]

        st.metric(label="Prezzo BTC/USD", value=f"${last_price:,.2f}")
        st.metric(label="Segnale Corrente", value=last_signal)

        st.subheader("📈 Prezzo con SMA")
        st.line_chart(data[['Close', 'SMA10', 'SMA30']])

        st.subheader("📉 RSI")
        st.line_chart(data['RSI'])

        if last_signal != "⚪ WAIT":
            sound_html = '''
                <audio autoplay>
                    <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
                </audio>
            '''
            st.markdown(sound_html, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Errore nel caricamento dei dati: {e}")
