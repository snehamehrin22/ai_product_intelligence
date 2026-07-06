# AI Todo App - Access Requirements Checklist

## Phase-by-Phase Access Needs

---

## **Phase 1: Core App (Week 1)**
*Goal: Working todo app with Lakebase*

### ✅ Required Access

#### 1. **Databricks Workspace**
- [ ] **Databricks account** (Azure Databricks or AWS Databricks)
  - Free trial available: https://www.databricks.com/try-databricks
  - Or Azure Databricks through Azure portal
- [ ] **Unity Catalog enabled** on your workspace
  - Required for: Schema/table management, governance
  - Setup: Can be enabled during workspace creation or afterward
- [ ] **SQL Warehouse** (serverless recommended)
  - Required for: Running SQL queries from FastAPI
  - Cost: ~$0.22/DBU (serverless auto-scales)
- [ ] **Personal Access Token** (PAT)
  - Required for: Backend to connect to Databricks
  - Generate: User Settings → Developer → Access Tokens

#### 2. **Python Environment**
- [ ] **Python 3.11+** installed locally
- [ ] **pip** for package management
- No special access needed - local development

#### 3. **Node.js Environment**
- [ ] **Node.js 18+** and **npm** installed
- No special access needed - local development

#### 4. **LLM API Access (for AI agent)**
- [ ] **OpenAI API key** OR **Anthropic API key**
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com/
  - Cost estimate: ~$5-10 for testing (use gpt-4o-mini)

**Estimated Phase 1 Cost: $0-20 (if using free trials)**

---

## **Phase 2: Event Instrumentation (Week 2)**
*Goal: Stream events from app to Kafka*

### ✅ Required Access

#### 5. **Azure Event Hubs** (Managed Kafka)
- [ ] **Azure subscription**
  - Free tier available: https://azure.microsoft.com/free/
  - $200 free credits for 30 days
- [ ] **Event Hubs Namespace** created
  - Region: Choose closest to you (e.g., East US, West Europe)
  - Pricing tier: Standard (supports Kafka protocol)
  - Cost: ~$11/month base + $0.028/million events
- [ ] **Event Hubs topics created:**
  - `platform_events` (for UI interactions)
  - `agent_traces` (for LLM telemetry)
- [ ] **Connection string** (from Event Hubs → Shared access policies)
  - Required for: Backend to publish events

#### 6. **Langfuse** (Agent Observability - Optional)
- [ ] **Langfuse Cloud account** (free tier)
  - Sign up: https://cloud.langfuse.com/
  - Or self-host: https://langfuse.com/docs/deployment/self-host
  - Required for: Real-time agent trace visualization
  - Cost: Free tier includes 50k traces/month

**Estimated Phase 2 Cost: $10-30/month (Azure Event Hubs)**

---

## **Phase 3: Streaming Ingestion (Week 3)**
*Goal: Event Hubs → Databricks Bronze tables*

### ✅ Required Access

#### 7. **Databricks Compute**
- [ ] **All-purpose cluster** OR **Job cluster**
  - Required for: Running Auto Loader notebooks
  - Recommended: Job clusters (cheaper, auto-terminate)
  - Size: Single node or 2-node cluster (small workload)
  - Cost: ~$0.20/DBU, ~10 DBUs/hour for small cluster = $2/hour
  - Note: Only runs when processing data

#### 8. **Azure Event Hubs Connection from Databricks**
- [ ] **Event Hubs connection string** (from Phase 2)
- [ ] **Databricks Secrets** configured
  - Set up: Databricks CLI → `databricks secrets create-scope`
  - Store Event Hubs connection string securely
  - Docs: https://docs.databricks.com/security/secrets/

**Estimated Phase 3 Cost: $10-20 (cluster runtime for testing)**

---

## **Phase 4: dbt Transformations (Week 4)**
*Goal: Bronze → Silver → Gold with dbt*

### ✅ Required Access

#### 9. **dbt Core** (Local Installation)
- [ ] **dbt-databricks adapter** installed
  - Install: `pip install dbt-databricks`
  - Free and open source

#### 10. **Databricks SQL Warehouse** (Already from Phase 1)
- [ ] Ensure SQL Warehouse has access to:
  - `bronze` schema (from Phase 3)
  - `silver` and `gold` schemas (will create)

**Estimated Phase 4 Cost: $5-10 (SQL Warehouse query time)**

---

## **Phase 5: Agent Evaluation (Week 5)**
*Goal: Golden dataset + eval pipelines*

### ✅ Required Access

#### 11. **LangSmith** (Agent Evaluation - Optional)
- [ ] **LangSmith account**
  - Sign up: https://smith.langchain.com/
  - Required for: Structured agent evaluation
  - Cost: Free tier includes 5k traces/month, then $39/month
  - Alternative: Build custom eval harness (no cost)

**Estimated Phase 5 Cost: $0 (use free tier or custom eval)**

---

## **Phase 6: Production Orchestration (Week 6)**
*Goal: Databricks Workflows + alerts*

### ✅ Required Access

#### 12. **Databricks Workflows**
- [ ] Already included in Databricks workspace (no extra cost)
- [ ] **Email/Slack webhook** for alerts
  - Optional: Set up Slack incoming webhook for notifications

#### 13. **Azure AKS** (Optional - for production deployment)
- [ ] **Azure Kubernetes Service** cluster
  - Only needed if deploying backend to cloud
  - Alternative: Run locally or use Azure App Service
  - Cost: ~$70/month for small cluster

**Estimated Phase 6 Cost: $0-100 (depending on deployment choice)**

---

## **Summary: What You Need to Sign Up For**

### **Minimum to Start (Phase 1)**
1. ✅ **Databricks** - Free trial (14 days) or pay-as-you-go
2. ✅ **OpenAI** OR **Anthropic** - API key (~$5-10 for testing)

### **To Complete Full Project (Phases 1-6)**
1. ✅ **Databricks** - Pay-as-you-go ($50-100 total for 6 weeks)
2. ✅ **Azure** - Free trial ($200 credits) for Event Hubs
3. ✅ **OpenAI/Anthropic** - API key ($20-30 for full testing)
4. ✅ **Langfuse** (Optional) - Free tier
5. ✅ **LangSmith** (Optional) - Free tier

---

## **Total Estimated Cost for 6-Week Project**

| Service | Cost |
|---------|------|
| Databricks (compute + SQL Warehouse) | $50-100 |
| Azure Event Hubs | $20-40 |
| LLM API (OpenAI/Anthropic) | $20-30 |
| Langfuse | $0 (free tier) |
| LangSmith | $0 (free tier) |
| **Total** | **$90-170** |

**Note:** This assumes:
- Development/learning usage (not production scale)
- Using free tiers where available
- Shutting down resources when not in use
- Azure free trial credits cover most Azure costs

---

## **Cost Optimization Tips**

1. **Databricks:**
   - Use serverless SQL Warehouse (auto-scales down)
   - Use job clusters instead of all-purpose clusters
   - Set cluster auto-termination to 15 minutes
   - Use spot instances (50-70% cheaper)

2. **Azure Event Hubs:**
   - Use Standard tier (not Premium)
   - Delete topics when not in active use during learning
   - Consider using Azure free credits

3. **LLM APIs:**
   - Use `gpt-4o-mini` or `claude-3-haiku` for testing (10x cheaper)
   - Set rate limits in code
   - Cache common responses

4. **General:**
   - Work in focused sprints (don't leave resources running overnight)
   - Use free tiers for observability tools
   - Can pause project between phases to control costs

---

## **Alternative: Fully Local Development (Phase 1 Only)**

If you want to start with **zero cloud costs**, you can:

1. **Replace Lakebase** with local **SQLite** or **DuckDB**
   - Learn the concepts without Databricks
   - Migrate to Databricks later

2. **Skip Event Hubs** initially
   - Use in-memory queues or local Kafka (Docker)

3. **Use local observability**
   - Print statements instead of Langfuse

**Trade-off:** You won't learn the Databricks/Azure-specific parts, but you'll understand the architectural patterns.

---

## **Recommended Order to Get Access**

### **Week 0 (Setup Week):**
1. Sign up for **Databricks** free trial
2. Get **OpenAI API key** (or Anthropic)
3. Set up **Azure free account** (don't create resources yet)

### **Week 1 (Phase 1):**
4. Create Databricks workspace + Unity Catalog
5. Generate Databricks Personal Access Token
6. Test Databricks SQL Warehouse connection

### **Week 2 (Phase 2):**
7. Create Azure Event Hubs namespace
8. Create platform_events and agent_traces topics
9. Sign up for Langfuse (optional)

### **Week 3-6:**
10. Set up remaining services as needed per phase

---

## **Next Steps**

1. **Decision:** Full cloud stack or start local?
2. **If cloud:** Begin with Databricks + OpenAI signup
3. **If local:** Begin with local SQLite + OpenAI for agent

**Want me to create detailed setup guides for any of these services?**
