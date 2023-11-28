"""
Main function that integrates the different modules of the project."""

# Import the client network and game state modules
import xhaven_speech.ClientNetwork
from .gamestate import GameState
import time

HOST = "localhost"
PORT = 4567

def main():
    game_state = GameState()
    client_network = ClientNetwork(game_state, host=HOST, port=PORT)
    game_state.set_client_network(client_network)
    
    # Initialize the client network
    client_network.connect()
    
    time.sleep(1)
    
    # Send the init message to the server   
    client_network.send_init_msg()
    while True:
        time.sleep(1)
        game_state.set_toast_message("Testing Toast")
        time.sleep(1)
        game_state.clear_toast_message()
    

if __name__ == "__main__":
    main()
    
