import asyncio
import json
import time
from datetime import datetime

import zenoh

node_name = "zenoh-simple-json"
zenoh_config = zenoh.Config()
zenoh_config.insert_json5("mode", json.dumps("client"))
zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/127.0.0.1:7447"]))
zenoh_config.insert_json5("adminspace", json.dumps({"enabled": True}))
zenoh_config.insert_json5("metadata", json.dumps({"name": node_name}))


# Foxglove log levels
LEVEL_MAP = {
    "UNKNOWN": 0,
    "DEBUG": 1,
    "INFO": 2,
    "WARNING": 3,
    "ERROR": 4,
    "FATAL": 5,
}


async def run_publisher(session):
    pub = session.declare_publisher("current_time")
    while True:
        total_ns = time.time_ns()
        # Foxglove log format
        foxglove_log = {
            "timestamp": {
                "sec": total_ns // 1_000_000_000,
                "nsec": total_ns % 1_000_000_000
            },
            "level": LEVEL_MAP["INFO"],
            "message": "Current system time log",
            "name": "run_publisher",
            "file": "publisher.py",
            "line": 32
        }
        data = json.dumps(foxglove_log)
        print(f"[Publisher] {data}")
        pub.put(
            data,
            encoding=zenoh.Encoding.APPLICATION_JSON.with_schema("foxglove.Log"),
        )
        await asyncio.sleep(1)


async def run_subscriber(session):
    def callback(sample: zenoh.Sample):
        payload = sample.payload.to_string()
        try:
            data = json.loads(payload)
            ts = data["timestamp"]
            print(f"[Subscriber] {data['message']} (ts={ts['sec']}.{ts['nsec']}) from {data['name']} @ {data['file']}:{data['line']}")
        except Exception as e:
            print(f"[Subscriber] Failed to parse JSON: {e}")

    session.declare_subscriber("current_time", callback)


async def main():
    zenoh.init_log_from_env_or("info")
    session = zenoh.open(zenoh_config)

    await asyncio.gather(
        run_publisher(session),
        run_subscriber(session),
    )


if __name__ == "__main__":
    asyncio.run(main())
