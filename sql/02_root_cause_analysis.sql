
-- 1. Restaurant delivery performance
SELECT
    restaurant_name,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'Delivered'
    ) AS delivered_orders,
    ROUND(
        (
            100.0 * COUNT(*) FILTER (
                WHERE delay_flag = TRUE
            ) / NULLIF(
                COUNT(*) FILTER (
                    WHERE order_status = 'Delivered'
                ), 0
            )
        )::numeric,
        2
    ) AS delay_rate_pct,
    ROUND(
        (
            AVG(delivery_time_min) FILTER (
                WHERE order_status = 'Delivered'
            )
        )::numeric,
        2
    ) AS avg_delivery_time_min
FROM food_delivery_orders
GROUP BY restaurant_name
ORDER BY delay_rate_pct DESC;


-- 2. City-wise cancellation analysis
SELECT
    city,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'Cancelled'
    ) AS cancelled_orders,
    ROUND(
        (
            100.0 * COUNT(*) FILTER (
                WHERE order_status = 'Cancelled'
            ) / NULLIF(COUNT(*), 0)
        )::numeric,
        2
    ) AS cancellation_rate_pct
FROM food_delivery_orders
GROUP BY city
ORDER BY cancellation_rate_pct DESC;


-- 3. Cancellation reason analysis
SELECT
    cancellation_reason,
    COUNT(*) AS cancelled_orders,
    ROUND(
        (
            100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()
        )::numeric,
        2
    ) AS share_of_cancellations_pct
FROM food_delivery_orders
WHERE order_status = 'Cancelled'
GROUP BY cancellation_reason
ORDER BY cancelled_orders DESC;
