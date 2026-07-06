# AI Todo App - Complete Setup Guide (Cloud + OpenAI)

**Stack:** Databricks + Azure Event Hubs + OpenAI + FastAPI + React

---

## Setup Order

Follow this exact order to avoid dependency issues:

1. ✅ Databricks Workspace
2. ✅ Azure Account + Event Hubs (for Phase 2+)
3. ✅ OpenAI API Key
4. ✅ Local Development Environment

---

## 1. Databricks Setup

### Step 1.1: Create Databricks Account

**Option A: Azure Databricks (Recommended for this project)**

1. Go to [Azure Portal](https://portal.azure.com/)
2. Sign up for Azure free account if you don't have one
   - You get $200 free credits for 30 days
   - Credit card required (won't be charged during free period)

3. Create Azure Databricks Workspace:
   ```
   Azure Portal → Create a resource → Search "Databricks"
   → Create → Fill in:

   - Resource group: Create new "ai-todo-app-rg"
   - Workspace name: "ai-todo-app-databricks"
   - Region: Select closest to you (e.g., East US)
   - Pricing tier: Premium (required for Unity Catalog)
   ```

4. Click "Review + Create" → "Create"
   - Deployment takes 2-3 minutes

5. Once deployed, click "Launch Workspace"

**Option B: Databricks Community Edition (Free, Limited)**

1. Go to [Databricks Community Edition](https://community.cloud.databricks.com/login.html)
2. Click "Sign up" → Fill in details
3. Verify email

**⚠️ Limitation:** Community Edition doesn't have Unity Catalog. Use for learning basics only.

---

### Step 1.2: Enable Unity Catalog

**If using Azure Databricks Premium:**

1. In Databricks workspace, click **Catalog** icon (left sidebar)
2. If prompted "Enable Unity Catalog" → Click "Enable"
3. Follow the wizard:
   - Create metastore: `ai_todo_metastore`
   - Link to your workspace
   - Assign yourself as admin

4. Verify Unity Catalog is active:
   ```sql
   -- Run in Databricks SQL Editor
   SHOW CATALOGS;
   ```
   You should see `main` catalog listed.

---

### Step 1.3: Create SQL Warehouse

1. Click **SQL Warehouses** (left sidebar)
2. Click "Create SQL Warehouse"
3. Configure:
   ```
   Name: ai-todo-sql-warehouse
   Cluster size: 2X-Small (cheapest, sufficient for learning)
   Type: Serverless (recommended - auto-scales)
   Auto Stop: 15 minutes (important for cost savings!)
   ```
4. Click "Create"
5. Wait for status to show "Running" (takes 2-3 minutes)

---

### Step 1.4: Create Schemas

1. Click **SQL Editor** (left sidebar)
2. Run these commands:

```sql
-- Use existing catalog
USE CATALOG signaltogrowth;

-- Create schemas for medallion architecture
CREATE SCHEMA IF NOT EXISTS signaltogrowth.bronze;
CREATE SCHEMA IF NOT EXISTS signaltogrowth.silver;
CREATE SCHEMA IF NOT EXISTS signaltogrowth.gold;

-- Create schema for app transactional data (Lakebase)
CREATE SCHEMA IF NOT EXISTS signaltogrowth.todo_app;

-- Verify
SHOW SCHEMAS IN signaltogrowth;
```

---

### Step 1.5: Create Initial Tables

```sql
-- Create tasks table (our "Lakebase" OLTP table)
CREATE TABLE IF NOT EXISTS signaltogrowth.todo_app.tasks (
  task_id STRING NOT NULL,
  user_id STRING NOT NULL,
  title STRING NOT NULL,
  description STRING,
  status STRING NOT NULL DEFAULT 'pending',
  priority STRING DEFAULT 'medium',
  due_date TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT tasks_pk PRIMARY KEY (task_id)
) USING DELTA
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Create users table
CREATE TABLE IF NOT EXISTS signaltogrowth.todo_app.users (
  user_id STRING NOT NULL,
  email STRING NOT NULL,
  name STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT users_pk PRIMARY KEY (user_id),
  CONSTRAINT users_email_unique UNIQUE (email)
) USING DELTA;

-- Insert test user
INSERT INTO signaltogrowth.todo_app.users VALUES (
  'user_test_001',
  'test@example.com',
  'Test User',
  CURRENT_TIMESTAMP()
);

-- Verify
SELECT * FROM signaltogrowth.todo_app.tasks;
SELECT * FROM signaltogrowth.todo_app.users;
```

---

### Step 1.6: Generate Personal Access Token

1. Click your **username** (top right) → **User Settings**
2. Click **Developer** tab
3. Click **Manage** next to "Access tokens"
4. Click **Generate new token**
   ```
   Comment: ai-todo-app-backend
   Lifetime: 90 days (or custom)
   ```
5. Click "Generate"
6. **COPY THE TOKEN** - you won't see it again!
7. Save it temporarily in a secure note

---

### Step 1.7: Get Connection Details

You need these for backend `.env` file:

1. **Databricks Host:**
   - Look at your browser URL: `https://adb-1234567890123456.7.azuredatabricks.net`
   - Copy everything including `https://`

2. **SQL Warehouse HTTP Path:**
   - Go to SQL Warehouses → Click your warehouse
   - Click "Connection Details" tab
   - Copy "HTTP Path" (looks like `/sql/1.0/warehouses/abc123def456`)

3. Save both to a note for later.

---

## 2. Azure Event Hubs Setup

**(Needed for Phase 2 - can skip for Phase 1)**

### Step 2.1: Create Event Hubs Namespace

1. Go to [Azure Portal](https://portal.azure.com/)
2. Search "Event Hubs" → Click "Create"
3. Fill in:
   ```
   Resource group: ai-todo-app-rg (same as Databricks)
   Namespace name: ai-todo-app-events (must be globally unique)
   Location: Same as your Databricks (e.g., East US)
   Pricing tier: Standard (required for Kafka protocol)
   Throughput units: 1 (minimum)
   Enable Auto-Inflate: No (for cost control)
   ```
4. Click "Review + Create" → "Create"
5. Wait for deployment (2-3 minutes)

---

### Step 2.2: Create Event Hubs (Topics)

1. Go to your Event Hubs namespace
2. Click "Event Hubs" (left sidebar under "Entities")
3. Click "+ Event Hub"
4. Create first hub:
   ```
   Name: platform-events
   Partition count: 2
   Retention: 1 day (minimum for learning)
   ```
5. Click "Create"
6. Repeat for second hub:
   ```
   Name: agent-traces
   Partition count: 2
   Retention: 1 day
   ```

---

### Step 2.3: Get Connection String

1. In your Event Hubs namespace, click "Shared access policies" (left sidebar)
2. Click "RootManageSharedAccessKey"
3. Copy "Connection string–primary key"
4. Save it securely (looks like):
   ```
   Endpoint=sb://ai-todo-app-events.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=abc123...
   ```

---

## 3. OpenAI Setup

### Step 3.1: Create OpenAI Account

1. Go to [OpenAI Platform](https://platform.openai.com/signup)
2. Sign up with email or Google
3. Verify your email

---

### Step 3.2: Add Payment Method

1. Go to [Billing Settings](https://platform.openai.com/account/billing/overview)
2. Click "Add payment method"
3. Add credit card
4. Set spending limit (recommended: $20/month for learning)

---

### Step 3.3: Create API Key

1. Go to [API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
   ```
   Name: ai-todo-app-backend
   Permissions: All (default)
   ```
3. Click "Create secret key"
4. **COPY THE KEY** - starts with `sk-proj-...`
5. Save it securely

---

### Step 3.4: Test API Key

Run this in terminal:

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }'
```

Expected response:
```json
{
  "choices": [{"message": {"content": "Hello! How can I..."}}]
}
```

---

## 4. Local Development Environment

### Step 4.1: Install Python

**Required: Python 3.11+**

Check current version:
```bash
python3 --version
```

If you have Python 3.13 (from your global CLAUDE.md):
```bash
/usr/local/bin/python3.13 --version
```

---

### Step 4.2: Install Node.js

**Required: Node.js 18+**

Check current version:
```bash
node --version
npm --version
```

If not installed:
- macOS: `brew install node`
- Windows: Download from [nodejs.org](https://nodejs.org/)

---

### Step 4.3: Install Git

```bash
git --version
```

If not installed:
- macOS: `brew install git`
- Windows: Download from [git-scm.com](https://git-scm.com/)

---

### Step 4.4: Install Docker (Optional - for Phase 2+)

Only needed if running local Kafka instead of Azure Event Hubs.

Download from [docker.com](https://www.docker.com/products/docker-desktop/)

---

## 5. Verify All Access

### Checklist

Run through this checklist to confirm everything is ready:

- [ ] Databricks workspace accessible
- [ ] Unity Catalog enabled with `signaltogrowth` catalog
- [ ] SQL Warehouse running
- [ ] `signaltogrowth.todo_app.tasks` and `signaltogrowth.todo_app.users` tables created
- [ ] Databricks Personal Access Token generated and saved
- [ ] Databricks host URL saved
- [ ] SQL Warehouse HTTP path saved
- [ ] Azure Event Hubs namespace created (Phase 2+)
- [ ] `platform-events` and `agent-traces` hubs created (Phase 2+)
- [ ] Event Hubs connection string saved (Phase 2+)
- [ ] OpenAI API key generated and saved
- [ ] OpenAI API key tested successfully
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Git installed

---

## 6. Create Environment File Template

Save this as a reference for later when we set up the backend:

```bash
# .env template (DO NOT COMMIT TO GIT)

# Databricks
DATABRICKS_HOST=https://adb-xxxxx.azuredatabricks.net
DATABRICKS_TOKEN=dapi1234567890abcdef
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abcdef123456

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Azure Event Hubs (Phase 2+)
EVENT_HUBS_CONNECTION_STRING=Endpoint=sb://xxx.servicebus.windows.net/...

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Next Steps

Once you've completed this setup:

1. ✅ All cloud services are ready
2. ✅ Local environment is prepared
3. ✅ Ready to begin Phase 1 implementation

**Next:** Create project structure and initialize Phase 1 codebase.

---

## Troubleshooting

### Databricks: "Unity Catalog not available"
- **Cause:** Using Standard tier instead of Premium
- **Fix:** Upgrade workspace to Premium tier in Azure Portal

### Databricks: "SQL Warehouse won't start"
- **Cause:** Azure quota limits or billing issue
- **Fix:** Check Azure subscription status and quotas

### OpenAI: "Invalid API key"
- **Cause:** Key not copied correctly or expired
- **Fix:** Regenerate key and copy again carefully

### Event Hubs: "Kafka connection failed"
- **Cause:** Wrong connection string or firewall
- **Fix:** Verify connection string format and check Azure firewall rules

### Azure: "Free credits exhausted"
- **Cause:** Used up $200 free credits
- **Fix:** Switch to pay-as-you-go billing (keep using cost controls)

---

## Cost Monitoring

### Set up Azure Budget Alerts

1. Azure Portal → Cost Management + Billing
2. Click "Budgets" → "Add"
3. Set budget: $50/month
4. Add alert at 80% ($40)
5. Enter your email

### Monitor Databricks Costs

1. Databricks workspace → Account Console
2. Click "Usage" to see DBU consumption
3. Track by:
   - SQL Warehouse queries
   - Cluster runtime
   - Data storage

### Monitor OpenAI Costs

1. [OpenAI Usage Dashboard](https://platform.openai.com/usage)
2. Check daily spend
3. Set hard limit at $20/month in billing settings

---

**Setup complete! Ready to start building?**
