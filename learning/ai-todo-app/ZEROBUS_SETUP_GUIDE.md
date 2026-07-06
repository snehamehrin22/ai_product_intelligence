# Databricks Zerobus Ingest Setup Guide (Azure)

**Phase 2: Event Instrumentation**

This guide walks you through configuring Databricks Zerobus Ingest for the AI Todo App on **Azure Databricks**.

## Overview

Zerobus Ingest is Databricks' serverless event streaming service that writes directly to Delta Lake with sub-5 second latency. No Kafka or Event Hubs needed.

**Critical Requirement:** Zerobus requires Unity Catalog with **managed storage** (Azure ADLS Gen2). Tables created with default workspace storage are NOT supported (Error 4024).

## Prerequisites

- ✅ Azure Databricks workspace with Unity Catalog enabled
- ✅ Azure Storage Account with ADLS Gen2 enabled
  - Container: `databricks-data`
  - Example: `signalogrowthdata.dfs.core.windows.net`
- ✅ Azure Databricks Access Connector resource (for managed identity)
- ✅ Contributor role on Access Connector resource (to create credentials)
- ✅ Admin access to create service principals in Databricks
- ✅ SQL Warehouse running

## Step 1: Extract Workspace Information

### 1.1 Get Workspace ID and Region

From your Databricks workspace URL: `https://adb-<workspace-id>.XX.azuredatabricks.net`

Example:
- URL: `https://adb-7405605390611356.16.azuredatabricks.net/`
- Workspace ID: `7405605390611356`
- Region: (Check your workspace region in Admin Settings)

### 1.2 Construct Zerobus Endpoint

**Azure Format:** `<workspace-id>.zerobus.<region>.azuredatabricks.net`

**Important:** NO `https://` prefix when using the SDK!

Example for East US:
```
7405605390611356.zerobus.eastus.azuredatabricks.net
```

**Common regions:**
- `eastus` - East US
- `eastus2` - East US 2
- `westus` - West US
- `westus2` - West US 2
- `westeurope` - West Europe

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

## Step 3: Create Storage Credential (Azure Managed Identity)

**Why:** Zerobus requires Unity Catalog tables with explicit storage locations. This step creates credentials for Azure ADLS Gen2 access.

### 3.1 Create Access Connector (If Not Exists)

If you don't already have an Azure Databricks Access Connector:

1. Go to **Azure Portal**
2. Create new resource → Search "Azure Databricks Access Connector"
3. Resource Group: Choose existing (e.g., `Analytics`)
4. Name: `databricks-access-connector`
5. Region: Same as your storage account
6. Click **Review + Create**

### 3.2 Grant Yourself Permissions

**Critical:** You need Contributor role on the Access Connector to use it in Databricks.

1. Go to Access Connector resource in Azure Portal
2. **Access control (IAM)** → Add role assignment
3. Role: **Contributor**
4. Assign access to: **User, group, or service principal**
5. Select yourself
6. Click **Review + assign**

### 3.3 Get Access Connector Resource ID

In Azure Portal, go to Access Connector → **Properties** → Copy **Resource ID**

Format:
```
/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Databricks/accessConnectors/<name>
```

Example:
```
/subscriptions/84e5732e-6218-4d5d-97a8-adf4ad14e6d8/resourceGroups/Analytics/providers/Microsoft.Databricks/accessConnectors/databricks-access-connector
```

### 3.4 Create Storage Credential in Databricks (UI Method - Easiest)

**This is the recommended approach that worked successfully.**

1. In Databricks workspace, click **Catalog** (left sidebar)
2. Click **External Data** tab at the top
3. Click **Credentials** in left menu
4. Click **Create credential** button
5. Select **Storage Credential**
6. Choose **Azure Managed Identity**
7. Credential name: `azure_storage_credential`
8. **Paste the Access Connector Resource ID** from Step 3.3
9. Click **Create**

### 3.5 Verify Storage Credential

In Databricks SQL Editor:
```sql
DESCRIBE STORAGE CREDENTIAL azure_storage_credential;
```

You should see output showing your credential with managed identity configuration.

### 3.6 Grant Storage Blob Data Contributor Role (Azure)

**Why:** The managed identity needs permission to access your storage account.

1. Go to **Azure Portal** → Storage Account (`signalogrowthdata`)
2. **Access control (IAM)** → Add role assignment
3. Role: **Storage Blob Data Contributor**
4. Assign access to: **Managed identity**
5. Members: Select your Access Connector
6. Click **Review + assign**

## Step 4: Create Catalog and Delta Tables

### 4.1 Run Setup SQL

1. Open Databricks SQL Editor
2. Connect to your SQL Warehouse
3. Open `databricks/setup_zerobus_catalog_tables.sql` from this repo
4. Execute the entire script

This creates:
- **Catalog:** `signaltogrowth_zerobus` with managed storage location
- **Schema:** `bronze` for raw events
- **Tables:**
  - `signaltogrowth_zerobus.bronze.platform_events` - UI interaction events
  - `signaltogrowth_zerobus.bronze.agent_traces` - OpenTelemetry agent traces

### 4.2 Verify Tables Have Managed Storage

**Critical Check:** Ensure tables show explicit ADLS Gen2 storage locations.

```sql
DESCRIBE EXTENDED signaltogrowth_zerobus.bronze.platform_events;
DESCRIBE EXTENDED signaltogrowth_zerobus.bronze.agent_traces;
```

**Look for the `Location` field in the output.** It MUST show an `abfss://` path like:
```
abfss://databricks-data@signalogrowthdata.dfs.core.windows.net/unity-catalog/signaltogrowth_zerobus/bronze/platform_events
```

**If Location is empty or shows `dbfs:/`, Zerobus will fail with Error 4024.** Re-create the catalog with managed storage.

### 4.3 Verify Table Counts

```sql
SELECT COUNT(*) FROM signaltogrowth_zerobus.bronze.platform_events;
SELECT COUNT(*) FROM signaltogrowth_zerobus.bronze.agent_traces;
```

Both should return 0 initially.

## Step 5: Grant Service Principal Permissions

The service principal needs permission to write to Zerobus tables.

Replace `<service-principal-id>` with the Application ID from Step 2.1 (e.g., `46538e1a-e97d-447e-99ef-2685a8492b8f`):

```sql
-- Grant catalog and schema access
GRANT USE CATALOG ON CATALOG signaltogrowth_zerobus TO `<service-principal-id>`;
GRANT USE SCHEMA ON SCHEMA signaltogrowth_zerobus.bronze TO `<service-principal-id>`;

-- Grant table permissions (MODIFY for writes, SELECT for reads)
GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.platform_events TO `<service-principal-id>`;
GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.agent_traces TO `<service-principal-id>`;
```

### Verify Permissions

```sql
SHOW GRANTS ON TABLE signaltogrowth_zerobus.bronze.platform_events;
SHOW GRANTS ON TABLE signaltogrowth_zerobus.bronze.agent_traces;
```

You should see your service principal with `MODIFY` and `SELECT` permissions.

## Step 6: Configure Backend Environment

### 6.1 Update `.env` File

Add the following to `backend/.env`:

```bash
# Databricks Zerobus Ingest Configuration (Azure)
DATABRICKS_ZEROBUS_ENDPOINT=7405605390611356.zerobus.eastus.azuredatabricks.net
DATABRICKS_WORKSPACE_URL=https://adb-7405605390611356.16.azuredatabricks.net
DATABRICKS_CLIENT_ID=46538e1a-e97d-447e-99ef-2685a8492b8f
DATABRICKS_CLIENT_SECRET=dapi...
```

**Replace with your actual values!**

**Important:**
- Endpoint format for Azure: `<workspace-id>.zerobus.<region>.azuredatabricks.net`
- NO `https://` prefix on endpoint
- Workspace URL MUST have `https://` and end in `.net` (not `.ne`)

### 6.2 Install Zerobus SDK

```bash
cd backend
source .venv/bin/activate
pip install databricks-zerobus-ingest-sdk
```

Add to `backend/requirements.txt`:
```
databricks-zerobus-ingest-sdk>=0.1.0
```

## Step 7: Test Connection

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

Zerobus Endpoint: 7405605390611356.zerobus.eastus.azuredatabricks.net
Workspace URL: https://adb-7405605390611356.16.azuredatabricks.net
Client ID: 46538e1a...

✅ Zerobus SDK initialized
✅ Zerobus stream created
✅ Test record ingested (offset: 0)
✅ Stream flushed
✅ Stream closed

================================================================================
✅ Zerobus Connection Test PASSED
================================================================================

Next steps:
  1. Verify event in Databricks SQL Editor:
     SELECT * FROM signaltogrowth_zerobus.bronze.platform_events
     WHERE event_id = '<event-id>'
  2. Note: Zerobus has ~5 second latency, so wait a bit before querying
  3. Proceed with implementing ZerobusPublisher service (US-2.2)
```

### Verify Test Event in Databricks

Wait ~5 seconds (Zerobus latency), then run in SQL Editor:

```sql
SELECT * FROM signaltogrowth_zerobus.bronze.platform_events
WHERE event_name = 'test_connection'
ORDER BY timestamp DESC
LIMIT 10;
```

You should see your test event with properties containing `"source": "test_zerobus_connection.py"`!

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

### ❌ Error 4024: "Unsupported table kind. Tables created in default storage are not supported"

**This is the most common error!**

**Root Cause:** Your catalog/tables don't have explicit ADLS Gen2 storage locations. Zerobus requires managed storage.

**How to verify:**
```sql
DESCRIBE EXTENDED signaltogrowth_zerobus.bronze.platform_events;
```

**Look at the `Location` field:**
- ❌ **Empty or `dbfs:/`** → Default storage, Zerobus won't work
- ✅ **`abfss://...`** → Managed storage, Zerobus will work

**Fix:**
1. Verify storage credential exists: `DESCRIBE STORAGE CREDENTIAL azure_storage_credential;`
2. Re-run `databricks/setup_zerobus_catalog_tables.sql` to create catalog with `MANAGED LOCATION`
3. Verify Location field shows `abfss://` path
4. Re-grant permissions to service principal

### ❌ "Failed to create Zerobus stream" (Other Causes)

1. **Service principal lacks permissions**
   - Run the GRANT statements from Step 5
   - Verify: `SHOW GRANTS ON TABLE signaltogrowth_zerobus.bronze.platform_events;`

2. **Table doesn't exist**
   - Run `databricks/setup_zerobus_catalog_tables.sql`
   - Verify: `SELECT * FROM signaltogrowth_zerobus.bronze.platform_events LIMIT 1;`

3. **Zerobus not enabled in workspace**
   - Go to Admin Settings → Lakeflow Connect → Enable Zerobus Ingest

4. **Wrong endpoint format for Azure**
   - ✅ Correct: `<workspace-id>.zerobus.<region>.azuredatabricks.net`
   - ❌ Wrong: `<workspace-id>.zerobus.<region>.cloud.databricks.com` (AWS format)
   - NO `https://` prefix!

5. **Workspace URL truncated in .env**
   - Must end in `.net`, not `.ne`
   - Example: `https://adb-7405605390611356.16.azuredatabricks.net`

### ❌ 401 Unauthorized (OAuth error)

**Causes:**
1. Service principal OAuth secret expired or incorrect
2. Whitespace/newlines in CLIENT_SECRET in .env file
3. Wrong CLIENT_ID

**Fix:**
1. Regenerate OAuth secret in Databricks
2. Copy secret carefully (no extra spaces)
3. Verify CLIENT_ID matches service principal Application ID

### ❌ "Table not found" in verification query

**Fix:** Wait 5-10 seconds after ingestion (Zerobus has ~5 second latency)

## Next Steps

Once the test passes:

1. ✅ **Zerobus configuration complete**
2. → **Implement `ZerobusPublisher` service** (US-2.2)
3. → **Define platform event schemas** (US-2.3)
4. → **Emit events from backend API** (US-2.4)
5. → **Continue with frontend instrumentation** (US-2.5+)

## Key Learnings from Setup

### What We Discovered

1. **Zerobus requires managed storage** - Error 4024 occurs when tables use default workspace storage
2. **UI credential creation is easiest** - Databricks Catalog UI is simpler than SQL for creating storage credentials
3. **Access Connector needs Contributor role** - You must grant yourself permissions on the Access Connector in Azure
4. **Azure vs AWS endpoint formats differ**:
   - Azure: `<workspace-id>.zerobus.<region>.azuredatabricks.net`
   - AWS: `<workspace-id>.zerobus.<region>.cloud.databricks.com`
5. **Storage credential comes BEFORE catalog** - Must create credential first, then catalog with MANAGED LOCATION

### Architecture Summary

```
Azure ADLS Gen2 Storage Account
        ↓ (authenticated via)
Azure Databricks Access Connector (Managed Identity)
        ↓ (permissions granted to)
Databricks Storage Credential
        ↓ (used by)
Unity Catalog with MANAGED LOCATION
        ↓ (contains)
Delta Tables with abfss:// paths
        ↓ (writable by)
Zerobus Ingest SDK
```

## Resources

### Official Documentation
- [Azure Zerobus Docs](https://learn.microsoft.com/en-us/azure/databricks/ingestion/zerobus-overview)
- [Unity Catalog Managed Storage](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/create-catalogs)
- [Azure Databricks Access Connector](https://learn.microsoft.com/en-us/azure/databricks/administration-guide/cloud-configurations/azure/access-connector)
- [Python SDK Repo](https://github.com/databricks/zerobus-sdk-py)

### Key Concepts
- **Error 4024:** "Tables created in default storage are not supported" - Most common Zerobus error
- **Managed Storage:** Unity Catalog with explicit ADLS Gen2 location (required for Zerobus)
- **Access Connector:** Azure resource that provides managed identity for Databricks → Storage authentication

---

**Ready to proceed?** Follow this guide step-by-step, then run the test script. Come back here if you hit issues.
