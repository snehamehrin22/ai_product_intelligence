"""
Test Kafka connectivity from Databricks or local machine.
Run this in a Databricks notebook to verify you can connect to Kafka.
"""

# Install kafka-python if not already installed
# %pip install kafka-python

from kafka import KafkaConsumer, KafkaProducer
import json

# Configuration
KAFKA_BROKER = "20.121.166.131:9092"
KAFKA_TOPIC = "agent-traces"

def test_connectivity():
    """Test basic connectivity to Kafka broker."""
    print(f"Testing connection to Kafka broker: {KAFKA_BROKER}")
    print(f"Topic: {KAFKA_TOPIC}")
    print("-" * 60)

    try:
        # Test 1: Create a consumer
        print("\n[Test 1] Creating Kafka consumer...")
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            consumer_timeout_ms=5000,  # 5 second timeout
            value_deserializer=lambda x: x  # Keep as bytes for now
        )
        print("✅ Consumer created successfully")

        # Test 2: Check topic partitions
        print("\n[Test 2] Checking topic partitions...")
        partitions = consumer.partitions_for_topic(KAFKA_TOPIC)
        print(f"✅ Topic '{KAFKA_TOPIC}' has {len(partitions)} partition(s): {partitions}")

        # Test 3: Try to read messages
        print("\n[Test 3] Reading messages...")
        message_count = 0
        for message in consumer:
            message_count += 1
            print(f"Message {message_count}:")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            print(f"  Timestamp: {message.timestamp}")
            print(f"  Value size: {len(message.value)} bytes")
            print(f"  First 100 bytes: {message.value[:100]}")

            if message_count >= 3:  # Read up to 3 messages
                break

        if message_count == 0:
            print("⚠️  No messages found (topic might be empty or at end of stream)")
        else:
            print(f"\n✅ Successfully read {message_count} message(s)")

        consumer.close()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Kafka is accessible!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if Kafka LoadBalancer IP is correct")
        print("2. Verify network connectivity (firewall, security groups)")
        print("3. Check if Kafka is running: kubectl get pods -l app=kafka")
        print("4. Verify LoadBalancer has external IP: kubectl get svc kafka-external")
        return False

if __name__ == "__main__":
    test_connectivity()
