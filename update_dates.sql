-- Recalculate max datetime using only values from 2006
DROP TEMPORARY TABLE IF EXISTS max_datetime_holder;
CREATE TEMPORARY TABLE max_datetime_holder (max_datetime DATETIME);

-- Get max date from columns where the year is 2006 only
INSERT INTO max_datetime_holder (max_datetime)
SELECT GREATEST(
    IFNULL((SELECT MAX(order_date) FROM orders WHERE YEAR(order_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(shipped_date) FROM orders WHERE YEAR(shipped_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(paid_date) FROM orders WHERE YEAR(paid_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(submitted_date) FROM purchase_orders WHERE YEAR(submitted_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(creation_date) FROM purchase_orders WHERE YEAR(creation_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(expected_date) FROM purchase_orders WHERE YEAR(expected_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(payment_date) FROM purchase_orders WHERE YEAR(payment_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(approved_date) FROM purchase_orders WHERE YEAR(approved_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(transaction_created_date) FROM inventory_transactions WHERE YEAR(transaction_created_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(transaction_modified_date) FROM inventory_transactions WHERE YEAR(transaction_modified_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(invoice_date) FROM invoices WHERE YEAR(invoice_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(due_date) FROM invoices WHERE YEAR(due_date) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(date_allocated) FROM order_details WHERE YEAR(date_allocated) = 2006), '1000-01-01'),
    IFNULL((SELECT MAX(date_received) FROM purchase_order_details WHERE YEAR(date_received) = 2006), '1000-01-01')
);

-- Calculate how many days to shift
SET @diff_days := DATEDIFF(CURDATE(), (SELECT max_datetime FROM max_datetime_holder));

-- Shift only dates from 2006
UPDATE orders SET
    order_date = DATE_ADD(order_date, INTERVAL @diff_days DAY)
    WHERE order_date IS NOT NULL AND YEAR(order_date) = 2006;

UPDATE orders SET
    shipped_date = DATE_ADD(shipped_date, INTERVAL @diff_days DAY)
    WHERE shipped_date IS NOT NULL AND YEAR(shipped_date) = 2006;

UPDATE orders SET
    paid_date = DATE_ADD(paid_date, INTERVAL @diff_days DAY)
    WHERE paid_date IS NOT NULL AND YEAR(paid_date) = 2006;

UPDATE purchase_orders SET
    submitted_date = DATE_ADD(submitted_date, INTERVAL @diff_days DAY)
    WHERE submitted_date IS NOT NULL AND YEAR(submitted_date) = 2006;

UPDATE purchase_orders SET
    creation_date = DATE_ADD(creation_date, INTERVAL @diff_days DAY)
    WHERE creation_date IS NOT NULL AND YEAR(creation_date) = 2006;

UPDATE purchase_orders SET
    expected_date = DATE_ADD(expected_date, INTERVAL @diff_days DAY)
    WHERE expected_date IS NOT NULL AND YEAR(expected_date) = 2006;

UPDATE purchase_orders SET
    payment_date = DATE_ADD(payment_date, INTERVAL @diff_days DAY)
    WHERE payment_date IS NOT NULL AND YEAR(payment_date) = 2006;

UPDATE purchase_orders SET
    approved_date = DATE_ADD(approved_date, INTERVAL @diff_days DAY)
    WHERE approved_date IS NOT NULL AND YEAR(approved_date) = 2006;

UPDATE inventory_transactions SET
    transaction_created_date = DATE_ADD(transaction_created_date, INTERVAL @diff_days DAY)
    WHERE transaction_created_date IS NOT NULL AND YEAR(transaction_created_date) = 2006;

UPDATE inventory_transactions SET
    transaction_modified_date = DATE_ADD(transaction_modified_date, INTERVAL @diff_days DAY)
    WHERE transaction_modified_date IS NOT NULL AND YEAR(transaction_modified_date) = 2006;

UPDATE invoices SET
    invoice_date = DATE_ADD(invoice_date, INTERVAL @diff_days DAY)
    WHERE invoice_date IS NOT NULL AND YEAR(invoice_date) = 2006;

UPDATE invoices SET
    due_date = DATE_ADD(due_date, INTERVAL @diff_days DAY)
    WHERE due_date IS NOT NULL AND YEAR(due_date) = 2006;

UPDATE order_details SET
    date_allocated = DATE_ADD(date_allocated, INTERVAL @diff_days DAY)
    WHERE date_allocated IS NOT NULL AND YEAR(date_allocated) = 2006;

UPDATE purchase_order_details SET
    date_received = DATE_ADD(date_received, INTERVAL @diff_days DAY)
    WHERE date_received IS NOT NULL AND YEAR(date_received) = 2006;
