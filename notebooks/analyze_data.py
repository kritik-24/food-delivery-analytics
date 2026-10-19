
import pandas as pd
from pathlib import Path

# Locate and load the dataset
project_dir = Path(__file__).resolve().parent.parent
csv_path = project_dir / "data" / "raw" / "food_delivery_orders.csv"

df = pd.read_csv(csv_path)

# Convert date column to a proper date type
df["order_date"] = pd.to_datetime(df["order_date"])

# 1. Basic dataset checks
print("\n========== DATASET OVERVIEW ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nMissing values:")
print(df.isnull().sum())

# 2. Overall business KPIs
delivered = df[df["order_status"] == "Delivered"]
cancelled = df[df["order_status"] == "Cancelled"]

print("\n========== BUSINESS KPIs ==========")
print("Total orders:", len(df))
print("Delivered orders:", len(delivered))
print("Cancelled orders:", len(cancelled))
print(f"Cancellation rate: {len(cancelled) / len(df) * 100:.2f}%")
print(f"Average delivery time: {delivered['delivery_time_min'].mean():.2f} minutes")
print(f"Delay rate: {delivered['delay_flag'].mean() * 100:.2f}%")

# 3. Restaurant performance
restaurant_report = (
    delivered.groupby("restaurant_name")
    .agg(
        delivered_orders=("order_id", "count"),
        avg_delivery_min=("delivery_time_min", "mean"),
        delayed_orders=("delay_flag", "sum"),
        avg_prep_time_min=("prep_time_min", "mean"),
    )
    .reset_index()
)

restaurant_report["delay_rate_pct"] = (
    restaurant_report["delayed_orders"]
    / restaurant_report["delivered_orders"] * 100
)

restaurant_report = restaurant_report.sort_values(
    "delay_rate_pct", ascending=False
)

print("\n========== RESTAURANT PERFORMANCE ==========")
print(restaurant_report.round(2).to_string(index=False))

# 4. City-level cancellation analysis
city_report = (
    df.assign(is_cancelled=df["order_status"].eq("Cancelled"))
    .groupby("city")
    .agg(
        total_orders=("order_id", "count"),
        cancelled_orders=("is_cancelled", "sum"),
    )
    .reset_index()
)

city_report["cancellation_rate_pct"] = (
    city_report["cancelled_orders"]
    / city_report["total_orders"] * 100
)

city_report = city_report.sort_values(
    "cancellation_rate_pct", ascending=False
)

print("\n========== CITY CANCELLATION ANALYSIS ==========")
print(city_report.round(2).to_string(index=False))

# 5. Cancellation reasons
reason_report = (
    df[df["order_status"] == "Cancelled"]
    .groupby("cancellation_reason")
    .size()
    .reset_index(name="cancelled_orders")
    .sort_values("cancelled_orders", ascending=False)
)

reason_report["share_pct"] = (
    reason_report["cancelled_orders"]
    / len(cancelled) * 100
)

print("\n========== CANCELLATION REASONS ==========")
print(reason_report.round(2).to_string(index=False))

# 6. Save analysis outputs for later Power BI use
output_dir = project_dir / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

restaurant_report.to_csv(
    output_dir / "restaurant_performance.csv", index=False
)
city_report.to_csv(
    output_dir / "city_cancellation_analysis.csv", index=False
)
reason_report.to_csv(
    output_dir / "cancellation_reasons.csv", index=False
)

print("\nAnalysis reports saved in data/processed/")
