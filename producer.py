#!/usr/bin/env python3
import json
import time
import boto3
from kafka import KafkaProducer

def download_logs_from_s3():
    """Download logs.json from S3 bucket"""
    s3_client = boto3.client('s3')
    bucket_name = 'my12data'
    key = 'logs.json'
    
    try:
        print(f"Downloading logs.json from s3://{bucket_name}/{key}...")
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        # Handle JSONL format (one JSON object per line)
        logs_data = []
        for line in content.strip().split('\n'):
            if line.strip():
                logs_data.append(json.loads(line))
        print(f"Successfully downloaded {len(logs_data)} log entries")
        return logs_data
    except Exception as e:
        print(f"Error downloading from S3: {e}")
        return []

def main():
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=['16.52.119.70:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    
    # Download logs from S3
    logs = download_logs_from_s3()
    
    if not logs:
        print("No logs found or error downloading from S3")
        return
    
    print(f"Sending {len(logs)} log entries to Kafka topic 'ingestion-logs'...")
    
    for i, log_entry in enumerate(logs):
        try:
            # Send to Kafka
            future = producer.send('ingestion-logs', value=log_entry, key=f"log-{i}")
            future.get(timeout=10)
            print(f"Sent log {i+1}/{len(logs)}: {log_entry.get('Etat', 'N/A')} - {log_entry.get('Source', 'N/A')}")
            time.sleep(0.1)  # Small delay to simulate real-time
        except Exception as e:
            print(f"Error sending log {i}: {e}")
    
    producer.flush()
    producer.close()
    print("All logs sent successfully!")

if __name__ == "__main__":
    main()