import logging
import logging.handlers
import socket
import threading


class ClientNetwork:
    """A socket network for the speech recognition system.
    This will communicate with XHaven app and receive updates to gamestate.
    It is also responsible for sending the gamestate to the app when it changes.
    """

    def __init__(self, GameState, host="localhost", port=4567) -> None:
        self.logger = logging.getLogger("xhaven_core.clientnetwork")
        self.logger.setLevel(logging.DEBUG)
        # socket_handler = logging.handlers.SocketHandler(
        #    "localhost", 19996
        # )  # Cutelog's default port is 19996
        # self.logger.addHandler(socket_handler)

        file_handler = logging.FileHandler("xhaven_speech.log")
        file_handler.setLevel(logging.DEBUG)  # Set the level of this handler
        self.logger.info("Starting network communication...")

        self.host = host
        self.port = port
        self.socket = None
        self.is_running = False
        self.lock = threading.Lock()

        # Provide a reference to the gamestate class
        self.gamestate_class = GameState

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.is_running = True
        self.logger.info("Connected to server at %s:%s", self.host, self.port)

        # Start a new thread to handle receiving data
        threading.Thread(target=self.receive_data).start()

    def receive_data(self):
        while self.is_running:
            if self.socket:
                # Receive gamestate updates from the server
                # Initialize an empty data buffer
                data = b""
                while True:
                    # Receive chunks of data from the server
                    chunk = self.socket.recv(4096)
                    self.logger.debug(
                        "Received chunk from server len: %s",
                        len(chunk),
                        extra={"chunk": chunk},
                    )
                    if not chunk:
                        # No more data to receive
                        break
                    data += chunk
                    if b"[EOM]" in chunk:
                        # All data has been received
                        break

                # Process the received data
                if data == b"S3nD:ping[EOM]":
                    #                    self.logger.debug("Received ping from server")
                    self.send_data(b"S3nD:pong[EOM]")
                elif b"GameState:" in data:
                    # When a new gamestate is recieved, update the gamestate class
                    # and log data received to log file
                    self.logger.debug(
                        "Received gamestate from server", extra={"data": data.decode()}
                    )
                    self.gamestate_class.set_gamestate(data)
                else:
                    # This should not happen, so log it to the log file as error
                    self.logger.error("Received unknown data from server: %s", data)

    def send_data(self, data):
        """Send data to the server"""
        # Basic class to send data to the server
        with self.lock:
            if self.socket:
                self.logger.debug("Sending data to server: %s", data)
                self.socket.sendall(data)

    def disconnect(self):
        """Disconnect from the server"""
        with self.lock:
            self.is_running = False
            if self.socket:
                self.logger.info("Disconnecting from server")
                self.socket.close()

    def send_init_msg(self):
        """Send the init message to the server"""
        # After connection is established, send the init message to the server
        # so that the server can send the gamestate to the client
        self.logger.info("Sending init message to server")
        self.send_data(b"S3nD:Init[EOM]")
