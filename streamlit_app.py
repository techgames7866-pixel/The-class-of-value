import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Title ---
st.title("🚀 Valuation Lab — Monte Carlo + Benchmarks")

st.write("Run scenarios, export charts/CSV, and get LinkedIn-ready visuals. (Educational tool.)")

# --- Sidebar Inputs ---
st.sidebar.header("Base Inputs")
stock_name = st.sidebar.text_input("Stock Name", "NSDL (demo)")
start_eps = st.sidebar.number_input("Starting EPS (₹)", value=17.16)
buy_price = st.sidebar.number_input("Buy / IPO Price (₹)", value=800.0)
target_pe = st.sidebar.number_input("Target / Base P/E", value=40.0)
inflation = st.sidebar.number_input("Inflation (annual %)", value=5.0) / 100
discount_rate = st.sidebar.number_input("Discount Rate (annual %)", value=10.0) / 100
years_total = st.sidebar.number_input("Simulation Length (Years)", value=20, step=1)
shares_owned = st.sidebar.number_input("Shares Owned", value=18, step=1)
div_payout = st.sidebar.number_input("Dividend Payout % of EPS", value=25.0) / 100
reinvest_div = st.sidebar.radio("Reinvest Dividends?", ["Yes", "No"]) == "Yes"
sip_monthly = st.sidebar.number_input("Monthly SIP Amount (₹)", value=0.0)
mc_sims = st.sidebar.number_input("Monte Carlo Simulations", value=1000, step=100)
mc_seed = st.sidebar.number_input("Random Seed (0 = random)", value=0, step=1)

# --- Growth periods (simplified for now) ---
st.sidebar.subheader("Growth Periods")
mean_growth = st.sidebar.number_input("Mean EPS Growth (%)", value=12.0) / 100
volatility = st.sidebar.number_input("Volatility (std dev %)", value=5.0) / 100

# --- Monte Carlo Simulation ---
rng = np.random.default_rng(None if mc_seed == 0 else mc_seed)
all_final_prices = []
eps_paths = []

for s in range(int(mc_sims)):
    eps = start_eps
    path = [eps]
    for y in range(int(years_total)):
        growth = rng.normal(loc=mean_growth, scale=volatility)
        eps *= (1 + growth)
        path.append(eps)
    eps_paths.append(path)
    all_final_prices.append(path[-1] * target_pe)

all_final_prices = np.array(all_final_prices)
median_final_price = np.median(all_final_prices)
p10, p25, p50, p75, p90 = np.percentile(all_final_prices, [10, 25, 50, 75, 90])

# --- Display Results ---
st.subheader(f"Summary for {stock_name}")
st.metric("Median Projected Price", f"₹ {median_final_price:,.2f}")
st.write(f"10th percentile: ₹ {p10:,.2f} | 90th percentile: ₹ {p90:,.2f}")

# --- Fan Chart ---
st.subheader("Monte Carlo Fan Chart")
years = np.arange(0, years_total + 1)
percentiles = {q: np.percentile([p[y] * target_pe for p in eps_paths], q, axis=0)
               for q in [10, 25, 50, 75, 90]}

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(years, percentiles[50], label="Median", color="black", linewidth=2)
ax.fill_between(years, percentiles[10], percentiles[90], color="blue", alpha=0.1, label="10–90%")
ax.fill_between(years, percentiles[25], percentiles[75], color="blue", alpha=0.2, label="25–75%")
ax.set_xlabel("Year")
ax.set_ylabel("Price (₹)")
ax.legend()
st.pyplot(fig)

# --- Histogram of final prices ---
st.subheader("Distribution of Final Prices")
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.hist(all_final_prices, bins=30, alpha=0.7, color="skyblue", edgecolor="black")
ax2.set_xlabel("Final Price (₹)")
ax2.set_ylabel("Frequency")
st.pyplot(fig2)

# --- Data Export ---
st.subheader("Download Results")
df_out = pd.DataFrame({
    "Year": years,
    "P10": percentiles[10],
    "P25": percentiles[25],
    "Median": percentiles[50],
    "P75": percentiles[75],
    "P90": percentiles[90],
})
st.dataframe(df_out)

st.download_button("Download CSV", df_out.to_csv(index=False), "valuation_results.csv", "text/csv")
