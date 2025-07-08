"""
This script demonstrates core Zenoh features for node development.

It uses a simple node configuration and runs four async tasks:

- run_queryable: Registers a query handler under the 'sum' topic.
- run_query_loop: Periodically queries the 'sum' topic.
- run_publisher: Periodically publishes current time to 'current_time'.
- run_subscriber: Registers a handler for messages on 'current_time'.

This minimal example illustrates publisher/subscriber and queryable usage.
Tasks can run on separate nodes for inter-service communication.
"""

import asyncio
import json
from datetime import datetime

import zenoh

node_name = "zenoh-simple-service"
zenoh_config = zenoh.Config()
zenoh_config.insert_json5("mode", json.dumps("client"))
zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/127.0.0.1:7447"]))
zenoh_config.insert_json5("adminspace", json.dumps({"enabled": True}))
zenoh_config.insert_json5("metadata", json.dumps({"name": node_name}))


async def run_queryable(session):
    def handle_query(query: zenoh.Query):
        params = query.selector.parameters
        try:
            a = int(params.get("a", "0"))
            b = int(params.get("b", "0"))
            query.reply(query.selector.key_expr, str(a + b))
        except Exception as e:
            query.reply(query.selector.key_expr, f"error: {e}")

    session.declare_queryable("sum", handle_query)

async def run_query_loop(session):
    i = 0
    while True:
        selector = zenoh.Selector(f"sum?a={i};b=1")
        replies = session.get(selector)
        for reply in replies:
            try:
                print(f"[QueryLoop] sum({i}, 1) = {reply.ok.payload.to_string()}")
            except:
                print("[QueryLoop] error:", reply.err.payload.to_string())
        i += 1
        await asyncio.sleep(2)

async def run_publisher(session):
    pub = session.declare_publisher("current_time")
    while True:
        now = datetime.now().isoformat()
        print(f"[Publisher] {now}")
        pub.put(now)
        await asyncio.sleep(1)


async def run_subscriber(session):
    def callback(sample: zenoh.Sample):
        print(f"[Subscriber] {sample.payload.to_string()}")

    session.declare_subscriber("current_time", callback)


async def main():
    zenoh.init_log_from_env_or("info")
    session = zenoh.open(zenoh_config)

    await asyncio.gather(
        run_queryable(session),
        run_query_loop(session),
        run_publisher(session),
        run_subscriber(session),
    )


if __name__ == "__main__":
    asyncio.run(main())