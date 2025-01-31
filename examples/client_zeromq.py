""" Example of a client using ZeroMQ for communication with a server. """
import sys
import os
import time
import json
import zmq
import zmq.asyncio
import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Get the path to the parent directory of the top-level package
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)


class ZMQClient:
    def __init__(self, config_path):
        self.context = zmq.asyncio.Context()
        abs_config_path = os.path.join(parent_dir, config_path)

        with open(abs_config_path, "r") as f:
            self.config = json.load(f)

        self.push_socket = self.context.socket(zmq.PUSH)
        self.push_socket.connect(self.config["receive_endpoint"])

        self.pull_socket = self.context.socket(zmq.PULL)
        self.pull_socket.connect(self.config["response_endpoint"])

    async def send_request(self, message):
        print("Sending request...")
        await self.push_socket.send_json(message)
        print("Waiting for response...")
        try:
            response = await asyncio.wait_for(self.pull_socket.recv_json(), timeout=10)
            print(f"Received response: {response}")
        except asyncio.TimeoutError:
            print("Timeout: No response received.")
    async def run_multiple_requests(self, num_requests=5):
        """Send multiple requests asynchronously for testing."""
        tasks = []
        for i in range(num_requests):
            request = {"request_id": str(i), "type": "inference", "data": f"data_{i}"}
            tasks.append(self.send_request(request))

        await asyncio.gather(*tasks)

    async def run(self):
        test_messages = [
            {"request_id": "1234", "type": "training", "data": "data"},
            {"request_id": "5678", "type": "inference", "data": "input"}
        ]
        for msg in test_messages:
            await self.send_request(msg)
            await asyncio.sleep(1)


if __name__ == "__main__":
    client = ZMQClient("ZMQconfig.json")
    asyncio.run(client.run_multiple_requests(num_requests=5))
