
import pandas as pd
import numpy as np
from pathlib import Path

rng = np.random.default_rng(42)

output_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

n = 5000

restaurants = [
    "Spice Hub",
    "Burger Point",
    "Pizza Corner",
    "South Kitchen",
    "Healthy Bites",
]

orders = pd.DataFrame({
    "order_id": np.arange(10001, 10001 + n),
    "customer_id": rng.integers(1001, 2201, n),
    "restaurant_name": rng.choice(restaurants, n),
    "city": rng.choice(
        ["Bhopal", "Indore", "Pune", "Bengaluru"], n
    ),
    "order_date": (
        pd.Timestamp("2026-01-01")
        + pd.to_timedelta(rng.integers(0, 273, n), unit="D")
    ),
    "order_value": np.round(rng.uniform(100, 1200, n), 2),
    "order_status": rng.choice(
        ["Delivered", "Cancelled"], n, p=[0.88, 0.12]
    ),
    "prep_time_min": rng.integers(10, 46, n),
    "delivery_distance_km": np.round(
        rng.uniform(0.5, 12, n), 2
    ),
})

orders["delivery_time_min"] = (
    orders["prep_time_min"]
    + orders["delivery_distance_km"] * 4
    + rng.normal(8, 5, n)
).round().clip(10, 120).astype(int)

# Cancelled orders have no completed delivery time
orders.loc[
    orders["order_status"] == "Cancelled",
    "delivery_time_min"
] = np.nan

orders["delay_flag"] = (
    (orders["order_status"] == "Delivered")
    & (orders["delivery_time_min"] > 45)
)

reasons = [
    "Restaurant unavailable",
    "Customer cancelled",
    "Delivery partner unavailable",
    "Payment failure",
]

cancelled = orders["order_status"] == "Cancelled"
orders["cancellation_reason"] = None
orders.loc[cancelled, "cancellation_reason"] = rng.choice(
    reasons, size=cancelled.sum()
)

orders["customer_rating"] = np.nan
delivered = orders["order_status"] == "Delivered"
orders.loc[delivered, "customer_rating"] = rng.integers(
    1, 6, size=delivered.sum()
)

output_file = output_dir / "food_delivery_orders.csv"
orders.to_csv(output_file, index=False)

print("Dataset generated successfully!")
print(f"File: {output_file}")
print(f"Total orders: {len(orders)}")
print(f"Delivered: {(orders['order_status'] == 'Delivered').sum()}")
print(f"Cancelled: {cancelled.sum()}")
print(f"Delayed deliveries: {orders['delay_flag'].sum()}")
print("\nSample data:")
print(orders.head().to_string(index=False))
