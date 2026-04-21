from datetime import date
from sqlalchemy import create_engine, text


def get_daily_summary(database_url: str, target_date: date) -> list[dict]:
    """Return purchases grouped by buyer and product for the given date."""
    engine = create_engine(database_url)
    query = text("""
        SELECT o.buyer_name, p.name AS product_name, SUM(o.quantity) AS total_qty
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.order_date = :target_date
        GROUP BY o.buyer_name, p.name
        ORDER BY o.buyer_name, p.name
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"target_date": target_date}).mappings().all()
    return [dict(r) for r in rows]


def get_low_stock_products(database_url: str) -> list[dict]:
    """Return products where stock < min_stock (min_stock must be set)."""
    engine = create_engine(database_url)
    query = text("""
        SELECT name, stock, min_stock
        FROM products
        WHERE min_stock IS NOT NULL AND stock < min_stock
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]
