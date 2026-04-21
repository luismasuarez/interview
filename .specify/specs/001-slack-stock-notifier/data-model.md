# Data Model: Slack Stock Notifier

## Entities

### Order
Represents a purchase transaction.

| Field | Type | Constraints |
|-------|------|-------------|
| id | integer | primary key |
| buyer_name | string | not null |
| product_id | integer | FK → Product.id |
| quantity | integer | > 0 |
| order_date | date | not null |

### Product
Represents a stocked item.

| Field | Type | Constraints |
|-------|------|-------------|
| id | integer | primary key |
| name | string | not null, unique |
| stock | integer | >= 0 |
| min_stock | integer | nullable — if null, excluded from alerts |

## Relationships

- One Product has many Orders
- One Order belongs to one Product and one Buyer (buyer identified by name string in MVP)

## Queries

### Daily Summary (read-only)
```sql
SELECT buyer_name, p.name AS product_name, SUM(o.quantity) AS total_qty
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE o.order_date = :target_date
GROUP BY buyer_name, p.name
ORDER BY buyer_name, p.name
```

### Stock Alert Check (read-only)
```sql
SELECT name, stock, min_stock
FROM products
WHERE min_stock IS NOT NULL AND stock < min_stock
```

## State Transitions

No state mutations. This system is read-only.
