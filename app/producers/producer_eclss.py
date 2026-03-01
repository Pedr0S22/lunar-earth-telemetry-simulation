import os
import time
import random
from kafka import KafkaProducer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka-kraft:9092')
TOPIC = 'telemetry-eclss'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: v.encode('utf-8')
)

def generate_eclss_data(eclss_state):
    """
    Generates ECLSS data with state-based temperature.
    """
    delta = random.uniform(-0.5, 0.5) 
    eclss_state['temp'] += delta
    
    if eclss_state['temp'] > 120:
        eclss_state['temp'] = 120
    elif eclss_state['temp'] < -170:
        eclss_state['temp'] = -170
        
    temp = eclss_state['temp']

    # --- Radiation Levels ---
    # 80% Normal, 15% High (Flight), 5% Critical (Chernobyl)
    rand_val = random.random()
    if rand_val < 0.80:
        radiation = random.uniform(0.06, 0.3)
    elif rand_val < 0.95:
        radiation = random.uniform(2.1, 2.8)
    else:
        radiation = random.uniform(5.0, 9.4)
        
    # --- Internal Cabin Pressure ---
    pressure = random.uniform(95.0, 105.0)

    #timestamp
    timestamp = time.time_ns()

    # InfluxDB Line Protocol
    # measurement: eclss
    line_protocol = f"eclss temperature={temp:.2f},radiation={radiation:.4f},pressure={pressure:.2f} {timestamp}"
    return line_protocol

def run():
    print(f"Starting ECLSS Producer connected to {KAFKA_BROKER}")
    
    eclss_state = {
        'temp': random.uniform(-100, 0) 
    }
    
    while True:
        batch_size = random.randint(5, 15)
        print(f"Sending burst of {batch_size} messages...")
        for _ in range(batch_size):
            data = generate_eclss_data(eclss_state)
            producer.send(TOPIC, value=data)
            time.sleep(10)
            
        producer.flush()
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    time.sleep(10)
    run()