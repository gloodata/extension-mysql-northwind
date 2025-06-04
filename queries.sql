-- List of categories
-- name: category_enum
-- This query is used to retrieve the list of product categories to use them as filters
SELECT distinct category as "key", category as "label"
FROM products

-- List of job titles 
-- name: job_title_enum
-- This query is used to retrieve the list of job titles to use them as filters
SELECT distinct job_title as "key", job_title as "label"
FROM employees

-- 1. Revenue analysis by product category with time filtering
-- name: revenue_by_category
-- This query shows total revenue and order count by product category, with date filtering
SELECT 
  p.category,
  SUM(od.quantity * od.unit_price * (1 - od.discount)) as total_revenue,
  COUNT(DISTINCT o.id) as total_orders,
  COUNT(DISTINCT o.customer_id) as unique_customers,
  ROUND(AVG(od.quantity * od.unit_price * (1 - od.discount)), 2) as avg_order_value
FROM order_details od
JOIN orders o ON od.order_id = o.id
JOIN products p ON od.product_id = p.id
JOIN customers c ON c.id = o.customer_id
WHERE (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
  AND (:category = '' OR p.category = :category)
GROUP BY p.category;

-- 2. Revenue analysis by product category by month with time filtering
-- name: revenue_by_category_by_month
-- This query shows total revenue and order count by product category by month, with date filtering
SELECT 
	DATE_FORMAT(o.order_date, '%%Y-%%m') AS date,
  p.category,
  SUM(od.quantity * od.unit_price * (1 - od.discount)) as total_revenue,
  COUNT(DISTINCT o.id) as total_orders,
  COUNT(DISTINCT o.customer_id) as unique_customers,
  ROUND(AVG(od.quantity * od.unit_price * (1 - od.discount)), 2) as avg_order_value
FROM order_details od
JOIN orders o ON od.order_id = o.id
JOIN products p ON od.product_id = p.id
JOIN customers c ON c.id = o.customer_id
WHERE (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
  AND (:category = '' OR p.category = :category)
GROUP BY date, p.category
ORDER BY date;


-- 3. Top performing employees by sales volume and revenue
-- name: employee_performance
-- This query analyzes employee performance showing total sales, revenue, and customer reach
SELECT 
    CONCAT(e.first_name, ' ', e.last_name) as employee,
    SUM(od.quantity * od.unit_price * (1 - od.discount)) as total_revenue,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(AVG(od.quantity * od.unit_price * (1 - od.discount)), 2) as avg_order_value
FROM employees e
JOIN orders o ON e.id = o.employee_id
JOIN order_details od ON o.id = od.order_id
WHERE (:job_title = '' OR e.job_title = :job_title)
  AND (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
GROUP BY e.id, e.first_name, e.last_name;

-- 4. Top performing employees by sales volume and revenue by month
-- name: employee_performance_by_month
-- This query analyzes employee performance showing total sales, revenue, and customer reach by month
SELECT 
	DATE_FORMAT(o.order_date, '%%Y-%%m') AS date,
  CONCAT(e.first_name, ' ', e.last_name) as employee,
  SUM(od.quantity * od.unit_price * (1 - od.discount)) as total_revenue,
  COUNT(DISTINCT o.id) as total_orders,
  COUNT(DISTINCT o.customer_id) as unique_customers,
  ROUND(AVG(od.quantity * od.unit_price * (1 - od.discount)), 2) as avg_order_value
FROM employees e
JOIN orders o ON e.id = o.employee_id
JOIN order_details od ON o.id = od.order_id
WHERE (:job_title = '' OR e.job_title = :job_title)
  AND (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
GROUP BY date, e.id, e.first_name, e.last_name;

-- 5. Customer analysis by country and region
-- name: customer_geography_analysis
-- This query analyzes customer distribution and purchasing behavior by geographic location
SELECT 
    c.state_province,
    SUM(od.quantity * od.unit_price * (1 - od.discount)) as total_revenue,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT c.id) as unique_customers,
    AVG(od.quantity * od.unit_price * (1 - od.discount)) as avg_order_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN order_details od ON o.id = od.order_id
GROUP BY c.state_province;

-- 6. Product performance analysis with inventory insights
-- name: product_performance
-- This query shows product sales performance along with pricing and inventory information
SELECT 
    p.product_name,
    p.category,
    p.list_price,
    p.standard_cost,
    (p.list_price - p.standard_cost) as profit_margin,
    COALESCE(SUM(od.quantity), 0) as total_quantity_sold,
    COALESCE(SUM(od.quantity * od.unit_price * (1 - od.discount)), 0) as total_revenue,
    COALESCE(COUNT(DISTINCT od.order_id), 0) as order_frequency,
    p.discontinued
FROM products p
LEFT JOIN order_details od ON p.id = od.product_id
LEFT JOIN orders o ON od.order_id = o.id
WHERE (:category = '' OR p.category = :category)
  AND (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
GROUP BY p.id, p.product_name, p.category, p.list_price, p.standard_cost, p.discontinued
ORDER BY total_revenue DESC;

-- 7. Shipping analysis by carrier and region
-- name: shipping_analysis
-- This query analyzes shipping performance, costs, and delivery patterns
SELECT 
    s.company as shipper_name,
    o.ship_country_region,
    COUNT(DISTINCT o.id) as total_shipments,
    AVG(o.shipping_fee) as avg_shipping_cost,
    SUM(o.shipping_fee) as total_shipping_revenue,
    AVG(DATEDIFF(o.shipped_date, o.order_date)) as avg_delivery_days
FROM orders o
JOIN shippers s ON o.shipper_id = s.id
WHERE o.shipped_date IS NOT NULL
  AND (:shipper = '' OR s.company = :shipper)
  AND (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
GROUP BY s.company, o.ship_country_region
ORDER BY total_shipments DESC;

-- 8. Customer loyalty and repeat purchase analysis
-- name: customer_loyalty_analysis
-- This query identifies customer segments based on purchase frequency and value
SELECT 
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    c.company,
    c.city,
    c.country_region,
    COUNT(DISTINCT o.id) as total_orders,
    SUM(od.quantity * od.unit_price * (1 - od.discount)) as lifetime_value,
    AVG(od.quantity * od.unit_price * (1 - od.discount)) as avg_order_value,
    DATEDIFF(MAX(o.order_date), MIN(o.order_date)) as customer_lifespan_days,
    CASE 
        WHEN COUNT(DISTINCT o.id) >= 5 THEN 'High Frequency'
        WHEN COUNT(DISTINCT o.id) >= 3 THEN 'Medium Frequency'
        WHEN COUNT(DISTINCT o.id) >= 2 THEN 'Low Frequency'
        ELSE 'One-time'
    END as customer_segment
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_details od ON o.id = od.order_id
GROUP BY c.id, c.first_name, c.last_name, c.company, c.city, c.country_region
ORDER BY lifetime_value DESC;

-- 9. Purchase order efficiency analysis
-- name: purchase_order_efficiency
-- This query analyzes purchase order patterns, supplier performance, and inventory management
SELECT 
    s.company as supplier_name,
    COUNT(DISTINCT po.id) as total_purchase_orders,
    SUM(pod.quantity * pod.unit_cost) as total_purchase_value,
    AVG(pod.quantity * pod.unit_cost) as avg_order_value,
    AVG(DATEDIFF(pod.date_received, po.creation_date)) as avg_fulfillment_days,
    COUNT(CASE WHEN pos.status = 'Closed' THEN 1 END) as completed_orders,
    (COUNT(CASE WHEN pos.status = 'Closed' THEN 1 END) * 100.0 / COUNT(DISTINCT po.id)) as completion_rate
FROM suppliers s
JOIN purchase_orders po ON s.id = po.supplier_id
JOIN purchase_order_details pod ON po.id = pod.purchase_order_id
LEFT JOIN purchase_order_status pos ON po.status_id = pos.id
WHERE (:supplier = '' OR s.company = :supplier)
  AND (:start_date = '' OR po.creation_date >= :start_date)
  AND (:end_date = '' OR po.creation_date <= :end_date)
GROUP BY s.id, s.company
ORDER BY total_purchase_value DESC;

-- 10. Inventory transaction analysis
-- name: inventory_movement_analysis
-- This query provides insights into inventory movements and stock management
SELECT 
    p.product_name,
    p.category,
    itt.type_name as transaction_type,
    COUNT(*) as transaction_count,
    SUM(it.quantity) as total_quantity,
    AVG(it.quantity) as avg_quantity_per_transaction,
    MAX(it.transaction_created_date) as last_transaction_date
FROM inventory_transactions it
JOIN products p ON it.product_id = p.id
JOIN inventory_transaction_types itt ON it.transaction_type = itt.id
WHERE (:category = '' OR p.category = :category)
  AND (:transaction_type = '' OR itt.type_name = :transaction_type)
  AND (:start_date = '' OR it.transaction_created_date >= :start_date)
  AND (:end_date = '' OR it.transaction_created_date <= :end_date)
GROUP BY p.id, p.product_name, p.category, itt.id, itt.type_name
ORDER BY total_quantity DESC;

-- 11. Order status and fulfillment analysis
-- name: order_fulfillment_analysis
-- This query analyzes order processing efficiency and status distribution
SELECT 
    os.status_name,
    COUNT(DISTINCT o.id) as order_count,
    SUM(od.quantity * od.unit_price * (1 - od.discount)) as total_value,
    AVG(DATEDIFF(o.shipped_date, o.order_date)) as avg_processing_days,
    COUNT(CASE WHEN o.shipped_date IS NOT NULL THEN 1 END) as shipped_orders,
    (COUNT(CASE WHEN o.shipped_date IS NOT NULL THEN 1 END) * 100.0 / COUNT(DISTINCT o.id)) as fulfillment_rate
FROM orders o
JOIN orders_status os ON o.status_id = os.id
LEFT JOIN order_details od ON o.id = od.order_id
WHERE (:status = '' OR os.status_name = :status)
  AND (:start_date = '' OR o.order_date >= :start_date)
  AND (:end_date = '' OR o.order_date <= :end_date)
GROUP BY os.id, os.status_name
ORDER BY order_count DESC;
