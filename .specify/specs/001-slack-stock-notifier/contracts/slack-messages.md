# Slack Message Contracts

## Daily Purchase Summary

**Trigger**: Scheduled daily job  
**Channel**: Configured via `SLACK_WEBHOOK_URL`

**Format**:
```
📊 *Resumen de compras del día - DD/MM/YYYY*

• <buyer_name>: <product_name> x<qty>[, <product_name> x<qty>...]
• <buyer_name>: ...

Total: <N> órdenes
```

**Empty day variant**:
```
📊 *Resumen de compras del día - DD/MM/YYYY*

Sin compras registradas para este día.
```

---

## Low Stock Alert

**Trigger**: Periodic stock check job  
**Channel**: Same webhook as summary

**Format**:
```
⚠️ *Alerta de bajo stock*

• <product_name>: <stock> unidades (mínimo: <min_stock>)
• <product_name>: <stock> unidades (mínimo: <min_stock>)
```

**No alert sent** when all products are at or above threshold.

---

## Delivery Contract

- HTTP POST to `SLACK_WEBHOOK_URL`
- Body: `{"text": "<message>"}`
- Content-Type: `application/json`
- Expected response: HTTP 200 with body `ok`
- On non-200: log error, retry once after 30 seconds
