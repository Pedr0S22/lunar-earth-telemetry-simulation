import os
import time
import random
from kafka import KafkaProducer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka-kraft:9092')
TOPIC = 'telemetry-comms'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: v.encode('utf-8')
)

def generate_comms_data():
    # Simulate signal degradation logic
    if random.random() < 0.2: # 20% chance of bad signal
        snr = random.uniform(0, 10)     # Low SNR
        ber = random.uniform(0.01, 0.1) # High Error Rate
        latency = random.uniform(500, 2000) # High Latency
    else:
        snr = random.uniform(20, 50)    # Good SNR
        ber = random.uniform(0.000001, 0.001)
        latency = random.uniform(20, 100)

    #Timestamp
    timestamp = time.time_ns()

    # InfluxDB Line Protocol
    # measurement: comms
    line_protocol = f"comms snr={snr:.2f},ber={ber:.6f},latency={latency:.2f} {timestamp}"
    return line_protocol

def run():
    print(f"Starting HGA Producer connected to {KAFKA_BROKER}")
    while True:
        batch_size = random.randint(5, 15)
        print(f"Sending burst of {batch_size} messages...")
        for _ in range(batch_size):
            data = generate_comms_data()
            producer.send(TOPIC, value=data)
            time.sleep(10)
            
        producer.flush()
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    time.sleep(10)
    run()