# data-injection

Complete log ingestion pipeline with monitoring and alerting capabilities.

## Architecture

```
S3 (logs.json) → Producer → Kafka → Promtail → Loki → Grafana
```

## Components

- **Kafka + Zookeeper**: Message streaming platform
- **Promtail**: Log collector consuming from Kafka
- **Loki**: Log aggregation system
- **Grafana**: Visualization and monitoring dashboards
- **Producer**: Python script for S3 to Kafka ingestion

## Features

- ✅ Persistent volumes for data retention
- ✅ Real-time log processing
- ✅ Grafana dashboards for monitoring
- ✅ LogQL queries for log analysis
- ✅ Auto-restart capabilities

## Quick Start

```bash
# Start all services
docker-compose up -d

# Send logs from S3 to Kafka
python3 producer.py

# Access Grafana
http://localhost:3000 (admin/admin)

# Access Loki API
http://localhost:3100
```

## Monitoring Queries

```logql
# All logs
{job="kafka-logs"}

# Success count
sum(count_over_time({job="kafka-logs", etat="SUCCESS"}[1h]))

# Error rate
sum(count_over_time({job="kafka-logs", etat="FAILED"}[1h])) / sum(count_over_time({job="kafka-logs"}[1h])) * 100
```