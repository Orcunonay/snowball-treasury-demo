
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

st.set_page_config(page_title="Treasury Scenario Simulator", layout="centered")
st.title("💰 Treasury Scenario Simulator")

st.markdown("Simulate liquidity and FX risk under multiple stress scenarios.")

# --- Sidebar Parameters ---
st.sidebar.header("📊 Scenario Parameters")
fx_shock = st.sidebar.slider("FX Rate Shock (%)", -20, 20, 0)
payment_delay = st.sidebar.slider("Avg. Payment Delay (Days)", 0, 90, 0)
interest_rate = st.sidebar.slider("Interest Rate (%)", 0.0, 25.0, 5.0)
base_fx = st.sidebar.number_input("Base FX Rate (e.g. USD/TRY)", value=32.00)

today = datetime.date.today()

# --- Generate Dummy Cash Flow Forecast ---
weeks = pd.date_range(today, periods=13, freq='W')
base_cashflow = np.linspace(10_000_000, 1_000_000, 13)  # simple declining cash

# FX impact and delay applied
adjusted_cashflow = base_cashflow * (1 - fx_shock / 100)
adjusted_cashflow = np.roll(adjusted_cashflow, payment_delay // 7)

df = pd.DataFrame({
    "Week": weeks,
    "Base Cashflow": base_cashflow.astype(int),
    "Adjusted Cashflow": adjusted_cashflow.astype(int)
})

# --- Chart: Cash Flow Comparison ---
st.subheader("📈 Forecasted Cashflow (Base vs. Scenario)")
fig = px.line(df, x="Week", y=["Base Cashflow", "Adjusted Cashflow"],
              labels={"value": "Cashflow (TRY)", "Week": "Date"},
              title="13-Week Projected Cash Flow")
st.plotly_chart(fig, use_container_width=True)

# --- FX Exposure Simulation ---
st.subheader("💱 FX Exposure Simulation")
fx_exposure = 5_000_000  # assumed net open FX position
fx_loss = fx_exposure * (fx_shock / 100)
st.write(f"Estimated FX impact: **{fx_loss:,.0f} TRY** on an open position of 5M TRY.")

# --- Liquidity Buffer Summary ---
st.subheader("🧮 Liquidity Summary")
liquidity_buffer = adjusted_cashflow.sum()
st.metric("Total Liquidity Buffer", f"{liquidity_buffer:,.0f} TRY")

if liquidity_buffer < 5_000_000:
    st.error("⚠️ Under liquidity stress. Action recommended.")
elif fx_shock >= 10:
    st.warning("⚠️ FX risk elevated. Consider hedging.")
else:
    st.success("✅ Liquidity position is stable.")

# --- Export Button ---
st.download_button(
    label="📄 Download Scenario Forecast (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="treasury_forecast_scenario.csv",
    mime="text/csv"
)
