import os
import time
import random
import json
from kafka import KafkaProducer

# Configuration
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka-kraft:9092')
TOPIC = 'telemetry-mobility'

# Initialize Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: v.encode('utf-8')
)

def generate_mobility_data(voltage_state):
    """
    Generates mobility data.
    Voltage cycles: decays, then recharges.
    Traction: normally high, occasionally drops (slippage).
    """
    # Voltage Logic
    if voltage_state['charging']:
        voltage_state['value'] += random.uniform(0.1, 0.5)
        if voltage_state['value'] >= 100.0:
            voltage_state['value'] = 100.0
            voltage_state['charging'] = False
    else:
        voltage_state['value'] -= random.uniform(0.05, 0.2)
        if voltage_state['value'] <= 10.0:  # Critical low
            voltage_state['charging'] = True
            
    # Traction Logic
    if random.random() < 0.1:
        traction = random.uniform(0.0, 0.4)
    else:
        traction = random.uniform(0.8, 1.0)
        
    rpm = random.randint(100, 5000)

    #Timestamp
    timestamp = time.time_ns()
  
    # InfluxDB Line Protocol
    line_protocol = f"mobility voltage={voltage_state['value']:.2f},rpm={rpm}i,traction={traction:.2f} {timestamp}"
    return line_protocol

def run():
    print(f"Starting Mobility Producer connected to {KAFKA_BROKER}")
    voltage_state = {'value': 100.0, 'charging': False}
    
    while True:
        # Burst transmission to simulate link availability
        batch_size = random.randint(5, 15)
        print(f"Sending burst of {batch_size} messages...")
        for _ in range(batch_size):
            data = generate_mobility_data(voltage_state)
            producer.send(TOPIC, value=data)
            time.sleep(10)
            
        producer.flush()
        
        # Sleep to simulate orbital link unavailability
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    time.sleep(10)
    run()
