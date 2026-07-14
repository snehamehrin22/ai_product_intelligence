# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest Agent Traces from Azure Event Hubs (Kafka)
# MAGIC
# MAGIC This notebook uses Databricks Auto Loader to read OTLP traces from Event Hubs and write to Delta Lake.
# MAGIC
# MAGIC **Architecture:**
# MAGIC ```
# MAGIC Agent (K8s) → OTLP Collector → Event Hubs → Auto Loader → Delta Lake
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Event Hubs configuration (replace with your values)
EVENTHUB_NAMESPACE = "eh-k8s-learning-XXXXX"  # From setup_eventhub.sh output
EVENTHUB_NAME = "agent-traces"
CONNECTION_STRING = "Endpoint=sb://..."  # Get from Azure portal or setup script

# Databricks configuration
CATALOG = "main"
SCHEMA = "observability"
TABLE_NAME = "agent_traces_k8s"
CHECKPOINT_PATH = f"/mnt/checkpoints/{TABLE_NAME}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Schema if Not Exists

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure Event Hubs Kafka Connection

# COMMAND ----------

kafka_bootstrap_servers = f"{EVENTHUB_NAMESPACE}.servicebus.windows.net:9093"
kafka_sasl_config = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{CONNECTION_STRING}";'

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read from Event Hubs (Kafka) using Structured Streaming

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

# Read from Kafka (Event Hubs)
df_raw = (spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
  .option("subscribe", EVENTHUB_NAME)
  .option("kafka.security.protocol", "SASL_SSL")
  .option("kafka.sasl.mechanism", "PLAIN")
  .option("kafka.sasl.jaas.config", kafka_sasl_config)
  .option("startingOffsets", "earliest")  # Or "latest" for new data only
  .option("failOnDataLoss", "false")  # Handles Event Hubs specifics
  .load()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parse OTLP JSON Format

# COMMAND ----------

# OTLP traces are sent as JSON in the Kafka message value
df_parsed = (df_raw
  .select(
    from_json(col("value").cast("string"), "resourceSpans ARRAY<STRUCT<resource:STRUCT<attributes:ARRAY<STRUCT<key:STRING,value:STRUCT<stringValue:STRING>>>>, scopeSpans:ARRAY<STRUCT<spans:ARRAY<STRUCT<traceId:STRING,spanId:STRING,parentSpanId:STRING,name:STRING,kind:INT,startTimeUnixNano:BIGINT,endTimeUnixNano:BIGINT,attributes:ARRAY<STRUCT<key:STRING,value:STRUCT<stringValue:STRING,intValue:BIGINT,doubleValue:DOUBLE>>>,status:STRUCT<code:INT>>>>>>>").alias("otlp"),
    col("timestamp").alias("kafka_timestamp"),
    col("partition"),
    col("offset")
  )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Flatten OTLP Structure to Table Schema

# COMMAND ----------

# Flatten the nested OTLP structure
df_flattened = (df_parsed
  .select(
    explode(col("otlp.resourceSpans")).alias("resourceSpan"),
    col("kafka_timestamp"),
    col("partition"),
    col("offset")
  )
  .select(
    explode(col("resourceSpan.scopeSpans")).alias("scopeSpan"),
    col("resourceSpan.resource.attributes").alias("resource_attributes"),
    col("kafka_timestamp"),
    col("partition"),
    col("offset")
  )
  .select(
    explode(col("scopeSpan.spans")).alias("span"),
    col("resource_attributes"),
    col("kafka_timestamp"),
    col("partition"),
    col("offset")
  )
  .select(
    # Trace identifiers
    col("span.traceId").alias("trace_id"),
    col("span.spanId").alias("span_id"),
    col("span.parentSpanId").alias("parent_span_id"),

    # Span details
    col("span.name").alias("span_name"),
    col("span.kind").alias("span_kind"),

    # Timestamps
    (col("span.startTimeUnixNano") / 1e9).cast("timestamp").alias("start_time"),
    (col("span.endTimeUnixNano") / 1e9).cast("timestamp").alias("end_time"),
    ((col("span.endTimeUnixNano") - col("span.startTimeUnixNano")) / 1e6).alias("duration_ms"),

    # Flatten span attributes (GenAI semantic conventions)
    transform(col("span.attributes"), lambda x: struct(x.key, x.value.stringValue, x.value.intValue, x.value.doubleValue)).alias("attributes"),

    # Resource attributes (service name, etc.)
    transform(col("resource_attributes"), lambda x: struct(x.key, x.value.stringValue)).alias("resource"),

    # Status
    col("span.status.code").alias("status_code"),

    # Kafka metadata
    col("kafka_timestamp"),
    col("partition"),
    col("offset")
  )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract Key Attributes for Easier Querying

# COMMAND ----------

# Helper function to extract attribute value
def get_attribute(attr_array, key):
    return expr(f"filter({attr_array}, x -> x.key = '{key}')[0].stringValue")

# Extract common GenAI attributes
df_final = (df_flattened
  .withColumn("gen_ai_model", get_attribute("attributes", "gen_ai.request.model"))
  .withColumn("gen_ai_input_tokens", expr("filter(attributes, x -> x.key = 'gen_ai.usage.input_tokens')[0].intValue"))
  .withColumn("gen_ai_output_tokens", expr("filter(attributes, x -> x.key = 'gen_ai.usage.output_tokens')[0].intValue"))
  .withColumn("gen_ai_total_tokens", expr("filter(attributes, x -> x.key = 'gen_ai.usage.total_tokens')[0].intValue"))
  .withColumn("session_id", get_attribute("attributes", "session_id"))
  .withColumn("service_name", expr("filter(resource, x -> x.key = 'service.name')[0].stringValue"))
  .withColumn("ingestion_timestamp", current_timestamp())
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Delta Lake

# COMMAND ----------

# Write streaming data to Delta table
query = (df_final
  .writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", CHECKPOINT_PATH)
  .option("mergeSchema", "true")  # Allow schema evolution
  .trigger(processingTime="10 seconds")  # Micro-batch every 10 seconds
  .table(f"{CATALOG}.{SCHEMA}.{TABLE_NAME}")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Monitor Streaming Query

# COMMAND ----------

# Display streaming metrics
display(query)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Query Traces

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   trace_id,
# MAGIC   span_name,
# MAGIC   gen_ai_model,
# MAGIC   gen_ai_total_tokens,
# MAGIC   duration_ms,
# MAGIC   start_time,
# MAGIC   session_id,
# MAGIC   service_name
# MAGIC FROM main.observability.agent_traces_k8s
# MAGIC ORDER BY start_time DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stop Streaming (when done)

# COMMAND ----------

# query.stop()
