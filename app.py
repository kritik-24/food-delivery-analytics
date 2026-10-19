
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "food_delivery_orders.csv"

st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="📦",
    layout="wide",
)

st.title("Food Delivery Analytics")
st.caption("Order performance, cancellation patterns and delivery delays")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["delay_flag"] = (
        df["delay_flag"].astype(str).str.lower().eq("true")
    )
    return df

df = load_data()

cities = ["All"] + sorted(df["city"].dropna().unique().tolist())
selected_city = st.selectbox("Filter by city", cities)

if selected_city != "All":
    df = df[df["city"] == selected_city]

delivered = df[df["order_status"] == "Delivered"]
cancelled = df[df["order_status"] == "Cancelled"]

total = len(df)
cancellation_rate = (
    len(cancelled) / total * 100 if total else 0
)
average_delivery = delivered["delivery_time_min"].mean()
delay_rate = (
    delivered["delay_flag"].mean() * 100 if len(delivered) else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{total:,}")
c2.metric("Cancelled Orders", f"{len(cancelled):,}")
c3.metric("Cancellation Rate", f"{cancellation_rate:.2f}%")
c4.metric(
    "Avg Delivery Time",
    f"{average_delivery:.2f} min" if pd.notna(average_delivery) else "N/A",
)

st.subheader("Cancellation Reasons")
if not cancelled.empty:
    reasons = (
        cancelled.groupby("cancellation_reason")
        .size()
        .reset_index(name="cancelled_orders")
        .sort_values("cancelled_orders", ascending=False)
    )
    st.plotly_chart(
        px.bar(
            reasons,
            x="cancellation_reason",
            y="cancelled_orders",
            title="Orders by Cancellation Reason",
            labels={
                "cancellation_reason": "Reason",
                "cancelled_orders": "Cancelled Orders",
            },
        ),
        use_container_width=True,
    )
else:
    st.info("No cancellations for this filter.")

st.subheader("City Cancellation Performance")
city_data = df.assign(
    is_cancelled=df["order_status"].eq("Cancelled")
).groupby("city").agg(
    total_orders=("order_id", "count"),
    cancelled_orders=("is_cancelled", "sum"),
).reset_index()

city_data["cancellation_rate_pct"] = (
    city_data["cancelled_orders"] / city_data["total_orders"] * 100
)

st.plotly_chart(
    px.bar(
        city_data,
        x="city",
        y="cancellation_rate_pct",
        title="Cancellation Rate by City",
        labels={
            "city": "City",
            "cancellation_rate_pct": "Cancellation Rate (%)",
        },
    ),
    use_container_width=True,
)

st.subheader("Restaurant Delivery Performance")
if not delivered.empty:
    restaurant_data = delivered.groupby("restaurant_name").agg(
        delivered_orders=("order_id", "count"),
        delay_rate_pct=("delay_flag", "mean"),
        avg_delivery_min=("delivery_time_min", "mean"),
    ).reset_index()

    restaurant_data["delay_rate_pct"] *= 100

    st.plotly_chart(
        px.bar(
            restaurant_data.sort_values("delay_rate_pct", ascending=False),
            x="restaurant_name",
            y="delay_rate_pct",
            title="Delay Rate Among Delivered Orders",
            labels={
                "restaurant_name": "Restaurant",
                "delay_rate_pct": "Delay Rate (%)",
            },
        ),
        use_container_width=True,
    )

st.caption(
    "Portfolio project using synthetic data. "
    "Delay rate is calculated among delivered orders."
)
