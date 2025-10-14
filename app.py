import streamlit as st
import pandas as pd
import numpy as np
import finnhub
import time
import plotly.express as px

FINNHUB_API_KEY = "d3mum09r01qmso35hdugd3mum09r01qmso35hdv0"
symbols = ["AAPL", "AMZN", "TSLA", "MSFT", "GOOG"]
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

st.set_page_config(page_title="RL + AHP Stock Dashboard", layout="wide")
st.title("RL + AHP Live Stock Decision Dashboard")

st.sidebar.header("Control Panel")
learning_rate = st.sidebar.slider("Learning Rate", 0.01, 0.5, 0.05, 0.01)
threshold = st.sidebar.slider("Sensitivity Threshold", 0.001, 0.05, 0.01, 0.001)
cycles = st.sidebar.number_input("Update Cycles", min_value=1, max_value=20, value=5)
auto_run = st.sidebar.checkbox("Auto Refresh", value=False)
run_button = st.sidebar.button("Run Once")

weights = np.array([0.4, 0.3, 0.3])
trend_data = []

# -----------------------------
# Functions
# -----------------------------
def get_stock_data():
    rows = []
    for s in symbols:
        try:
            q = finnhub_client.quote(s)
            rows.append({
                "Stock": s,
                "Price": q["c"],
                "PrevClose": q["pc"],
                "ROI": ((q["c"] - q["pc"]) / q["pc"]) * 100,
                "Satisfaction": np.random.uniform(3.5, 5.0)
            })
        except Exception as e:
            st.warning(f"Error fetching {s}: {e}")
    return pd.DataFrame(rows)

def recalc_AHP(df, weights):
    df["ROI_norm"] = df["ROI"] / df["ROI"].max()
    df["Cost_norm"] = 1 - (df["Price"] / df["Price"].max())
    df["Satisfaction_norm"] = df["Satisfaction"] / df["Satisfaction"].max()
    df["AHP_Score"] = (
        weights[0]*df["ROI_norm"] +
        weights[1]*df["Cost_norm"] +
        weights[2]*df["Satisfaction_norm"]
    )
    return df

def update_weights(weights, reward):
    delta = learning_rate * reward
    new_weights = weights + delta * np.random.uniform(-1, 1, size=3)
    new_weights = np.clip(new_weights, 0.05, 0.8)
    new_weights /= new_weights.sum()
    return new_weights

# -----------------------------
# RL + AHP Adaptive Loop
# -----------------------------
if run_button or auto_run:
    for step in range(cycles):
        df_live = get_stock_data()
        df_live = recalc_AHP(df_live, weights)
        avg_before = df_live["AHP_Score"].mean()
        time.sleep(2)
        df_new = get_stock_data()
        df_new = recalc_AHP(df_new, weights)
        avg_after = df_new["AHP_Score"].mean()
        reward = avg_after - avg_before

        if abs(reward) > threshold:
            weights = update_weights(weights, reward)
            status = f"Update Triggered (Δ={reward:.4f})"
        else:
            status = f"Skipped Update (Δ={reward:.4f})"

        trend_data.append({
            "Step": step+1,
            "ROI": weights[0],
            "Cost": weights[1],
            "Satisfaction": weights[2],
            "Reward": reward
        })

        df_ranked = df_new.sort_values("AHP_Score", ascending=False).reset_index(drop=True)
        best_stock = df_ranked.iloc[0]

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"Cycle {step+1} — {status}")
            st.dataframe(df_ranked[["Stock", "Price", "ROI", "Satisfaction", "AHP_Score"]])
        with col2:
            st.metric("ROI Weight", f"{weights[0]:.3f}")
            st.metric("Cost Weight", f"{weights[1]:.3f}")
            st.metric("Satisfaction Weight", f"{weights[2]:.3f}")

        # Dynamic chart updates
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            weight_df = pd.DataFrame({"Criteria": ["ROI", "Cost", "Satisfaction"], "Weight": weights})
            fig_bar = px.bar(weight_df, x="Criteria", y="Weight", title="Current Criteria Weights",
                             color="Criteria", text="Weight", range_y=[0,1])
            st.plotly_chart(fig_bar, use_container_width=True)
        with chart_col2:
            if len(trend_data) > 1:
                trend_df = pd.DataFrame(trend_data)
                fig_line = px.line(trend_df, x="Step", y=["ROI","Cost","Satisfaction"], markers=True,
                                   title="Weight Evolution Over Time")
                st.plotly_chart(fig_line, use_container_width=True)

        # Detailed Recommendation Section
        with st.expander("Best Investment Recommendation (Detailed Analysis)", expanded=True):
            st.markdown(f"""
            **Top Recommended Stock:** {best_stock['Stock']}  
            **AHP Score:** {best_stock['AHP_Score']:.3f}  
            **ROI:** {best_stock['ROI']:.2f}%  
            **Current Price:** ${best_stock['Price']:.2f}  
            **Satisfaction Score:** {best_stock['Satisfaction']:.2f}  
            """)
            
            st.write("### Reason for Selection:")
            reasoning = []
            if best_stock["ROI"] == df_ranked["ROI"].max():
                reasoning.append("Highest return on investment (ROI) compared to others.")
            if best_stock["Price"] == df_ranked["Price"].min():
                reasoning.append("Lowest current cost, offering better value entry point.")
            if best_stock["Satisfaction"] == df_ranked["Satisfaction"].max():
                reasoning.append("Strong user sentiment and market satisfaction.")
            if not reasoning:
                reasoning.append("Balanced trade-off between ROI, cost, and satisfaction.")

            for r in reasoning:
                st.write(f"- {r}")

            st.write("### Rank Summary:")
            df_ranked["Rank"] = df_ranked.index + 1
            st.dataframe(df_ranked[["Rank", "Stock", "ROI", "Price", "Satisfaction", "AHP_Score"]])

        if not auto_run:
            break
        time.sleep(5)

    st.success("RL + AHP Adaptation Complete")
    st.subheader("Adaptation Summary")
    st.dataframe(pd.DataFrame(trend_data))
else:
    st.info("Click 'Run Once' or enable 'Auto Refresh' to start.")
