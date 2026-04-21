# Incremental k-Anonymity for Big Data Log Ingestion

This project implements a secure, scalable, and **Privacy by Design** pipeline for the ingestion and anonymization of system logs. It leverages a microservices architecture to balance the operational need for system observability with the strict privacy requirements imposed by the **GDPR**.

## Project Overview
Modern IT infrastructures generate massive volumes of logs containing sensitive **Quasi-Identifiers (QI)** such as IP addresses and timestamps. Standard techniques like pseudonymization often fail to prevent re-identification via **Linkage Attacks**.

This framework introduces a **Secure Ingestion Agent** that applies **Incremental k-Anonymity** to streaming data. Unlike static models, this agent processes logs "in-stream," ensuring that no personal data is persisted to disk until it meets the safety threshold of $k=5$.

## Architecture
The system is built using a containerized microservices approach (Docker):

* **Source & Logstash**: Captures raw logs and parses them into structured JSON.
* **Redis**: Acts as an asynchronous message broker to handle traffic bursts and buffer data.
* **Secure Ingestion Agent (Python)**: The core logic that performs real-time clustering and anonymization.
* **Elasticsearch**: Stores only the anonymized records.
* **Kibana**: Provides a "Privacy-Preserving Dashboard" for ethical Business Intelligence.

## Technical Architecture & Script Overview

The framework is structured as a distributed microservices pipeline where each component handles a specific stage of the Data Lifecycle.

### 1. Data Collection: `log_archiver.py`
This script acts as the **Producer** in the architecture, bridging the gap between raw unstructured logs and the secure processing layer.
* **Log Ingestion**: Scans the designated log directory for new entries.
* **Regex Parsing**: Transforms semi-structured web logs into clean, structured JSON objects.
* **Buffering**: Pushes JSON payloads into a **Redis** queue to prevent data loss during traffic spikes and decouple ingestion from processing.

### 2. Processing Engine: `redis_consumer.py` (Secure Ingestion Agent)
This is the core of the project, functioning as a **Stateful Gateway** that implements the incremental $k$-anonymity logic.
* **Asynchronous Consumption**: Uses blocking operations to retrieve logs from Redis as they arrive.
* **Incremental Clustering**: Maintains **Equivalence Classes** in RAM, assigning incoming logs to clusters based on minimum **Information Loss**.
* **Anonymization Layer**:
    * **Network Masking**: Strips specific host information, keeping only the network prefix (e.g., `/24`).
    * **Time Slotting**: Rounds timestamps to the nearest hour to neutralize timing attacks.
    * **Path Abstraction**: Removes sensitive query parameters from URLs by extracting macro-categories.
* **Secure Release**: Data is indexed in **Elasticsearch** only once a cluster reaches the safety threshold of $k=5$.

### 3. Orchestration: `docker-compose.yml`
Defines the multi-container environment, ensuring services are networked and started in the correct order.
* **Service Isolation**: Each component runs in its own isolated container.
* **Internal Service Discovery**: Uses Docker's internal DNS to allow communication via logical names (e.g., `redis:6379`).
* **Persistence**: Configures volumes for Elasticsearch to ensure data survival across restarts.

### 4. Data Visualization: Kibana Dashboard
Provides a window into the anonymized data, allowing statistical analysis without violating privacy.
* **Business Intelligence**: Visualizes the most visited resource categories and traffic trends.
* **System Observability**: Monitors HTTP status codes (200, 404, 500) to ensure infrastructure health.
* **Privacy Verification**: Visually demonstrates that data remains useful for analysis while being impossible to trace back to individuals.

## Privacy Techniques Applied
The Agent utilizes several generalization strategies to minimize **Information Loss** while maximizing privacy:

* **Network Masking**: Generalizing IP addresses into subnets.
* **Time Slotting**: Temporal aggregation to prevent event correlation.
* **Path Abstraction**: Removing query strings and identifying parameters from URLs.
* **Suppression**: Removing outliers that could compromise the anonymity of the dataset.

## Key Results
Validation performed on a real-world dataset (Kaggle Web Server Logs) demonstrated:

* **Privacy Guarantee**: Re-identification risk mathematically confined to $\le 20\%$ (with $k=5$).
* **Data Utility**: Preservation of **85%** of statistical utility, measured via Global Certainty Penalty.
* **Operational Readiness**: Full observability maintained without individual profiling.

## How to Run
Ensure you have Docker and Docker Compose installed, then run:

```bash
docker-compose up --build
