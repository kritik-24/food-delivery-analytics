

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project paths
project_dir = Path(__file__).resolve().parent.parent
data_path = project_dir / "data" / "raw" / "food_delivery_orders.csv"
output_dir = project_dir / "reports" / "charts"
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(data_path)
df["order_date"] = pd.to_datetime(df["order_date"])

delivered = df[df["order_status"] == "Delivered"].copy()
cancelled = df[df["order_status"] == "Cancelled"].copy()

# Chart 1: Delay rate by restaurant
restaurant = (
    delivered.groupby("restaurant_name")
    .agg(
        total_delivered=("order_id", "count"),
        delayed_orders=("delay_flag", "sum"),
    )
)

restaurant["delay_rate_pct"] = (
    restaurant["delayed_orders"]
    / restaurant["total_delivered"] * 100
)
restaurant = restaurant.sort_values("delay_rate_pct")

plt.figure(figsize=(10, 6))
restaurant["delay_rate_pct"].plot(kind="barh")
plt.title("Delivery Delay Rate by Restaurant")
plt.xlabel("Delayed deliveries (%)")
plt.ylabel("Restaurant")
plt.tight_layout()
plt.savefig(output_dir / "restaurant_delay_rate.png", dpi=150)
plt.close()

# Chart 2: Cancellation rate by city
city = (
    df.assign(is_cancelled=df["order_status"].eq("Cancelled"))
    .groupby("city")
    .agg(
        total_orders=("order_id", "count"),
        cancelled_orders=("is_cancelled", "sum"),
    )
)

city["cancellation_rate_pct"] = (
    city["cancelled_orders"] / city["total_orders"] * 100
)
city = city.sort_values("cancellation_rate_pct")

plt.figure(figsize=(9, 5))
city["cancellation_rate_pct"].plot(kind="bar")
plt.title("Cancellation Rate by City")
plt.xlabel("City")
plt.ylabel("Cancelled orders (%)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(output_dir / "city_cancellation_rate.png", dpi=150)
plt.close()

# Chart 3: Most common cancellation reasons
reason_counts = cancelled["cancellation_reason"].value_counts()

plt.figure(figsize=(10, 6))
reason_counts.sort_values().plot(kind="barh")
plt.title("Orders by Cancellation Reason")
plt.xlabel("Number of cancelled orders")
plt.ylabel("Cancellation reason")
plt.tight_layout()
plt.savefig(output_dir / "cancellation_reasons.png", dpi=150)
plt.close()

# Chart 4: Monthly order volume
monthly = (
    df.set_index("order_date")
    .resample("MS")["order_id"]
    .count()
)

plt.figure(figsize=(10, 5))
monthly.plot(kind="line", marker="o")
plt.title("Monthly Order Volume")
plt.xlabel("Month")
plt.ylabel("Number of orders")
plt.tight_layout()
plt.savefig(output_dir / "monthly_order_volume.png", dpi=150)
plt.close()

print("Charts generated successfully!")
print(f"Charts saved to: {output_dir}")
print("\nFiles created:")
for chart in sorted(output_dir.glob("*.png")):
    print("-", chart.name)
