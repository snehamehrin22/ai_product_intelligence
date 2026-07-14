# Troubleshooting Databricks Integration

## Problem: No data in Databricks tables

### Step 1: Verify Kafka has data

```bash
# Check Kafka pod is running
kubectl get pods -l app=kafka

# Check message count in topic
kubectl exec kafka-0 -- kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic agent-traces

# If output is "agent-traces:0:0" then no messages yet
# If output is "agent-traces:0:1" then you have 1 message
```

**If no messages**: Generate test data first:
```bash
curl -X POST "http://20.75.255.1/process" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test: Buy milk", "user_id": "test"}'
```

### Step 2: Verify Kafka is accessible from Databricks

**Option A: Test from Databricks notebook**

1. Create a new Python notebook in Databricks
2. Install kafka-python:
   ```python
   %pip install kafka-python
   ```
3. Copy and paste `test_kafka_connection.py` content
4. Run the test

**Option B: Test from your local machine**

```bash
# Install kafka-python locally
pip install kafka-python

# Run the test script
python databricks/test_kafka_connection.py
```

**Expected output if working**:
```
✅ Consumer created successfully
✅ Topic 'agent-traces' has 1 partition(s): {0}
✅ Successfully read 1 message(s)
✅ ALL TESTS PASSED - Kafka is accessible!
```

**If connection fails**: Check these:
- [ ] Kafka LoadBalancer has external IP: `kubectl get svc kafka-external`
- [ ] Your network allows outbound connections to port 9092
- [ ] No firewall blocking Azure resources
- [ ] Databricks cluster is in same region (lower latency)

### Step 3: Verify streaming notebook is running

Did you actually **start the streaming job** in Databricks?

**To start streaming:**

1. Open `streaming_ingestion_notebook.py` in Databricks
2. Update the configuration:
   ```python
   KAFKA_BROKER = "20.121.166.131:9092"
   KAFKA_TOPIC = "agent-traces"
   ```
3. **Run all cells** in the notebook
4. Look for output like:
   ```
   ✅ Streaming from Kafka to telemetry.agent_traces.raw_traces
   📊 Stream ID: <some-uuid>
   ```

**Check if streaming is active:**

```python
# In Databricks notebook
for stream in spark.streams.active:
    print(f"Stream: {stream.name}")
    print(f"Status: {stream.status}")
    print(f"Last Progress: {stream.lastProgress}")
```

### Step 4: Wait for micro-batch processing

Structured Streaming uses micro-batches. Default is every **10 seconds**.

Wait at least **30 seconds** after starting the stream, then check:

```sql
SELECT COUNT(*) FROM telemetry.agent_traces.raw_traces;
```

### Step 5: Check checkpoint locations

If the checkpoint directory has issues, streaming won't work:

```python
# In Databricks notebook
dbutils.fs.ls("/tmp/checkpoints/")
```

If you see errors, clear checkpoints and restart:

```python
# Delete checkpoints (this will restart from beginning)
dbutils.fs.rm("/tmp/checkpoints/kafka_to_raw", recurse=True)

# Then restart the streaming notebook
```

### Step 6: Check Databricks streaming logs

In the Databricks notebook that's running the stream:

```python
# Get detailed progress info
for stream in spark.streams.active:
    progress = stream.lastProgress
    if progress:
        print(f"Batch ID: {progress['batchId']}")
        print(f"Records processed: {progress['numInputRows']}")
        print(f"Processing time: {progress['durationMs']}")
        print(f"Errors: {progress.get('sources', [{}])[0].get('numInputErrors', 0)}")
```

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Connection refused" | Kafka LoadBalancer not accessible. Check firewall/network. |
| "Topic does not exist" | Kafka auto-create is enabled. Generate a message first. |
| "Stream not found" | You didn't start the streaming notebook. Run all cells. |
| "Checkpoint error" | Clear checkpoints: `dbutils.fs.rm("/tmp/checkpoints/...", True)` |
| "No data after 5 mins" | Check stream is active: `spark.streams.active` |
| "Permission denied" | Check Databricks cluster has access to checkpoint location |

### Quick Debug Checklist

Run this checklist in order:

```bash
# 1. Kafka has messages?
kubectl exec kafka-0 -- kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic agent-traces
# Expected: agent-traces:0:<number>

# 2. Kafka is accessible externally?
curl -v telnet://20.121.166.131:9092
# Expected: Connection successful

# 3. Generate test message
curl -X POST "http://20.75.255.1/process" \
  -H "Content-Type: application/json" \
  -d '{"message": "Debug test", "user_id": "debug"}'
# Expected: 200 OK response

# 4. Check message arrived in Kafka
kubectl exec kafka-0 -- kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic agent-traces
# Expected: offset increased by 1
```

### Still Not Working?

Share the output of these commands:

```python
# In Databricks notebook
print("Active streams:")
print(spark.streams.active)

print("\nStream status:")
for stream in spark.streams.active:
    print(stream.status)
    print(stream.lastProgress)

print("\nTable counts:")
print(spark.sql("SELECT COUNT(*) FROM telemetry.agent_traces.raw_traces").collect())
```

And these bash commands:

```bash
kubectl get pods -l app=kafka
kubectl get svc kafka-external
kubectl logs -l app=otel-collector --tail=50
```

## Next Steps After Troubleshooting

Once you see data in `raw_traces`:

1. **Implement the parser** in the streaming notebook to populate `parsed_traces`
2. **Create the aggregation stream** to populate `agent_metrics_hourly`
3. **Build dashboards** in Databricks SQL
4. **Set up alerts** for anomalies

## Need Help?

Check:
- Kafka logs: `kubectl logs kafka-0`
- Collector logs: `kubectl logs -l app=otel-collector`
- Agent logs: `kubectl logs -l app=agent`
