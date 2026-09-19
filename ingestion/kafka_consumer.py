
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
from kafka import KafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
from datalake_utils import write_df


def run_consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        group_id="insightlab-consumer-group",
    )
    print(f"=== Consumer Kafka démarré (topic={KAFKA_TOPIC}) — en écoute... ===")
    try:
        for message in consumer:
            tick = message.value
            df = pd.DataFrame([tick])
            write_df(df, "raw_streaming", if_exists="append")
            print(f"  <- reçu et stocké : {tick['ticker']} @ {tick['close']}")
    except KeyboardInterrupt:
        print("\nArrêt du consumer.")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()