
import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Treasury Scenario Simulator", layout="centered")
st.title("💰 Treasury Scenario Simulator")

st.markdown("Simulate liquidity and FX impact based on stress parameters.")

# --- Inputs ---
st.sidebar.header("📊 Scenario Parameters")
fx_shock = st.sidebar.slider("FX Rate Shock (%)", -20, 20, 0)
payment_delay = st.sidebar.slider("Payment Delay (Days)", 0, 90, 0)
interest_rate = st.sidebar.slider("Interest Rate (%)", 0.0, 25.0, 5.0)

base_fx = st.sidebar.number_input("Base FX Rate (e.g. USD/TRY)", value=32.00)
today = datetime.date.today()

# --- Dummy forecast logic ---
weeks = pd.date_range(today, periods=13, freq='W')
base_cashflow = np.linspace(10_000_000, 1_000_000, 13)  # dummy decreasing cash

adjusted_cashflow = base_cashflow * (1 - fx_shock / 100)
adjusted_cashflow = np.roll(adjusted_cashflow, payment_delay // 7)

df = pd.DataFrame({
    "Week": weeks,
    "Projected Cashflow (TRY)": adjusted_cashflow.astype(int)
})

# --- Outputs ---
st.subheader("📈 Projected 13-Week Liquidity Forecast")
st.line_chart(df.set_index("Week"))

st.subheader("🧮 Summary")
liquidity_buffer = adjusted_cashflow.sum()
st.write(f"**Total liquidity buffer:** {liquidity_buffer:,.0f} TRY")

if liquidity_buffer < 5_000_000:
    st.error("⚠️ Risk detected: Liquidity buffer under stress.")
elif fx_shock >= 10:
    st.warning("⚠️ FX exposure elevated. Consider hedging.")
else:
    st.success("✅ Liquidity position is stable under this scenario.")

# Export
st.download_button(
    label="📄 Download Forecast (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="treasury_forecast.csv",
    mime="text/csv"
)
