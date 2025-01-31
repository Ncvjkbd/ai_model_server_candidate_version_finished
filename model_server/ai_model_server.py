""" This model server will manage training and inference requests for multiple models. """
import json
import asyncio
import multiprocessing
import zmq
import zmq.asyncio
from logger.logger import Logger  # Custom logger module
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class ModelServer(multiprocessing.Process):
    def __init__(self, config_file):
        """Initialize the model server process."""
        super().__init__()

        self.config_file = config_file
        self.logger = None
        self.context = None
        self.pull_socket = None
        self.push_socket = None
        self.stopping = None

    def run(self):
        """Main process function to handle requests asynchronously."""
        # Initialize logger inside the process
        self.logger = Logger("ModelServer", "logs/app_model_server.log")
        self.logger.logger.info("Model Server Started")

        config = self.load_config(self.config_file)

        self.context = zmq.asyncio.Context()

        self.stopping = asyncio.Event()

        self.pull_socket = self.context.socket(zmq.PULL)
        self.pull_socket.bind(config["receive_endpoint"])

        self.push_socket = self.context.socket(zmq.PUSH)
        self.push_socket.bind(config["response_endpoint"])

        self.logger.logger.info("ZMQ Sockets initialized.")

        try:
            asyncio.run(self.process_requests())
        except Exception as e:
            self.logger.logger.error(f"Error in model server: {e}")

    async def process_requests(self):
        """Asynchronously process incoming requests."""
        self.logger.logger.info("Request listener started...")

        while not self.stopping.is_set():
            try:
                message = await self.pull_socket.recv_json()
                self.logger.logger.info(f"Received request: {message}")

                if message == "INTERNAL_EXIT":
                    self.stopping.set()
                    break

                await asyncio.sleep(1)

                response = {
                    "request_id": message.get("request_id", "unknown"),
                    "status": "processed",
                    "result": "success"
                }

                await self.push_socket.send_json(response)
                self.logger.logger.info(f"Sent response: {response}")

            except zmq.ZMQError as e:
                self.logger.logger.error(f"ZMQ Error: {e}")
            except Exception as e:
                self.logger.logger.error(f"Unexpected error: {e}")

        self.logger.logger.info("Request listener stopped.")

    def stop(self):
        """Gracefully stop the model server."""
        if self.logger:
            self.logger.logger.info("Stopping Model Server...")

        if self.stopping:
            self.stopping.set()

        if self.pull_socket:
            self.pull_socket.close()
        if self.push_socket:
            self.push_socket.close()

        if self.context:
            self.context.term()

        if self.logger:
            self.logger.logger.info("Model Server Stopped.")

    def load_config(self, file_path):
        """Load ZMQ configuration from JSON file."""
        with open(file_path, "r") as file:
            return json.load(file)
