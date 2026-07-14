# Databricks notebook source
# MAGIC %md
# MAGIC # OpenTelemetry Traces - Kafka to Delta Lake Streaming Ingestion
# MAGIC
# MAGIC This notebook sets up streaming ingestion from Kafka to Delta Lake for OpenTelemetry traces.
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC 1. Kafka broker accessible from Databricks (LoadBalancer IP or VNet peering)
# MAGIC 2. Delta tables created (run `setup_kafka_streaming.sql` first)
# MAGIC 3. Install protobuf library: `%pip install protobuf`
# MAGIC
# MAGIC **Architecture:**
# MAGIC ```
# MAGIC Kafka (agent-traces topic)
# MAGIC   → Structured Streaming
# MAGIC     → Delta Lake (raw_traces - Bronze)
# MAGIC       → Parse OTLP Protobuf
# MAGIC         → Delta Lake (parsed_traces - Silver)
# MAGIC           → Aggregate metrics
# MAGIC             → Delta Lake (agent_metrics_hourly - Gold)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Kafka configuration
KAFKA_BROKER = "20.75.255.1:9092"  # Replace with your Kafka LoadBalancer IP
KAFKA_TOPIC = "agent-traces"

# Delta table locations
CATALOG = "telemetry"
SCHEMA = "agent_traces"
RAW_TABLE = f"{CATALOG}.{SCHEMA}.raw_traces"
PARSED_TABLE = f"{CATALOG}.{SCHEMA}.parsed_traces"
METRICS_TABLE = f"{CATALOG}.{SCHEMA}.agent_metrics_hourly"

# Checkpoint locations (for streaming state management)
RAW_CHECKPOINT = "/tmp/checkpoints/kafka_to_raw"
PARSED_CHECKPOINT = "/tmp/checkpoints/raw_to_parsed"
METRICS_CHECKPOINT = "/tmp/checkpoints/parsed_to_metrics"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Dependencies

# COMMAND ----------

# MAGIC %pip install protobuf==4.25.1

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stream 1: Kafka → Raw Traces (Bronze Layer)

# COMMAND ----------

from pyspark.sql.functions import col, current_timestamp, expr

# Read from Kafka
kafka_df = (spark
  .readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", KAFKA_BROKER)
  .option("subscribe", KAFKA_TOPIC)
  .option("startingOffsets", "earliest")  # Use "latest" for new data only
  .option("maxOffsetsPerTrigger", 1000)   # Rate limiting
  .load()
)

# Add ingestion timestamp
raw_df = kafka_df.select(
  col("key").alias("kafka_key"),
  col("value").alias("kafka_value"),
  col("topic").alias("kafka_topic"),
  col("partition").alias("kafka_partition"),
  col("offset").alias("kafka_offset"),
  col("timestamp").alias("kafka_timestamp"),
  current_timestamp().alias("ingestion_timestamp")
)

# Write to Delta Lake
raw_stream = (raw_df
  .writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", RAW_CHECKPOINT)
  .trigger(processingTime="10 seconds")  # Micro-batch every 10 seconds
  .toTable(RAW_TABLE)
)

print(f"✅ Streaming from Kafka to {RAW_TABLE}")
print(f"📊 Stream ID: {raw_stream.id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stream 2: Raw Traces → Parsed Traces (Silver Layer)

# COMMAND ----------

# MAGIC %md
# MAGIC ### OTLP Protobuf Parser

# COMMAND ----------

from pyspark.sql.functions import udf, col
from pyspark.sql.types import *
import json

# Define schema for parsed trace
parsed_schema = StructType([
    StructField("trace_id", StringType(), True),
    StructField("span_id", StringType(), True),
    StructField("parent_span_id", StringType(), True),
    StructField("span_name", StringType(), True),
    StructField("span_kind", StringType(), True),
    StructField("start_time_unix_nano", LongType(), True),
    StructField("end_time_unix_nano", LongType(), True),
    StructField("duration_ms", DoubleType(), True),
    StructField("service_name", StringType(), True),
    StructField("service_version", StringType(), True),
    StructField("deployment_environment", StringType(), True),
    StructField("gen_ai_request_model", StringType(), True),
    StructField("gen_ai_usage_input_tokens", IntegerType(), True),
    StructField("gen_ai_usage_output_tokens", IntegerType(), True),
    StructField("gen_ai_usage_total_tokens", IntegerType(), True),
    StructField("gen_ai_response_finish_reason", StringType(), True),
    StructField("extraction_priority", StringType(), True),
    StructField("extraction_confidence", DoubleType(), True),
    StructField("extraction_has_due_date", BooleanType(), True),
    StructField("message_length", IntegerType(), True),
    StructField("agent_success", BooleanType(), True),
    StructField("agent_processing_time_ms", DoubleType(), True),
    StructField("attributes", StringType(), True),
    StructField("resource_attributes", StringType(), True)
])

@udf(returnType=ArrayType(parsed_schema))
def parse_otlp_protobuf(binary_data):
    """
    Parse OTLP trace data from Kafka.

    Note: This is a simplified parser. In production, you'd use the official
    opentelemetry-proto package and parse the full protobuf structure.

    For now, we'll return a placeholder that you'll need to implement with
    proper OTLP protobuf parsing.
    """
    try:
        # TODO: Implement full OTLP protobuf parsing
        # For now, return empty array as placeholder
        # You'll need to:
        # 1. Import from opentelemetry.proto.trace.v1 import trace_pb2
        # 2. Parse binary_data as trace_pb2.TracesData()
        # 3. Extract spans and their attributes

        return []
    except Exception as e:
        print(f"Error parsing OTLP data: {e}")
        return []

# COMMAND ----------

# MAGIC %md
# MAGIC ### Simplified JSON-based Parser (Alternative)
# MAGIC
# MAGIC Since OTLP protobuf parsing is complex, let's use a simplified approach by configuring
# MAGIC the OTLP Collector to export as JSON instead of protobuf.

# COMMAND ----------

from pyspark.sql.functions import from_json, explode, col, lit
from pyspark.sql.types import *

# For JSON-based parsing (if we modify collector to export JSON)
trace_json_schema = ArrayType(StructType([
    StructField("traceId", StringType()),
    StructField("spanId", StringType()),
    StructField("parentSpanId", StringType()),
    StructField("name", StringType()),
    StructField("kind", IntegerType()),
    StructField("startTimeUnixNano", StringType()),
    StructField("endTimeUnixNano", StringType()),
    StructField("attributes", MapType(StringType(), StringType())),
    StructField("resource", StructType([
        StructField("attributes", MapType(StringType(), StringType()))
    ]))
]))

# Read from raw_traces table
raw_traces_df = spark.readStream.table(RAW_TABLE)

# Parse JSON (if using JSON export from collector)
# For protobuf, you'd use parse_otlp_protobuf UDF instead
parsed_df = (raw_traces_df
    # Note: For protobuf, replace this with parse_otlp_protobuf
    .select(
        col("kafka_key"),
        col("kafka_value").cast("string").alias("json_value"),
        col("kafka_topic"),
        col("kafka_partition"),
        col("kafka_offset"),
        col("kafka_timestamp"),
        col("ingestion_timestamp")
    )
    # TODO: Add actual parsing logic here
    # This is a placeholder - you'll need to implement based on your data format
)

print("⚠️  Parser configured (needs implementation based on data format)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification Queries

# COMMAND ----------

# Check raw traces count
display(spark.sql(f"SELECT COUNT(*) as total_traces FROM {RAW_TABLE}"))

# COMMAND ----------

# Sample raw traces
display(spark.sql(f"SELECT * FROM {RAW_TABLE} ORDER BY ingestion_timestamp DESC LIMIT 10"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stream Management Commands

# COMMAND ----------

# List all active streams
for stream in spark.streams.active:
    print(f"Stream ID: {stream.id}")
    print(f"  Name: {stream.name}")
    print(f"  Status: {stream.status}")
    print(f"  Recent Progress: {stream.lastProgress}")
    print()

# COMMAND ----------

# Stop a specific stream (replace with actual stream ID)
# stream_to_stop = spark.streams.get("stream_id_here")
# stream_to_stop.stop()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. **Verify Connectivity**: Test connection to Kafka from Databricks
# MAGIC 2. **Implement Parser**: Complete the OTLP protobuf parsing logic
# MAGIC 3. **Create Stream 2**: Parse raw traces to structured format
# MAGIC 4. **Create Stream 3**: Aggregate to metrics table
# MAGIC 5. **Set up Monitoring**: Create dashboard for stream health
