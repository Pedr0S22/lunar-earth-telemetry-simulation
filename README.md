# Resilient Telemetry for Lunar Exploration Infrastructure

## Project Description
This project simulates the telemetry pipeline of a Lunar Surface Rover communicating with a Gateway Orbiter. In extraterrestrial networks, data transmission faces high Bit Error Rates (BER), intermittent connectivity, and harsh environmental variables. 

To address these challenges, this project engineers a Dockerized "Systems-of-Systems" architecture. It deploys a resilient ingestion pipeline that decouples data generation (sensors) from data persistence (database) using a message broker. This ensures that critical operational data—ranging from life-support metrics to orbital link diagnostics—is buffered, processed, and visualized in near real-time, simulating a true Cloud-to-Deep-Space continuum.

## Table of Contents
1. [Project Description](#project-description-overview)
2. [Project Structure (Pipeline & Architecture)](#project-structure-pipeline--architecture)
3. [System Components & Services](#system-components--services)
4. [Docker Compose Architecture](#docker-compose-architecture)
5. [Deployment & Setup](#deployment--setup)
6. [License](#license)
7. [Authors](#authors)

## Project Structure (Pipeline & Architecture)

The system enforces strict network isolation to simulate the air gap between operational technology (the rover) and IT infrastructure (the mission control database). It utilizes two distinct Docker networks: `deep-space-net` and `ground-control-net`, bridged securely by the ingestion agent. Below you find the details of the pipeline architecture.

![architecture](lunar_architecture.png)

## System Components & Services

### 1. Telemetry Emulators (Python Producers)
Three distinct containerized Python applications simulate burst transmission behaviors to mimic limited transmission windows. Data is serialized using the InfluxDB Line Protocol.
* **Producer A (Mobility & Power):** Publishes to `telemetry-mobility`. Simulates battery voltage decay/recharge, motor RPM, and wheel traction drops mapping regolith slippage.
* **Producer B (ECLSS):** Publishes to `telemetry-eclss`. Simulates external temperature (-170°C to +120°C), radiation levels (µSv/h), and internal cabin pressure.
* **Producer C (HGA Diagnostics):** Publishes to `telemetry-comms`. Simulates orbital link conditions including Signal-to-Noise Ratio (SNR), Bit Error Rate (BER), and Latency, mapping intermittent signal degradation.

### 2. Message Broker (Apache Kafka)
Deployed in modern **KRaft mode** (without Zookeeper dependency) utilizing the `bitnamilegacy/kafka:latest` image. It acts as a resilient buffer to guarantee message durability in fault-intolerant conditions via persistent volumes.

### 3. Ingestion Agent (Telegraf)
Acts as the sole secure bridge between the deep space and ground control networks. Subscribes to Kafka topics (`inputs.kafka_consumer`), enforces Line Protocol formatting, and securely writes batched telemetry to the database (`outputs.influxdb_v2`).

### 4. Persistence, Visualization & Alerting (InfluxDB)
Serves as the mission control archive (Organization: `esa-sic`, Bucket: `lunar-mission`). 
* **Mission Dashboard:** Includes real-time gauge indicators for cabin pressure, heatmaps correlating motor RPM with wheel traction, and threshold graphs tracking critical battery discharge.
* **Automated Flux Alerts:** Runs custom Flux scripts (`alert_eclss.flux`, `alert_hga.flux`, `alert_mobility.flux`) to automatically evaluate telemetry streams and trigger `OK`, `INFO`, `WARN`, and `CRIT` states based on mission parameters.


## Docker Compose Architecture
To ensure fault tolerance, isolation, and reliable data flow, the `docker-compose.yml` file leverages three critical Docker concepts:

### 1. Persistent Volumes
In extraterrestrial deployments, data loss is catastrophic. Docker containers are ephemeral by nature, meaning if a container crashes, its internal data is destroyed. To solve this, Persistent Volumes map a storage area on the host machine to the container's internal directory. We explicitly define named volumes for both Kafka (kafka-data) and InfluxDB (influxdb-data). This guarantees that if the broker or database containers restart, all buffered messages and historical telemetry are preserved and immediately reattached.

### 2. Ports Exposure vs. Isolation
Containers run in isolated networks. We use port mapping to punch selective holes through this isolation, using the format `HOST_PORT:CONTAINER_PORT`. We map InfluxDB's `port 8086` to the host machine ("8086:8086") so that Ground Control (web browser in the simulation) can access the UI and dashboards. However, the internal Kafka broker and Python producers are deliberately not exposed to the host, ensuring they remain isolated within the deep-space-net to simulate a secure, air-gapped operational environment.

### 3. Health Checks
Containers booting up do not mean the applications inside are instantly ready to receive data. We implement Health Checks on core services like Kafka and InfluxDB. The Python telemetry producers use the depends_on: condition: service_healthy directive. This ensures the producers will patiently wait until Kafka is fully initialized before attempting to send data, preventing "No Brokers Available" crash loops upon startup.

## Deployment & Setup

The entire architecture is containerized and orchestrated via Docker Compose, ensuring a completely self-contained deployment environment.

1. **Clone the repository.**
2. **Environment Setup:** Configure the `.env` file with the necessary credentials and InfluxDB tokens to avoid hardcoding secrets.
3. **Launch the Pipeline:**
   ```bash
   docker compose up --build -d
   ```
4. **Access the Mission Control Dashboard:** Open `http://localhost:8086` and authenticate using the credentials specified in your `.env` file. Import `dashboard.json` to view the customized Mission Control telemetry displays.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Authors

* **Pedro Silva** - pedrosilva222004@gmail.com
* **Ramyad Raadi** - uc2023205631@student.uc.pt
