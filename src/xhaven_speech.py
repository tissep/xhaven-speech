"""
Main function that integrates the different modules of the project."""

# Import the client network and game state modules

from tracemalloc import start
from numpy import char
from src.xhaven_core import speech
from src.xhaven_core.clientnetwork import ClientNetwork
import xhaven_core
import time
import logging
import logging.handlers
import json
import os

if __name__ == "__main__":
    logger = logging.getLogger('xhaven_core')
    logger.setLevel(logging.DEBUG)
    socket_handler = logging.handlers.SocketHandler('localhost', 19996)  # Cutelog's default port is 19996
    logger.addHandler(socket_handler)
    
    file_handler = logging.FileHandler('xhaven_speech.log')
    file_handler.setLevel(logging.DEBUG)  # Set the level of this handler


    # Read the initial parameters from the JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "initial_parameters.json"
    file_path = os.path.join(current_dir, file_name)

    # Read the JSON file
    with open(file_path, "r") as file:
        initial_parameters = json.load(file)
        
    logger.debug(f"Initial Parameters: {initial_parameters}")

    # Access the parameters
    if initial_parameters["host"] is not None:
        host = initial_parameters["host"]
    else:
        host = "localhost"
    if initial_parameters["port"] is not None:
        port = initial_parameters["port"]
    else:
        port = 4567
    
    character_names = initial_parameters["character_names"]
    monster_names = initial_parameters["monster_names"]
        
    game_state = xhaven_core.GameState(character_names, monster_names)
    client_network = xhaven_core.ClientNetwork(game_state, host=host, port=port)
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
    
    # Start speech recognition
    speech = speech.speech(game_state)
       
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
        elif key_input == "m":
            # Create a toast message with monster names
            # Example: t
            # Toast message: "The monsters are: monster-id, monster_short_name..."
            monster_list = game_state.get_monster_names()
            if monster_list is None:
                game_state.set_toast_message("There are no monsters")
            else:
                monster_list_str = ", ".join(f"{key}: {value}" for key, value in monster_list.items())
                game_state.set_toast_message(f"The monsters are: {monster_list_str}")
        elif key_input == "c":
            # Create a toast message with character names
            # Example: c
            # Toast message: "The characters are: character-id, character_name..."
            character_list = game_state.get_character_names()
            if character_list is None:
                game_state.set_toast_message("There are no characters")
            else:
                character_list_str = ", ".join(f"{key}: {value}" for key, value in character_list.items())
                game_state.set_toast_message(f"The characters are: {character_list_str}")
        elif key_input.startswith("ci"):
            # Update character initiative with the given value
            # Example: ci Hatchet 10
            # Mainly for debugging purposes
            name = key_input.split(" ")[1]
            initiative = int(key_input.split(" ")[2])
            logger.debug(f"Trying to update initiative for {name} to {initiative}")
            game_state.update_initiative(name, initiative)
        elif key_input.startswith("ch"):
            # Update character health with the given value
            # Example: ch Hatchet 8
            name = key_input.split(" ")[1]
            health = int(key_input.split(" ")[2])
            logger.debug(f"Trying to update health for {name} to {health}")
            game_state.update_character_health(name, health)
        elif key_input == "h":
            print("Help menu")
            print("Available commands:")
            print("q - Quit the program")
            print("i - Print character and monster information")
            print("m - Print monster names")
            print("c - Print character names")
            
            
    print("Done")

        
    

