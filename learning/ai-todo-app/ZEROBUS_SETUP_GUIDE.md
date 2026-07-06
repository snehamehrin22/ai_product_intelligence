# Databricks Zerobus Ingest Setup Guide

**Phase 2: Event Instrumentation**

This guide walks you through configuring Databricks Zerobus Ingest for the AI Todo App.

## Overview

Zerobus Ingest is Databricks' serverless event streaming service that writes directly to Delta Lake with sub-5 second latency. No Kafka or Event Hubs needed.

**Reference Notebook:** See `ZEROBUS_INGEST_2026-07-06T18_15_42.511Z.ipynb` in Downloads folder

## Prerequisites

- ✅ Databricks workspace (already configured for Phase 1)
- ✅ Admin access to create service principals
- ✅ SQL Warehouse running

## Step 1: Extract Workspace Information

### 1.1 Get Workspace ID and Region

From your Databricks workspace URL: `https://adb-<workspace-id>.XX.azuredatabricks.net`

Example:
- URL: `https://adb-7405605390611356.16.azuredatabricks.net/`
- Workspace ID: `7405605390611356`
- Region: (Check your workspace region in Admin Settings)

### 1.2 Construct Zerobus Endpoint

**Format:** `<workspace-id>.zerobus.<region>.cloud.databricks.com`

**Important:** NO `https://` prefix when using the SDK!

Example:
```
7405605390611356.zerobus.us-west-2.cloud.databricks.com
```

## Step 2: Create Service Principal

Service principals provide OAuth authentication for Zerobus SDK.

### 2.1 Create Service Principal

1. Go to **Settings → Identity & Access → Service Principals**
2. Click **Add Service Principal**
3. Name: `zerobus-ai-todo-app`
4. Click **Add**
5. **Copy the Application ID** (this is your `CLIENT_ID`)

Example Application ID format: `abc12345-6789-abcd-ef01-23456789abcd`

### 2.2 Generate Client Secret

1. Click on the service principal you just created
2. Go to **OAuth secrets** tab
3. Click **Generate secret**
4. **Copy the secret immediately** (you can't see it again!)
5. This is your `CLIENT_SECRET`

## Step 3: Create Delta Tables

### 3.1 Run Setup SQL

1. Open Databricks SQL Editor
2. Connect to your SQL Warehouse
3. Open `databricks/setup_zerobus.sql` from this repo
4. Execute the entire script

This creates:
- `main.events.platform_events` - UI interaction events
- `main.events.agent_traces` - OpenTelemetry agent traces

### 3.2 Verify Tables Created

```sql
DESCRIBE EXTENDED main.events.platform_events;
DESCRIBE EXTENDED main.events.agent_traces;

SELECT COUNT(*) FROM main.events.platform_events;
SELECT COUNT(*) FROM main.events.agent_traces;
```

## Step 4: Grant Service Principal Permissions

Replace `<service-principal-id>` with the Application ID from Step 2.1:

```sql
-- Grant catalog and schema access
GRANT USE CATALOG ON CATALOG main TO `<service-principal-id>`;
GRANT USE SCHEMA ON SCHEMA main.events TO `<service-principal-id>`;

-- Grant table permissions (MODIFY for writes, SELECT for reads)
GRANT MODIFY, SELECT ON TABLE main.events.platform_events TO `<service-principal-id>`;
GRANT MODIFY, SELECT ON TABLE main.events.agent_traces TO `<service-principal-id>`;
```

### Verify Permissions

```sql
SHOW GRANTS ON TABLE main.events.platform_events;
SHOW GRANTS ON TABLE main.events.agent_traces;
```

You should see your service principal with `MODIFY` and `SELECT` permissions.

## Step 5: Configure Backend Environment

### 5.1 Update `.env` File

Add the following to `backend/.env`:

```bash
# Databricks Zerobus Ingest Configuration
DATABRICKS_WORKSPACE_ID=7405605390611356
DATABRICKS_REGION=us-west-2
DATABRICKS_ZEROBUS_ENDPOINT=7405605390611356.zerobus.us-west-2.cloud.databricks.com
DATABRICKS_WORKSPACE_URL=https://adb-7405605390611356.16.azuredatabricks.net
DATABRICKS_CLIENT_ID=abc12345-6789-abcd-ef01-23456789abcd
DATABRICKS_CLIENT_SECRET=dapi...
```

**Replace with your actual values!**

### 5.2 Install Zerobus SDK

```bash
cd backend
source .venv/bin/activate
pip install databricks-zerobus-ingest-sdk
```

Add to `backend/requirements.txt`:
```
databricks-zerobus-ingest-sdk>=0.1.0
```

## Step 6: Test Connection

Run the connection test script:

```bash
cd backend
source .venv/bin/activate
python scripts/test_zerobus_connection.py
```

### Expected Output

```
================================================================================
Testing Databricks Zerobus Ingest Connection
================================================================================

✅ All required environment variables found
✅ Zerobus SDK imported successfully
✅ Zerobus SDK initialized

Zerobus Endpoint: 7405605390611356.zerobus.us-west-2.cloud.databricks.com
Workspace URL: https://adb-7405605390611356.16.azuredatabricks.net
Client ID: abc12345...

✅ Zerobus stream created
✅ Test record ingested (offset: 0)
✅ Stream flushed
✅ Stream closed

================================================================================
✅ Zerobus Connection Test PASSED
================================================================================
```

### Verify Test Event in Databricks

Wait ~5 seconds (Zerobus latency), then run in SQL Editor:

```sql
SELECT * FROM main.events.platform_events
WHERE event_name = 'test_connection'
ORDER BY timestamp DESC
LIMIT 10;
```

You should see your test event!

## Common Issues

### ❌ "Missing required environment variables"

**Fix:** Double-check all variables are in `backend/.env`:
- `DATABRICKS_ZEROBUS_ENDPOINT` (no https://)
- `DATABRICKS_WORKSPACE_URL` (with https://)
- `DATABRICKS_CLIENT_ID`
- `DATABRICKS_CLIENT_SECRET`

### ❌ "Failed to import Zerobus SDK"

**Fix:** Install SDK in venv:
```bash
cd backend
source .venv/bin/activate
pip install databricks-zerobus-ingest-sdk
```

### ❌ "Failed to create Zerobus stream"

**Possible causes:**

1. **Service principal lacks permissions**
   - Run the GRANT statements from Step 4
   - Verify with `SHOW GRANTS`

2. **Table doesn't exist**
   - Run `databricks/setup_zerobus.sql`
   - Verify: `SELECT * FROM main.events.platform_events LIMIT 1;`

3. **Zerobus not enabled in workspace**
   - Go to Admin Settings → Lakeflow Connect
   - Enable Zerobus Ingest

4. **Wrong endpoint format**
   - Should be: `<workspace-id>.zerobus.<region>.cloud.databricks.com`
   - NO `https://` prefix!

### ❌ "Table not found" in verification query

**Fix:** Wait 5-10 seconds after ingestion (Zerobus has ~5 second latency)

## Next Steps

Once the test passes:

1. ✅ Zerobus configuration complete
2. → Implement `ZerobusPublisher` service (US-2.2)
3. → Define platform event schemas (US-2.3)
4. → Emit events from backend API (US-2.4)
5. → Continue with frontend instrumentation (US-2.5+)

## Resources

- [AWS Zerobus Docs](https://docs.databricks.com/aws/en/ingestion/zerobus-overview)
- [Azure Zerobus Docs](https://learn.microsoft.com/en-us/azure/databricks/ingestion/zerobus-overview)
- [Python SDK Repo](https://github.com/databricks/zerobus-sdk-py)
- [Workspace URL Docs](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest#get-your-workspace-url)
- [Zerobus Regions](https://docs.databricks.com/aws/en/ingestion/zerobus-limits#workspace)

---

**Ready to proceed?** Follow this guide step-by-step, then run the test script. Come back here if you hit issues.
