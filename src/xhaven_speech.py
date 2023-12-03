"""
Main function that integrates the different modules of the project."""

# Import the client network and game state modules

from tracemalloc import start
from src.xhaven_core.clientnetwork import ClientNetwork
import xhaven_core
import time
import logging
import logging.handlers
import json
import os

HOST = "localhost"
PORT = 4567

if __name__ == "__main__":
    logger = logging.getLogger('xhaven_core')
    logger.setLevel(logging.DEBUG)
    socket_handler = logging.handlers.SocketHandler('localhost', 19996)  # Cutelog's default port is 19996
    logger.addHandler(socket_handler)
    file_handler = logging.FileHandler('characters.log')
    file_handler.setLevel(logging.DEBUG)  # Set the level of this handler


    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the file name
    file_name = "initial_parameters.json"

    # Construct the file path
    file_path = os.path.join(current_dir, file_name)

    # Read the JSON file
    with open(file_path, "r") as file:
        initial_parameters = json.load(file)
        
    logger.debug(f"Initial Parameters: {initial_parameters}")

    # Access the parameters
    if initial_parameters["host"] is not None:
        host = initial_parameters["host"]
    if initial_parameters["port"] is not None:
        port = initial_parameters["port"]

    game_state = xhaven_core.GameState(character_names=initial_parameters["character_names"])
    client_network = xhaven_core.ClientNetwork(game_state, host=HOST, port=PORT)
    game_state.set_client_network(client_network)
    
    # Initialize the client network
    client_network.connect()
    
    # Do not know if this is necessary
    time.sleep(5)
    
    # Send the init message to the server   
    client_network.send_init_msg()
    
    # Do not know if this is necessary
    time.sleep(5)
    
    # Send request for game state
    client_network.send_data(b"S3nD:Index:-1Description::GetDataDescriptionGameState:{}[EOM]")
    
    time.sleep(5)
    
    # Print the initial information from game_state
    print("Initial Information:")
    print(game_state.get_character_info())
    print(game_state.get_monster_info())
    
    while True:
        # Get key input
        key_input = input("Enter a key: ")
        
        # Process the key input
        if key_input == "q":
            print("Exiting")
            client_network.disconnect()
            break
        elif key_input == "i":
            print(game_state.get_character_info())
            print(game_state.get_monster_info())
        elif key_input.startswith("ui"):
            # Update character initiative with the given value
            # Example: ui Hatchet 10
            # Mainly for debugging purposes
            name = key_input.split(" ")[1]
            initiative = int(key_input.split(" ")[2])
            logger.debug(f"Trying to update initiative for {name} to {initiative}")
            game_state.update_initiative(name, initiative)
        elif key_input.startswith("uh"):
            # Update character health with the given value
            # Example: uh Hatchet 8
            name = key_input.split(" ")[1]
            health = int(key_input.split(" ")[2])
            logger.debug(f"Trying to update health for {name} to {health}")
            game_state.update_character_health(name, health)
        elif key_input == "h":
            print("Help menu")
            print("Available commands:")
            print("q - Quit the program")
            print("i - Print character and monster information")
            
            
    print("Done")

        
    

