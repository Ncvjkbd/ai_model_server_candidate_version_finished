import time
import multiprocessing
import threading
import keyboard
from model_server.ai_model_server import ModelServer


class MainApp:
    """ Main example application class """

    def __init__(self):
        """Initialize the application."""
        self.ai_model_server = None

    def start_model_server(self):
        """Start the AI model server."""
        print("Starting model server...")
        self.ai_model_server = ModelServer("ZMQconfig.json")
        self.ai_model_server.start()
        print("Model server started")

    def stop_model_server(self):
        """Stop the AI model server gracefully."""
        print("Stopping model server...")
        if self.ai_model_server:
            self.ai_model_server.stop()
            self.ai_model_server.join()
        print("Model server stopped")

    def listen_for_exit(self):
        """Listen for the ESC key to exit the server."""
        print("Press ESC to shut down the server...")
        keyboard.wait("esc")
        self.running = False


if __name__ == "__main__":
    app = MainApp()

    try:
        app.start_model_server()
        exit_thread = threading.Thread(target=app.listen_for_exit(),daemon=True)
        exit_thread.start()

        while app.running:
            time.sleep(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        app.stop_model_server()
