import asyncio
import json
import time
from datetime import datetime

import zenoh

node_name = "zenoh-simple-client"
zenoh_config = zenoh.Config()
zenoh_config.insert_json5("mode", json.dumps("client"))
zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/127.0.0.1:7447"]))
zenoh_config.insert_json5("adminspace", json.dumps({"enabled": True}))
zenoh_config.insert_json5("metadata", json.dumps({"name": node_name}))

async def run_publisher(session):
    pub = session.declare_publisher("client")
    while True:
        data = "ping"
        print(f"[Client] Sending {data}")
        pub.put(
            data,
            encoding=zenoh.Encoding.TEXT_PLAIN,
        )
        await asyncio.sleep(1)


async def run_subscriber(session):
    def callback(sample: zenoh.Sample):
        data = sample.payload.to_string()
        print(f"[Client] Received {data}")

    session.declare_subscriber("peer", callback)


async def main():
    zenoh.init_log_from_env_or("info")
    session = zenoh.open(zenoh_config)

    await asyncio.gather(
        run_publisher(session),
        run_subscriber(session),
    )

if __name__ == "__main__":
    asyncio.run(main())
