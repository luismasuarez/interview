# Feature Specification: Slack Stock Notifier

**Feature Branch**: `001-slack-stock-notifier`  
**Created**: 2026-04-21  
**Status**: Draft  

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily Purchase Summary (Priority: P1)

Every morning, the manager receives a Slack message with a summary of the previous day's purchases grouped by buyer. The message shows each buyer's name, the products they purchased, and the quantities.

**Why this priority**: This is the core daily reporting need. Without it, the manager has no visibility into purchasing activity.

**Independent Test**: Can be fully tested by triggering the daily job manually and verifying a correctly formatted Slack message arrives in the configured channel.

**Acceptance Scenarios**:

1. **Given** there are purchases recorded for the previous day, **When** the daily summary job runs at the configured time, **Then** a Slack message is sent listing each buyer with their purchased products and quantities.
2. **Given** there are no purchases for the previous day, **When** the daily summary job runs, **Then** a Slack message is sent indicating no purchases were recorded.
3. **Given** the Slack webhook is unreachable, **When** the daily summary job runs, **Then** the failure is logged and the job retries at least once before marking as failed.

---

### User Story 2 - Low Stock Alert (Priority: P2)

When any product's stock falls below its configured minimum threshold, the manager receives an immediate Slack alert identifying the product, its current stock level, and the minimum threshold.

**Why this priority**: Stock alerts are time-sensitive. A delayed alert could result in stockouts. This is the second most critical feature.

**Independent Test**: Can be fully tested by setting a product's stock below its threshold and triggering the stock check job, then verifying the alert arrives in Slack.

**Acceptance Scenarios**:

1. **Given** a product's stock is below its minimum threshold, **When** the stock check job runs, **Then** a Slack alert is sent with the product name, current stock, and minimum threshold.
2. **Given** multiple products are below threshold, **When** the stock check job runs, **Then** a single Slack message lists all affected products.
3. **Given** all products are at or above their thresholds, **When** the stock check job runs, **Then** no alert is sent.
4. **Given** a product was already below threshold in the previous check, **When** the stock check runs again and it is still below threshold, **Then** an alert is sent again (no deduplication in MVP).

---

### User Story 3 - Scheduler Reliability (Priority: P3)

The system runs automatically on a schedule without manual intervention. The manager does not need to trigger reports manually.

**Why this priority**: Automation is the value proposition. Without scheduling, the tool requires manual operation.

**Independent Test**: Can be tested by running the scheduler for a short period with a test schedule (e.g., every minute) and verifying jobs execute and produce output.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** the configured daily summary time is reached, **Then** the summary job executes automatically.
2. **Given** the system is running, **When** the configured stock check interval elapses, **Then** the stock check job executes automatically.
3. **Given** a job fails, **When** the next scheduled execution arrives, **Then** the job runs again normally (failures do not disable future executions).

---

### Edge Cases

- What happens when the data source is unavailable at job execution time? → Log the error, skip the notification, do not crash the scheduler.
- What happens when a buyer has no purchases for the day? → That buyer is omitted from the daily summary.
- What happens when a product has no minimum threshold configured? → That product is excluded from stock alerts.
- What happens when the Slack webhook returns an error? → Log the HTTP status and response body, retry once after 30 seconds.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST send a daily Slack message summarizing purchases grouped by buyer for the previous calendar day.
- **FR-002**: The daily summary MUST include, for each buyer: buyer name, list of products purchased, and quantity per product.
- **FR-003**: The system MUST send a Slack alert when any product's stock falls below its configured minimum threshold.
- **FR-004**: Stock alerts MUST include: product name, current stock quantity, and minimum threshold value.
- **FR-005**: Both the daily summary and stock alerts MUST be delivered to a configurable Slack channel via Incoming Webhook.
- **FR-006**: The daily summary schedule (time of day) MUST be configurable without code changes.
- **FR-007**: The stock check interval MUST be configurable without code changes.
- **FR-008**: Minimum stock thresholds per product MUST be configurable without code changes.
- **FR-009**: All job executions MUST produce a log entry recording: job name, execution time, outcome (success/failure), and any error details.
- **FR-010**: The system MUST retry a failed Slack delivery once before logging the failure as unrecoverable.
- **FR-011**: The system MUST validate its configuration at startup and refuse to start if required values are missing or invalid.

### Key Entities

- **Buyer**: A person who makes purchases. Identified by name or ID. Has one or more orders.
- **Product**: An item that can be purchased and stocked. Has a name, current stock quantity, and an optional minimum stock threshold.
- **Order**: A purchase event linking a buyer to one or more products with quantities, recorded on a specific date.
- **StockThreshold**: The minimum acceptable stock level for a product, below which an alert is triggered.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The daily summary message is delivered to Slack within 60 seconds of the scheduled time, 100% of the time under normal conditions.
- **SC-002**: A stock alert is delivered within one stock-check interval of a product falling below threshold.
- **SC-003**: Zero silent failures — every job execution produces a log entry regardless of outcome.
- **SC-004**: The system starts successfully and rejects invalid configuration with a human-readable error message in under 5 seconds.
- **SC-005**: The manager can identify which products need restocking and which buyers are most active from the Slack messages alone, without accessing any other system.

## Assumptions

- The data source (database) is pre-populated with orders and product stock levels by an external system; this tool only reads data.
- A single Slack channel receives both daily summaries and stock alerts (configurable, but one channel for MVP).
- "Previous day" means the calendar day before the job runs in the system's local timezone.
- Stock levels are updated externally; this system only monitors and reports, it does not modify stock.
- The manager is the sole recipient; no multi-recipient or role-based routing in MVP.
- Internet connectivity to Slack's webhook endpoint is available from the host running this system.
