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
  COUNT(DISTINCT o.id) as order_count,
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
  COUNT(DISTINCT o.id) as order_count,
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