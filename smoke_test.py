#!/usr/bin/env python3
"""
Smoke test — demuestra que el servicio funciona end-to-end sin Slack real.

Levanta un servidor HTTP local que simula el webhook de Slack, crea una base
de datos SQLite en memoria con datos de prueba, ejecuta ambos jobs y verifica
que los mensajes enviados tienen el formato correcto.

Uso:
    python3 smoke_test.py

Requisitos:
    uv pip install -e ".[dev]"   # o: pip install -e ".[dev]"
"""

import json
import sys
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

from sqlalchemy import create_engine, text

# ── Mock Slack webhook ────────────────────────────────────────────────────────

received: list[str] = []


class SlackMockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        received.append(body["text"])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass  # silenciar logs HTTP


server = HTTPServer(("localhost", 0), SlackMockHandler)  # puerto aleatorio
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()

WEBHOOK = f"http://localhost:{port}"

# ── Base de datos en memoria ──────────────────────────────────────────────────

engine = create_engine("sqlite:///:memory:")
yesterday = date.today() - timedelta(days=1)

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            stock INTEGER NOT NULL, min_stock INTEGER
        )
    """))
    conn.execute(text("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY, buyer_name TEXT NOT NULL,
            product_id INTEGER NOT NULL, quantity INTEGER NOT NULL,
            order_date DATE NOT NULL
        )
    """))
    conn.execute(text("INSERT INTO products VALUES (1,'Widget',2,10),(2,'Gadget',15,5)"))
    conn.execute(text(f"INSERT INTO orders VALUES "
                      f"(1,'Ana',1,3,'{yesterday}'),"
                      f"(2,'Carlos',2,1,'{yesterday}'),"
                      f"(3,'Ana',2,2,'{yesterday}')"))
    conn.commit()

# Parchear create_engine para que los jobs usen nuestra DB en memoria
import slack_notifier.db as db_module
db_module.create_engine = lambda *a, **kw: engine  # type: ignore

# ── Ejecutar jobs ─────────────────────────────────────────────────────────────

from slack_notifier.jobs import daily_summary_job, stock_alert_job

DB = "sqlite:///:memory:"

print("=" * 60)
print("SMOKE TEST — Slack Stock Notifier")
print("=" * 60)

print("\n[1/2] daily_summary_job")
daily_summary_job(DB, WEBHOOK)

print("[2/2] stock_alert_job")
stock_alert_job(DB, WEBHOOK)

# ── Verificar resultados ──────────────────────────────────────────────────────

assert len(received) == 2, f"Se esperaban 2 mensajes, se recibieron {len(received)}"

summary, alert = received

date_str = yesterday.strftime("%d/%m/%Y")
assert "📊" in summary,          "FAIL: falta emoji en resumen"
assert date_str in summary,      "FAIL: falta fecha en resumen"
assert "Ana" in summary,         "FAIL: falta comprador Ana"
assert "Carlos" in summary,      "FAIL: falta comprador Carlos"
assert "Widget x3" in summary,   "FAIL: cantidad incorrecta de Widget"
assert "Gadget x2" in summary,   "FAIL: cantidad incorrecta de Gadget"
assert "Total: 6 unidades" in summary, "FAIL: total incorrecto"

assert "⚠️" in alert,            "FAIL: falta emoji en alerta"
assert "Widget" in alert,        "FAIL: falta Widget en alerta"
assert "2 unidades" in alert,    "FAIL: stock incorrecto en alerta"
assert "mínimo: 10" in alert,    "FAIL: umbral incorrecto en alerta"
assert "Gadget" not in alert,    "FAIL: Gadget no debería aparecer en alerta"

# ── Output ────────────────────────────────────────────────────────────────────

print("\n── Mensaje 1: Resumen diario ──────────────────────────────")
print(summary)
print("\n── Mensaje 2: Alerta de stock ─────────────────────────────")
print(alert)
print("\n" + "=" * 60)
print("✅  SMOKE TEST PASSED — 2/2 mensajes verificados")
print("=" * 60)

server.shutdown()
sys.exit(0)
