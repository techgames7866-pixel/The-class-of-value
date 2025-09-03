import streamlit as st
import math

st.title("📈 Stock Valuation & CAGR Calculator")

# Inputs
stock_name = st.text_input("Stock Name", "Example Ltd")
eps = st.number_input("Current EPS", value=10.0, step=0.1)
growth1 = st.number_input("EPS Growth % (first phase)", value=20.0, step=1.0)
years1 = st.number_input("Years for first growth phase", value=10, step=1)
growth2 = st.number_input("EPS Growth % (second phase)", value=10.0, step=1.0)
years2 = st.number_input("Years for second growth phase", value=10, step=1)
pe = st.number_input("Future P/E Ratio", value=40.0, step=1.0)
inflation = st.number_input("Inflation Rate %", value=6.0, step=0.5)
shares = st.number_input("Number of Shares", value=10, step=1)
buy_price = st.number_input("Purchase Price per Share", value=800.0, step=10.0)

# Calculation
eps_future = eps * ((1 + growth1/100) ** years1) * ((1 + growth2/100) ** years2)
future_price = eps_future * pe
total_future_value = future_price * shares

# Inflation adjusted
inflation_factor = (1 + inflation/100) ** (years1 + years2)
real_future_value = total_future_value / inflation_factor

# CAGR
cagr = ((future_price / buy_price) ** (1/(years1+years2)) - 1) * 100

# Output
st.subheader(f"📊 Results for {stock_name}")
st.write(f"Future EPS: **{eps_future:.2f}**")
st.write(f"Future Price: **₹{future_price:.2f}**")
st.write(f"Total Value ({shares} shares): **₹{total_future_value:,.2f}**")
st.write(f"Inflation-adjusted Value: **₹{real_future_value:,.2f}**")
st.write(f"CAGR over {years1+years2} years: **{cagr:.2f}%**")
