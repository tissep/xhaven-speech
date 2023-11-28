import socket
import threading
from . import GameState

"""
A socket network for the speech recognition system.
This will communicate with XHaven app and receive updates to gamestate.
It is also responsible for sending the gamestate to the app when it changes.
"""

gamestate_class: GameState

class ClientNetwork:
    def __init__(self, GameState, host=None, port=4567):
        self.host = host  # Replace with the actual host address
        self.port = port  # Replace with the actual port number
        self.socket = None
        self.is_running = False
        
        # Provide a reference to the gamestate class
        self.gamestate_class = GameState

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.is_running = True
        print(f"Connected to server at {self.host}:{self.port}")

        # Start a new thread to handle receiving data
        threading.Thread(target=self.receive_data).start()

    def receive_data(self):
        while self.is_running:
            if self.socket:
                # Receive gamestate updates from the server
                data = self.socket.recv(10240)
                print(type(data))
                if not data:
                    break
                # Process the received data
                print(data)
                if data == b"S3nD:ping[EOM]":
                    self.send_data(b"S3nD:pong[EOM]")
                elif b"GameState:" in data:
                    # When a new gamestate is recieved, update the gamestate class
                    # and log data received to log file
                    self.gamestate_class.set_gamestate(data)
                else:
                    # This should not happen, so log it to the log file as error
                    print(f"Received unknown data from server: {data}")

    def send_data(self, data):
        # Basic class to send data to the server
        if self.socket:
            self.socket.sendall(data)
            print(f"Sent data to server: {data}")

    def disconnect(self):
        self.is_running = False
        if self.socket:
            self.socket.close()
            print("Disconnected from server")

    def send_init_msg(self):
        # After connection is established, send the init message to the server
        # so that the server can send the gamestate to the client
        self.send_data("S3nD:Init[EOM]")
        print(f"Sent init message to server")

    def update_gamestate_on_server(self):
        # When a new gamestate has been set in the Gamestate class, send it to the server
        new_gamestate = self.gamestate_class.get_gamestate()
        self.send_data(new_gamestate)

