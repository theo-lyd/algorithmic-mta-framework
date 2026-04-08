import streamlit as st

st.set_page_config(page_title="MTA What-If Simulator", layout="wide")
st.title("MTA What-If Simulator")
st.write("Scaffold app: add budget reallocation logic and predictive outputs in Phase VI.")

source = st.selectbox("Move budget from", ["Display", "Paid Social", "Email", "Search"])
target = st.selectbox("Move budget to", ["Search", "Email", "Display", "Paid Social"])
amount = st.slider("Budget reallocation (EUR)", min_value=1000, max_value=50000, step=1000, value=10000)

if st.button("Simulate"):
    st.success(f"Scaffold run: move EUR {amount:,} from {source} to {target}.")
